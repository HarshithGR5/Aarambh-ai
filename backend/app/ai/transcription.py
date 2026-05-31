"""
Whisper STT transcription service.
Falls back to mock response if OpenAI key is not configured.
"""
import tempfile
import os
from typing import Optional
from .client import get_client
import logging

logger = logging.getLogger(__name__)


async def transcribe_audio(
    audio_bytes: bytes,
    filename: str,
    language_hint: Optional[str] = None,
) -> dict:
    """
    Transcribe audio using OpenAI Whisper API.
    Returns: { transcript, detected_language, duration_seconds }
    """
    client = get_client()

    if client is None:
        logger.info("Mock transcription response (OpenAI not configured)")
        return {
            "transcript": "Child is playing well with others today. Shows good social interaction.",
            "detected_language": language_hint or "en",
            "duration_seconds": 5.0,
        }

    suffix = os.path.splitext(filename)[1] or ".webm"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        with open(tmp_path, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                language=language_hint,
                response_format="verbose_json",
            )

        return {
            "transcript": transcript.text,
            "detected_language": getattr(transcript, "language", language_hint or "hi"),
            "duration_seconds": getattr(transcript, "duration", 0.0),
        }
    finally:
        os.unlink(tmp_path)
