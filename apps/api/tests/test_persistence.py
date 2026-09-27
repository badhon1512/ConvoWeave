import asyncio

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models import Base
from app.services.media import StoredMedia
from app.services.persistence import (
    create_conversation,
    get_transcription,
    list_conversations,
    rename_speaker,
    save_media_asset,
    save_transcription,
)
from app.services.transcript import build_transcript


def test_saves_loads_and_renames_speakers() -> None:
    asyncio.run(_persistence_scenario())


async def _persistence_scenario() -> None:
    engine = create_async_engine("sqlite+aiosqlite://")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        conversation = await create_conversation(session, "meeting.wav")
        media = await save_media_asset(
            session,
            conversation.id,
            filename="meeting.wav",
            content_type="audio/wav",
            size_bytes=1234,
            stored=StoredMedia(
                storage_path=f"/test-media/conversations/{conversation.id}/meeting.wav",
                checksum_sha256="a" * 64,
            ),
        )
        transcript = build_transcript(
            {
                "language_code": "en",
                "text": "Hello there",
                "words": [
                    {
                        "text": "Hello",
                        "start": 0.0,
                        "end": 0.4,
                        "speaker_id": "speaker_0",
                        "type": "word",
                    },
                    {
                        "text": "there",
                        "start": 0.5,
                        "end": 0.9,
                        "speaker_id": "speaker_0",
                        "type": "word",
                    },
                ],
            }
        )
        stored = await save_transcription(
            session,
            transcript,
            conversation_id=conversation.id,
            model_id="scribe_v2",
        )

        assert stored.id is not None
        assert stored.conversation_id is not None
        assert stored.media_id == media.id
        assert stored.audio_filename == "meeting.wav"
        assert stored.turns[0].text == "Hello there"

        loaded = await get_transcription(session, str(stored.id))
        assert loaded is not None
        assert loaded.speakers == ["speaker_0"]

        renamed = await rename_speaker(
            session,
            str(stored.id),
            "speaker_0",
            "Dr. Rivera",
        )
        assert renamed is not None
        assert renamed.speaker_names == {"speaker_0": "Dr. Rivera"}
        assert renamed.turns[0].speaker_name == "Dr. Rivera"

        conversations = await list_conversations(session)
        assert len(conversations) == 1
        assert conversations[0].transcript_id == stored.id
        assert conversations[0].media_id == media.id

    await engine.dispose()
