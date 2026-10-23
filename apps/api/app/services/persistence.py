from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import (
    Conversation,
    IntelligenceArtifact,
    MediaAsset,
    Speaker,
    Transcript,
    Turn,
)
from app.schemas import (
    ConversationSummary,
    ConversationTurn,
    IntelligenceDraft,
    IntelligenceResponse,
    TranscriptionResponse,
    TranscriptWord,
)
from app.services.media import StoredMedia


async def create_conversation(
    session: AsyncSession,
    title: str,
) -> Conversation:
    conversation = Conversation(title=title, status="uploading")
    session.add(conversation)
    try:
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    return conversation


async def save_media_asset(
    session: AsyncSession,
    conversation_id: UUID,
    filename: str,
    content_type: str,
    size_bytes: int,
    stored: StoredMedia,
) -> MediaAsset:
    asset = MediaAsset(
        conversation_id=conversation_id,
        original_filename=filename,
        content_type=content_type,
        size_bytes=size_bytes,
        checksum_sha256=stored.checksum_sha256,
        storage_path=stored.storage_path,
    )
    session.add(asset)
    try:
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    return asset


async def set_conversation_status(
    session: AsyncSession,
    conversation_id: UUID,
    status: str,
) -> None:
    conversation = await session.get(Conversation, conversation_id)
    if conversation is None:
        return
    conversation.status = status
    await session.commit()


async def save_transcription(
    session: AsyncSession,
    transcription: TranscriptionResponse,
    conversation_id: UUID,
    model_id: str,
) -> TranscriptionResponse:
    conversation = await session.get(Conversation, conversation_id)
    if conversation is None:
        raise ValueError("Conversation not found.")

    transcript = Transcript(
        conversation=conversation,
        language_code=transcription.language_code,
        language_probability=transcription.language_probability,
        full_text=transcription.text,
        model_id=model_id,
    )
    speakers: dict[str, Speaker] = {}
    for position, provider_id in enumerate(transcription.speakers):
        speaker = Speaker(
            transcript=transcript,
            provider_speaker_id=provider_id,
            position=position,
        )
        speakers[provider_id] = speaker

    for turn in transcription.turns:
        Turn(
            transcript=transcript,
            speaker=speakers[turn.speaker_id],
            sequence=turn.sequence,
            start=turn.start,
            end=turn.end,
            text=turn.text,
            words=[word.model_dump() for word in turn.words],
        )

    conversation.status = "draft_ready"
    session.add(transcript)

    try:
        await session.commit()
    except Exception:
        await session.rollback()
        raise

    stored = await get_transcription(session, str(transcript.id))
    if stored is None:
        raise RuntimeError("Stored transcription could not be loaded.")
    return stored


async def get_transcription(
    session: AsyncSession,
    transcription_id: str,
) -> TranscriptionResponse | None:
    try:
        parsed_id = UUID(transcription_id)
    except ValueError:
        return None

    result = await session.execute(
        select(Transcript)
        .where(Transcript.id == parsed_id)
        .options(
            selectinload(Transcript.speakers),
            selectinload(Transcript.turns).selectinload(Turn.speaker),
            selectinload(Transcript.conversation).selectinload(
                Conversation.media_assets
            ),
        )
    )
    transcript = result.scalar_one_or_none()
    if transcript is None:
        return None

    names = {
        speaker.provider_speaker_id: speaker.display_name
        for speaker in transcript.speakers
        if speaker.display_name
    }
    turns = [
        ConversationTurn(
            sequence=turn.sequence,
            speaker_id=turn.speaker.provider_speaker_id,
            speaker_name=turn.speaker.display_name,
            start=turn.start,
            end=turn.end,
            text=turn.text,
            words=[TranscriptWord.model_validate(word) for word in turn.words],
        )
        for turn in transcript.turns
    ]
    media = transcript.conversation.media_assets[0] if transcript.conversation.media_assets else None

    return TranscriptionResponse(
        id=transcript.id,
        conversation_id=transcript.conversation_id,
        media_id=media.id if media else None,
        audio_filename=media.original_filename if media else None,
        language_code=transcript.language_code,
        language_probability=transcript.language_probability,
        text=transcript.full_text,
        speakers=[speaker.provider_speaker_id for speaker in transcript.speakers],
        speaker_names=names,
        turns=turns,
    )


async def get_latest_conversation_transcription(
    session: AsyncSession,
    conversation_id: UUID,
) -> TranscriptionResponse | None:
    result = await session.execute(
        select(Transcript.id)
        .where(Transcript.conversation_id == conversation_id)
        .order_by(Transcript.version.desc())
        .limit(1)
    )
    transcript_id = result.scalar_one_or_none()
    if transcript_id is None:
        return None
    return await get_transcription(session, str(transcript_id))


async def save_intelligence(
    session: AsyncSession,
    conversation_id: UUID,
    draft: IntelligenceDraft,
    model_id: str,
    prompt_version: str,
) -> IntelligenceResponse:
    existing = await get_latest_intelligence(session, conversation_id)
    if existing is not None:
        return existing

    conversation = await session.get(Conversation, conversation_id)
    if conversation is None:
        raise ValueError("Conversation not found.")

    artifact = IntelligenceArtifact(
        conversation=conversation,
        kind="summary",
        version=1,
        status="citation_validated",
        content=draft.model_dump(),
        model_id=model_id,
        prompt_version=prompt_version,
    )
    session.add(artifact)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        existing = await get_latest_intelligence(session, conversation_id)
        if existing is None:
            raise
        return existing
    except Exception:
        await session.rollback()
        raise
    await session.refresh(artifact)
    return _intelligence_response(artifact)


async def get_latest_intelligence(
    session: AsyncSession,
    conversation_id: UUID,
) -> IntelligenceResponse | None:
    result = await session.execute(
        select(IntelligenceArtifact)
        .where(
            IntelligenceArtifact.conversation_id == conversation_id,
            IntelligenceArtifact.kind == "summary",
        )
        .order_by(IntelligenceArtifact.version.desc())
        .limit(1)
    )
    artifact = result.scalar_one_or_none()
    return _intelligence_response(artifact) if artifact else None


def _intelligence_response(artifact: IntelligenceArtifact) -> IntelligenceResponse:
    return IntelligenceResponse.model_validate(
        {
            **artifact.content,
            "id": artifact.id,
            "conversation_id": artifact.conversation_id,
            "version": artifact.version,
            "status": artifact.status,
            "model_id": artifact.model_id,
            "prompt_version": artifact.prompt_version,
            "created_at": artifact.created_at.isoformat(),
        }
    )


async def list_conversations(
    session: AsyncSession,
    limit: int = 50,
) -> list[ConversationSummary]:
    result = await session.execute(
        select(Conversation)
        .options(
            selectinload(Conversation.media_assets),
            selectinload(Conversation.transcripts),
        )
        .order_by(Conversation.created_at.desc())
        .limit(limit)
    )
    conversations = result.scalars().all()
    summaries: list[ConversationSummary] = []
    for conversation in conversations:
        media = conversation.media_assets[0] if conversation.media_assets else None
        transcript = conversation.transcripts[-1] if conversation.transcripts else None
        summaries.append(
            ConversationSummary(
                id=conversation.id,
                title=conversation.title,
                status=conversation.status,
                created_at=conversation.created_at.isoformat(),
                media_id=media.id if media else None,
                audio_filename=media.original_filename if media else None,
                transcript_id=transcript.id if transcript else None,
            )
        )
    return summaries


async def get_media_asset(
    session: AsyncSession,
    media_id: str,
) -> MediaAsset | None:
    try:
        parsed_id = UUID(media_id)
    except ValueError:
        return None
    return await session.get(MediaAsset, parsed_id)


async def rename_speaker(
    session: AsyncSession,
    transcription_id: str,
    provider_speaker_id: str,
    display_name: str,
) -> TranscriptionResponse | None:
    try:
        parsed_id = UUID(transcription_id)
    except ValueError:
        return None

    result = await session.execute(
        select(Speaker).where(
            Speaker.transcript_id == parsed_id,
            Speaker.provider_speaker_id == provider_speaker_id,
        )
    )
    speaker = result.scalar_one_or_none()
    if speaker is None:
        return None

    speaker.display_name = display_name
    await session.commit()
    return await get_transcription(session, transcription_id)
