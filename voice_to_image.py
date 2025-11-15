import base64
import io
import logging
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

import requests
from openai import OpenAI


logger = logging.getLogger("voice_to_image_agent")


@dataclass
class AgentConfig:
    transcription_model: str = "whisper-1"
    text_model: str = "gpt-4o-mini"
    image_model: str = "dall-e-3"
    image_size: str = "1024x1024"


@dataclass
class VoiceToImageResult:
    transcript: str
    image_prompt: str
    image_bytes: bytes
    models_used: Dict[str, str]


class VoiceToImageAgent:
    def __init__(self, client: Optional[OpenAI] = None, config: Optional[AgentConfig] = None):
        self.client = client or OpenAI()
        self.config = config or AgentConfig()

    def transcribe(self, audio_bytes: bytes, filename: str) -> str:
        suffix = Path(filename).suffix or ".wav"
        logger.info("Saving audio input to a temporary file with suffix %s", suffix)
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_audio:
            temp_audio.write(audio_bytes)
            temp_audio_path = temp_audio.name

        try:
            with open(temp_audio_path, "rb") as handle:
                logger.info("Sending audio to %s for transcription", self.config.transcription_model)
                response = self.client.audio.transcriptions.create(
                    model=self.config.transcription_model,
                    file=handle,
                )
        finally:
            Path(temp_audio_path).unlink(missing_ok=True)

        transcript = response.text.strip()
        logger.info("Transcription complete: %s", transcript)
        return transcript

    def build_image_prompt(self, transcript: str) -> str:
        instructions = (
            "You are a senior creative director. Convert the following voice request "
            "into a vivid, concrete image description for a text-to-image model. "
            "Focus on key subjects, environment, lighting, style, and mood. "
            "Do not add markdown or quotes. Keep it under 120 words."
        )
        logger.info("Generating image prompt with %s", self.config.text_model)
        response = self.client.chat.completions.create(
            model=self.config.text_model,
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": transcript},
            ],
        )
        prompt = response.choices[0].message.content.strip()
        logger.info("Prompt ready: %s", prompt)
        return prompt

    def generate_image(self, prompt: str) -> bytes:
        logger.info(
            "Calling %s to generate image (%s)",
            self.config.image_model,
            self.config.image_size,
        )
        response = self.client.images.generate(
            model=self.config.image_model,
            prompt=prompt,
            size=self.config.image_size,
            n=1,
        )
        # DALL-E 3 returns url, DALL-E 2 returns b64_json
        if hasattr(response.data[0], 'b64_json') and response.data[0].b64_json:
            image_base64 = response.data[0].b64_json
            return base64.b64decode(image_base64)
        else:
            image_url = response.data[0].url
            image_response = requests.get(image_url)
            image_response.raise_for_status()
            return image_response.content

    def run(self, audio_bytes: bytes, filename: str) -> VoiceToImageResult:
        transcript = self.transcribe(audio_bytes, filename)
        prompt = self.build_image_prompt(transcript)
        image_bytes = self.generate_image(prompt)

        return VoiceToImageResult(
            transcript=transcript,
            image_prompt=prompt,
            image_bytes=image_bytes,
            models_used={
                "transcription_model": self.config.transcription_model,
                "text_model": self.config.text_model,
                "image_model": self.config.image_model,
            },
        )


def bytes_to_io(image_bytes: bytes) -> io.BytesIO:
    buffer = io.BytesIO(image_bytes)
    buffer.seek(0)
    return buffer

