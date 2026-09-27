from pathlib import Path
from typing import Annotated

from anyio import to_thread
from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.config import Settings, get_settings
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.schemas import (
    ConversationSummary,
    HealthResponse,
    SpeakerUpdate,
    TranscriptionResponse,
)
from app.services.media import MediaStore
from app.services.persistence import (
    create_conversation,
    get_media_asset,
    get_transcription,
    list_conversations,
    rename_speaker,
    save_media_asset,
    save_transcription,
    set_conversation_status,
)
from app.services.elevenlabs import ElevenLabsError, ElevenLabsTranscriber
from app.services.transcript import build_transcript


app = FastAPI(title="ConvoWeave API", version="0.1.0")
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post(
    "/api/v1/transcriptions",
    response_model=TranscriptionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_transcription(
    audio: Annotated[UploadFile, File(description="Audio conversation")],
    language_code: Annotated[str | None, Query(min_length=2, max_length=3)] = None,
    num_speakers: Annotated[int | None, Query(ge=1, le=32)] = None,
    settings: Settings = Depends(get_settings),
    session: AsyncSession = Depends(get_session),
) -> TranscriptionResponse:
    if not settings.elevenlabs_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ElevenLabs is not configured.",
        )

    if not audio.content_type or not audio.content_type.startswith("audio/"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="An audio file is required.",
        )

    size = await _upload_size(audio)
    if size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio file is empty.",
        )
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if size > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Audio must be no larger than {settings.max_upload_mb} MB.",
        )

    filename = audio.filename or "conversation"
    conversation = await create_conversation(session, filename)
    media_store = MediaStore(
        root=settings.media_root,
    )
    transcriber = ElevenLabsTranscriber(
        api_key=settings.elevenlabs_api_key,
        model_id=settings.elevenlabs_model_id,
        base_url=settings.elevenlabs_base_url,
        timeout_seconds=settings.request_timeout_seconds,
    )

    try:
        try:
            stored_media = await to_thread.run_sync(
                lambda: media_store.store(
                    audio=audio.file,
                    conversation_id=conversation.id,
                    filename=filename,
                    content_type=audio.content_type,
                )
            )
            await save_media_asset(
                session=session,
                conversation_id=conversation.id,
                filename=filename,
                content_type=audio.content_type,
                size_bytes=size,
                stored=stored_media,
            )
        except Exception as exc:
            await set_conversation_status(session, conversation.id, "media_failed")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Could not store audio.",
            ) from exc

        await set_conversation_status(session, conversation.id, "processing")

        payload = await to_thread.run_sync(
            lambda: transcriber.transcribe(
                audio=audio.file,
                filename=filename,
                content_type=audio.content_type,
                language_code=language_code,
                num_speakers=num_speakers,
            )
        )
    except ElevenLabsError as exc:
        await set_conversation_status(session, conversation.id, "transcription_failed")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
    finally:
        await audio.close()

    try:
        transcript = build_transcript(payload)
        return await save_transcription(
            session=session,
            transcription=transcript,
            conversation_id=conversation.id,
            model_id=settings.elevenlabs_model_id,
        )
    except Exception:
        await set_conversation_status(session, conversation.id, "processing_failed")
        raise


@app.get(
    "/api/v1/conversations",
    response_model=list[ConversationSummary],
)
async def read_conversations(
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    session: AsyncSession = Depends(get_session),
) -> list[ConversationSummary]:
    return await list_conversations(session, limit)


@app.get("/api/v1/media/{media_id}", response_class=FileResponse)
async def read_media(
    media_id: str,
    session: AsyncSession = Depends(get_session),
) -> FileResponse:
    media = await get_media_asset(session, media_id)
    if media is None or not Path(media.storage_path).is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found.",
        )
    return FileResponse(
        path=media.storage_path,
        media_type=media.content_type,
        filename=media.original_filename,
        content_disposition_type="inline",
    )


@app.get(
    "/api/v1/transcriptions/{transcription_id}",
    response_model=TranscriptionResponse,
)
async def read_transcription(
    transcription_id: str,
    session: AsyncSession = Depends(get_session),
) -> TranscriptionResponse:
    transcription = await get_transcription(session, transcription_id)
    if transcription is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcription not found.",
        )
    return transcription


@app.patch(
    "/api/v1/transcriptions/{transcription_id}/speakers/{speaker_id}",
    response_model=TranscriptionResponse,
)
async def update_speaker(
    transcription_id: str,
    speaker_id: str,
    update: SpeakerUpdate,
    session: AsyncSession = Depends(get_session),
) -> TranscriptionResponse:
    transcription = await rename_speaker(
        session,
        transcription_id,
        speaker_id,
        update.display_name.strip(),
    )
    if transcription is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcription or speaker not found.",
        )
    return transcription


async def _upload_size(audio: UploadFile) -> int:
    await audio.seek(0)
    audio.file.seek(0, 2)
    size = audio.file.tell()
    await audio.seek(0)
    return size
