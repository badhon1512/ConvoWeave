from app.services.transcript import build_transcript


def test_builds_sequential_speaker_turns() -> None:
    payload = {
        "language_code": "en",
        "language_probability": 0.99,
        "text": "Hello, Sam. Hi Doctor.",
        "words": [
            _word("Hello", 0.0, 0.4, "speaker_0"),
            _word(",", 0.4, 0.45, "speaker_0"),
            _word("Sam", 0.5, 0.8, "speaker_0"),
            _word(".", 0.8, 0.85, "speaker_0"),
            _word("Hi", 1.0, 1.2, "speaker_1"),
            _word("Doctor", 1.3, 1.7, "speaker_1"),
            _word(".", 1.7, 1.75, "speaker_1"),
        ],
    }

    result = build_transcript(payload)

    assert result.speakers == ["speaker_0", "speaker_1"]
    assert len(result.turns) == 2
    assert result.turns[0].sequence == 1
    assert result.turns[0].speaker_id == "speaker_0"
    assert result.turns[0].text == "Hello, Sam."
    assert result.turns[1].sequence == 2
    assert result.turns[1].speaker_id == "speaker_1"
    assert result.turns[1].text == "Hi Doctor."


def test_splits_same_speaker_after_long_pause() -> None:
    payload = {
        "text": "First thought. Second thought.",
        "words": [
            _word("First", 0.0, 0.4, "speaker_0"),
            _word("thought", 0.5, 0.9, "speaker_0"),
            _word("Second", 4.0, 4.4, "speaker_0"),
            _word("thought", 4.5, 4.9, "speaker_0"),
        ],
    }

    result = build_transcript(payload)

    assert len(result.turns) == 2
    assert result.turns[0].text == "First thought"
    assert result.turns[1].text == "Second thought"


def test_ignores_spacing_and_incomplete_tokens() -> None:
    payload = {
        "text": "Hello world",
        "words": [
            _word("Hello", 0.0, 0.4, "speaker_0"),
            {"text": " ", "type": "spacing"},
            {"text": "missing timing", "speaker_id": "speaker_0"},
            _word("world", 0.5, 0.9, "speaker_0"),
        ],
    }

    result = build_transcript(payload)

    assert len(result.turns) == 1
    assert result.turns[0].text == "Hello world"


def _word(
    text: str,
    start: float,
    end: float,
    speaker_id: str,
) -> dict:
    return {
        "text": text,
        "start": start,
        "end": end,
        "speaker_id": speaker_id,
        "type": "word",
    }

