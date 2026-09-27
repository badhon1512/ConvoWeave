import hashlib
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO
from uuid import UUID, uuid4

@dataclass(frozen=True)
class StoredMedia:
    storage_path: str
    checksum_sha256: str


class MediaStore:
    def __init__(
        self,
        root: str,
    ) -> None:
        self.root = Path(root).resolve()

    def store(
        self,
        audio: BinaryIO,
        conversation_id: UUID,
        filename: str,
        content_type: str,
    ) -> StoredMedia:
        checksum = _sha256(audio)
        directory = self.root / "conversations" / str(conversation_id)
        directory.mkdir(parents=True, exist_ok=True)
        destination = directory / f"{uuid4()}-{_safe_filename(filename)}"
        audio.seek(0)
        with destination.open("wb") as target:
            shutil.copyfileobj(audio, target)
        audio.seek(0)
        return StoredMedia(
            storage_path=str(destination),
            checksum_sha256=checksum,
        )


def _sha256(file: BinaryIO) -> str:
    digest = hashlib.sha256()
    file.seek(0)
    while chunk := file.read(1024 * 1024):
        digest.update(chunk)
    file.seek(0)
    return digest.hexdigest()


def _safe_filename(filename: str) -> str:
    name = Path(filename).name
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-.")
    return cleaned[:180] or "conversation-audio"
