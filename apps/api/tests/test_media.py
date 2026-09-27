from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

from app.services.media import MediaStore


def test_stores_audio_with_checksum_and_safe_name() -> None:
    with TemporaryDirectory() as directory:
        store = MediaStore(directory)
        stored = store.store(
            audio=BytesIO(b"audio-content"),
            conversation_id=uuid4(),
            filename="../../Meeting notes.wav",
            content_type="audio/wav",
        )

        path = Path(stored.storage_path)
        assert path.is_file()
        assert path.name.endswith("Meeting-notes.wav")
        assert path.read_bytes() == b"audio-content"
        assert len(stored.checksum_sha256) == 64

