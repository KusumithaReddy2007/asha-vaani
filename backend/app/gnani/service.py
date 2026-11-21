import asyncio
import json
import logging
from typing import AsyncGenerator, Callable, Optional, Dict, Any
import httpx
import websockets
from app.core.config import settings

logger = logging.getLogger("gnani_service")

class GnaniService:
    """
    Official Gnani API Platform Integration Service
    - STT: Gnani Prisma v3.0 (Streaming WebSocket)
    - TTS: Gnani Timbre v3.0 (Streaming Audio Synthesis)
    """

    def __init__(self):
        self.api_key = settings.GNANI_API_KEY
        self.stt_model = settings.GNANI_STT_MODEL # Prisma-v3.0
        self.tts_model = settings.GNANI_TTS_MODEL # Timbre-v3.0
        self.ws_url = settings.GNANI_WS_URL
        self.tts_url = settings.GNANI_TTS_URL
        self.default_lang = settings.GNANI_LANGUAGE_CODE

    def is_configured(self) -> bool:
        """Check if a real Gnani API key is configured."""
        return bool(self.api_key and self.api_key.strip() and self.api_key != "your_gnani_api_key_here")

    def get_status(self) -> Dict[str, Any]:
        """Return connectivity status of Gnani integration."""
        configured = self.is_configured()
        return {
            "provider": "Gnani API Platform",
            "stt_engine": self.stt_model,
            "tts_engine": self.tts_model,
            "is_live_configured": configured,
            "mode": "LIVE_GNANI_PRODUCTION" if configured else "ADAPTER_DEMO_MODE",
            "message": "Connected to Gnani Cloud" if configured else "Gnani API key not configured. Add GNANI_API_KEY in backend/.env to connect live."
        }

    async def stream_audio_to_gnani_prisma(
        self,
        audio_stream: AsyncGenerator[bytes, None],
        on_partial_transcript: Callable[[str], Any],
        on_final_transcript: Callable[[str], Any],
        language_code: str = "en-IN"
    ):
        """
        Stream binary audio chunks to Gnani Prisma v3.0 WebSocket.
        Formats: 16000Hz, 16-bit Mono Linear PCM or WebM/Opus.
        """
        if not self.is_configured():
            logger.info("Gnani API key not set. Utilizing adapter layer.")
            return

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "X-Model-Identifier": self.stt_model,
            "X-Language-Code": language_code
        }

        try:
            async with websockets.connect(self.ws_url, extra_headers=headers) as ws:
                logger.info(f"Connected to Gnani Prisma v3.0 endpoint: {self.ws_url}")

                # Task 1: Send audio chunks
                async def sender():
                    async for chunk in audio_stream:
                        if chunk:
                            await ws.send(chunk)
                    # Send end-of-stream delimiter if required by protocol
                    await ws.send(json.dumps({"action": "stop"}))

                # Task 2: Receive transcription frames
                async def receiver():
                    async for message in ws:
                        data = json.loads(message)
                        transcript = data.get("transcript", "")
                        is_final = data.get("is_final", False)
                        if is_final:
                            await on_final_transcript(transcript)
                        else:
                            await on_partial_transcript(transcript)

                await asyncio.gather(sender(), receiver())
        except Exception as e:
            logger.error(f"Gnani Prisma v3.0 WebSocket error: {e}")
            raise

    async def synthesize_speech_gnani_timbre(
        self,
        text: str,
        language_code: str = "en-IN",
        gender: str = "female"
    ) -> Optional[bytes]:
        """
        Synthesize speech using Gnani Timbre v3.0 TTS.
        Returns binary audio bytes (WAV/MP3).
        """
        if not self.is_configured():
            logger.info("Gnani Timbre v3.0: Key not set. Returning None to allow frontend synthesis.")
            return None

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.tts_model,
            "text": text,
            "language": language_code,
            "voice_gender": gender,
            "audio_format": "wav",
            "sample_rate": 24000
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(self.tts_url, json=payload, headers=headers)
                if response.status_code == 200:
                    return response.content
                else:
                    logger.warning(f"Gnani Timbre TTS failed with status {response.status_code}: {response.text}")
                    return None
        except Exception as e:
            logger.error(f"Gnani Timbre TTS Exception: {e}")
            return None

gnani_service = GnaniService()
