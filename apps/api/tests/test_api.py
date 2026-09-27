from fastapi.testclient import TestClient

from app.config import Settings, get_settings
from app.database import get_session
from app.main import app


client = TestClient(app)


def _settings_without_elevenlabs() -> Settings:
    return Settings(elevenlabs_api_key="")


async def _unused_session():
    yield None


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_transcription_requires_configuration() -> None:
    app.dependency_overrides[get_settings] = _settings_without_elevenlabs
    app.dependency_overrides[get_session] = _unused_session
    try:
        response = client.post(
            "/api/v1/transcriptions",
            files={"audio": ("conversation.wav", b"audio", "audio/wav")},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json() == {"detail": "ElevenLabs is not configured."}
