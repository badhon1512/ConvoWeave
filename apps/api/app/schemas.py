from uuid import UUID

from pydantic import BaseModel, Field


class TranscriptWord(BaseModel):
    text: str
    start: float
    end: float
    speaker_id: str
    type: str = "word"


class ConversationTurn(BaseModel):
    sequence: int = Field(ge=1)
    speaker_id: str
    speaker_name: str | None = None
    start: float
    end: float
    text: str
    words: list[TranscriptWord]


class TranscriptionResponse(BaseModel):
    id: UUID | None = None
    conversation_id: UUID | None = None
    media_id: UUID | None = None
    audio_filename: str | None = None
    language_code: str | None = None
    language_probability: float | None = None
    text: str
    speakers: list[str]
    speaker_names: dict[str, str] = Field(default_factory=dict)
    turns: list[ConversationTurn]


class SpeakerUpdate(BaseModel):
    display_name: str = Field(min_length=1, max_length=80)


class ConversationSummary(BaseModel):
    id: UUID
    title: str
    status: str
    created_at: str
    media_id: UUID | None = None
    audio_filename: str | None = None
    transcript_id: UUID | None = None


class HealthResponse(BaseModel):
    status: str
