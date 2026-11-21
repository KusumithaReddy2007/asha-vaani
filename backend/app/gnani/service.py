
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
    Gnani API Platform integration.

    STT: Prisma v3.0 streaming WebSocket
    TTS: Timbre v3.0 inference API
    """

    def __init__(self):
        self.api_key = settings.GNANI_API_KEY
        self.stt_model = settings.GNANI_STT_MODEL
        self.tts_model = settings.GNANI_TTS_MODEL
        self.ws_url = settings.GNANI_WS_URL
        self.tts_url = settings.GNANI_TTS_URL
        self.default_lang = settings.GNANI_LANGUAGE_CODE

    def is_configured(self) -> bool:
        return bool(
            self.api_key
            and self.api_key.strip()
            and self.api_key != "your_gnani_api_key_here"
        )

    def get_status(self) -> Dict[str, Any]:
        configured = self.is_configured()

        return {
            "provider": "Gnani API Platform",
            "stt_engine": self.stt_model,
            "tts_engine": self.tts_model,
            "is_live_configured": configured,
            "mode": (
                "LIVE_GNANI_CONFIGURED"
                if configured
                else "ADAPTER_DEMO_MODE"
            ),
            "message": (
                "API key configured; live connectivity not yet verified."
                if configured
                else "Gnani API key is not configured."
            ),
        }

    async def stream_audio_to_gnani_prisma(
        self,
        audio_stream: AsyncGenerator[bytes, None],
        on_partial_transcript: Callable[[str], Any],
        on_final_transcript: Callable[[str], Any],
        language_code: str = "en-IN",
        sample_rate: int = 16000,
    ):
        """
        Forward raw PCM audio to Prisma v3.0.

        Audio must be:
        - Signed 16-bit little-endian PCM
        - Mono
        - 1024-byte frames
        - Sample rate matching sample_rate

        The audio generator should finish when the user stops recording.
        """

        if not self.is_configured():
            raise RuntimeError("Gnani API key is not configured.")

        if sample_rate not in (8000, 16000, 44100, 48000):
            raise ValueError("Unsupported Prisma sample rate.")

        headers = {
            "x-api-key-id": self.api_key,
            "X-Model-Identifier": self.stt_model,
            "X-Language-Code": language_code,
            "x-sample-rate": str(sample_rate),
            "format": "codemix",
            "keyterms": json.dumps([
                "ANC",
                "IFA",
                "IFA goli",
                "TT injection",
                "Td",
                "ASHA",
                "PHC",
                "beneficiary",
                "vaccination",
            ]),
        }

        receiver_task = None

        try:
            async with websockets.connect(
                self.ws_url,
                additional_headers=headers,
                open_timeout=15,
                close_timeout=5,
                ping_interval=20,
                ping_timeout=20,
                max_size=2**20,
            ) as ws:

                logger.info("Prisma WebSocket connection established.")

                async def sender():
                    async for chunk in audio_stream:
                        if not chunk:
                            continue

                        if len(chunk) != 1024:
                            raise ValueError(
                                "Prisma audio frames must contain exactly "
                                "1024 bytes."
                            )

                        await ws.send(chunk)

                    # Official Prisma end-of-utterance command.
                    await ws.send(json.dumps({"type": "commit"}))

                async def receiver():
                    async for message in ws:
                        if not isinstance(message, str):
                            continue

                        try:
                            data = json.loads(message)
                        except json.JSONDecodeError:
                            logger.warning(
                                "Received an invalid Prisma response."
                            )
                            continue

                        message_type = data.get("type")

                        if message_type == "error":
                            logger.error(
                                "Prisma returned an API error: %s",
                                data.get("message", "Unknown error"),
                            )
                            continue

                        if message_type != "transcript":
                            continue

                        transcript = data.get("text", "").strip()

                        if not transcript:
                            continue

                        if data.get("is_final") is True:
                            result = on_final_transcript(transcript)
                        else:
                            result = on_partial_transcript(transcript)

                        if asyncio.iscoroutine(result):
                            await result

                receiver_task = asyncio.create_task(receiver())

                await sender()

                # Allow Prisma time to return the final transcript.
                try:
                    await asyncio.wait_for(
                        receiver_task,
                        timeout=8,
                    )
                except asyncio.TimeoutError:
                    logger.warning(
                        "Prisma final transcript wait timed out."
                    )

        except Exception:
            logger.exception("Prisma v3.0 streaming failed.")
            raise

        finally:
            if receiver_task and not receiver_task.done():
                receiver_task.cancel()
                try:
                    await receiver_task
                except asyncio.CancelledError:
                    pass

    async def synthesize_speech_gnani_timbre(
        self,
        text: str,
        language_code: str = "en-IN",
        voice: str = "Shivani",
        gender: Optional[str] = None,
    ) -> Optional[bytes]:
        """
        Generate WAV audio using Gnani Timbre v3.0.

        Returns the binary WAV response or None on failure.
        The gender argument is retained for compatibility with
        older callers; Timbre uses a named voice instead.
        """

        if not self.is_configured():
            logger.warning("Timbre unavailable: API key not configured.")
            return None

        if not text or not text.strip():
            return None

        headers = {
            "X-API-Key-ID": self.api_key,
            "Content-Type": "application/json",
        }

        payload = {
            "text": text.strip(),
            "voice": voice,
            "model": self.tts_model,
            "language": language_code,
            "speed": 1.0,
            "audio_config": {
                "encoding": "linear_pcm",
                "container": "wav",
                "num_channels": 1,
                "sample_rate": 48000,
                "sample_width": 2,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.tts_url,
                    json=payload,
                    headers=headers,
                )

                if response.status_code == 200:
                    logger.info("Timbre speech synthesis succeeded.")
                    return response.content

                logger.error(
                    "Timbre request failed: HTTP %s",
                    response.status_code,
                )
                return None

        except httpx.TimeoutException:
            logger.error("Timbre request timed out.")
            return None

        except Exception:
            logger.exception("Timbre speech synthesis failed.")
            return None


gnani_service = GnaniService()
