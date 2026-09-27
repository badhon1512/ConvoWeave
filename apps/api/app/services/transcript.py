from dataclasses import dataclass, field
from typing import Any

from app.schemas import ConversationTurn, TranscriptWord, TranscriptionResponse


@dataclass
class _TurnBuilder:
    speaker_id: str
    start: float
    end: float
    parts: list[str] = field(default_factory=list)
    words: list[TranscriptWord] = field(default_factory=list)

    def add(self, word: TranscriptWord) -> None:
        self.end = max(self.end, word.end)
        self.words.append(word)
        self.parts.append(word.text)

    def text(self) -> str:
        return _join_tokens(self.parts)


def build_transcript(
    payload: dict[str, Any],
    pause_threshold_seconds: float = 2.0,
) -> TranscriptionResponse:
    words = _parse_words(payload.get("words", []))
    turns = _build_turns(words, pause_threshold_seconds)
    speakers = list(dict.fromkeys(turn.speaker_id for turn in turns))

    return TranscriptionResponse(
        language_code=payload.get("language_code"),
        language_probability=payload.get("language_probability"),
        text=payload.get("text", ""),
        speakers=speakers,
        turns=turns,
    )


def _parse_words(items: list[dict[str, Any]]) -> list[TranscriptWord]:
    words: list[TranscriptWord] = []
    current_speaker = "speaker_unknown"

    for item in items:
        token_type = item.get("type", "word")
        if token_type == "spacing":
            continue

        text = str(item.get("text", "")).strip()
        start = item.get("start")
        end = item.get("end")
        if not text or start is None or end is None:
            continue

        speaker_id = item.get("speaker_id") or current_speaker
        current_speaker = speaker_id
        words.append(
            TranscriptWord(
                text=text,
                start=float(start),
                end=float(end),
                speaker_id=speaker_id,
                type=token_type,
            )
        )

    return words


def _build_turns(
    words: list[TranscriptWord],
    pause_threshold_seconds: float,
) -> list[ConversationTurn]:
    if not words:
        return []

    turns: list[ConversationTurn] = []
    builder = _TurnBuilder(
        speaker_id=words[0].speaker_id,
        start=words[0].start,
        end=words[0].end,
    )
    builder.add(words[0])

    for word in words[1:]:
        speaker_changed = word.speaker_id != builder.speaker_id
        long_pause = word.start - builder.end > pause_threshold_seconds

        if speaker_changed or long_pause:
            turns.append(_finish_turn(builder, len(turns) + 1))
            builder = _TurnBuilder(
                speaker_id=word.speaker_id,
                start=word.start,
                end=word.end,
            )

        builder.add(word)

    turns.append(_finish_turn(builder, len(turns) + 1))
    return turns


def _finish_turn(builder: _TurnBuilder, sequence: int) -> ConversationTurn:
    return ConversationTurn(
        sequence=sequence,
        speaker_id=builder.speaker_id,
        start=builder.start,
        end=builder.end,
        text=builder.text(),
        words=builder.words,
    )


def _join_tokens(tokens: list[str]) -> str:
    text = ""
    closing_punctuation = {".", ",", "!", "?", ":", ";", "%", ")", "]", "}"}
    opening_punctuation = {"(", "[", "{"}

    for token in tokens:
        if not text:
            text = token
        elif token in closing_punctuation or token.startswith(("'", "’")):
            text += token
        elif text[-1] in opening_punctuation:
            text += token
        else:
            text += f" {token}"

    return text.strip()

