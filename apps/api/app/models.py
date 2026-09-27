from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(40), default="draft_ready")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    transcripts: Mapped[list["Transcript"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Transcript.version",
    )
    media_assets: Mapped[list["MediaAsset"]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan"
    )


class MediaAsset(Base):
    __tablename__ = "media_assets"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    conversation_id: Mapped[UUID] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"), index=True
    )
    original_filename: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(120))
    size_bytes: Mapped[int] = mapped_column(Integer)
    checksum_sha256: Mapped[str] = mapped_column(String(64))
    storage_path: Mapped[str] = mapped_column(String(500), unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    conversation: Mapped[Conversation] = relationship(back_populates="media_assets")


class Transcript(Base):
    __tablename__ = "transcripts"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    conversation_id: Mapped[UUID] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"), index=True
    )
    version: Mapped[int] = mapped_column(Integer, default=1)
    language_code: Mapped[str | None] = mapped_column(String(10))
    language_probability: Mapped[float | None] = mapped_column(Float)
    full_text: Mapped[str] = mapped_column(Text)
    provider: Mapped[str] = mapped_column(String(50), default="elevenlabs")
    model_id: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    conversation: Mapped[Conversation] = relationship(back_populates="transcripts")
    speakers: Mapped[list["Speaker"]] = relationship(
        back_populates="transcript",
        cascade="all, delete-orphan",
        order_by="Speaker.position",
    )
    turns: Mapped[list["Turn"]] = relationship(
        back_populates="transcript",
        cascade="all, delete-orphan",
        order_by="Turn.sequence",
    )


class Speaker(Base):
    __tablename__ = "speakers"
    __table_args__ = (
        UniqueConstraint(
            "transcript_id", "provider_speaker_id", name="uq_transcript_speaker"
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    transcript_id: Mapped[UUID] = mapped_column(
        ForeignKey("transcripts.id", ondelete="CASCADE"), index=True
    )
    provider_speaker_id: Mapped[str] = mapped_column(String(100))
    display_name: Mapped[str | None] = mapped_column(String(80))
    position: Mapped[int] = mapped_column(Integer)

    transcript: Mapped[Transcript] = relationship(back_populates="speakers")


class Turn(Base):
    __tablename__ = "turns"
    __table_args__ = (
        UniqueConstraint("transcript_id", "sequence", name="uq_transcript_turn"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    transcript_id: Mapped[UUID] = mapped_column(
        ForeignKey("transcripts.id", ondelete="CASCADE"), index=True
    )
    speaker_id: Mapped[UUID] = mapped_column(ForeignKey("speakers.id"))
    sequence: Mapped[int] = mapped_column(Integer)
    start: Mapped[float] = mapped_column(Float)
    end: Mapped[float] = mapped_column(Float)
    text: Mapped[str] = mapped_column(Text)
    words: Mapped[list[dict]] = mapped_column(JSON)

    transcript: Mapped[Transcript] = relationship(back_populates="turns")
    speaker: Mapped[Speaker] = relationship()
