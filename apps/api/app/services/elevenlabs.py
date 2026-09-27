from typing import BinaryIO

import httpx


class ElevenLabsError(Exception):
    pass


class ElevenLabsTranscriber:
    def __init__(
        self,
        api_key: str,
        model_id: str,
        base_url: str,
        timeout_seconds: float,
    ) -> None:
        self.api_key = api_key
        self.model_id = model_id
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def transcribe(
        self,
        audio: BinaryIO,
        filename: str,
        content_type: str,
        language_code: str | None = None,
        num_speakers: int | None = None,
    ) -> dict:
        data = {
            "model_id": self.model_id,
            "diarize": "true",
            "tag_audio_events": "true",
        }
        if language_code:
            data["language_code"] = language_code
        if num_speakers is not None:
            data["num_speakers"] = str(num_speakers)

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(
                    f"{self.base_url}/v1/speech-to-text",
                    headers={"xi-api-key": self.api_key},
                    data=data,
                    files={"file": (filename, audio, content_type)},
                )
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            raise ElevenLabsError(
                f"ElevenLabs transcription failed with status {status}."
            ) from exc
        except httpx.HTTPError as exc:
            raise ElevenLabsError("Could not reach ElevenLabs.") from exc

        return response.json()

