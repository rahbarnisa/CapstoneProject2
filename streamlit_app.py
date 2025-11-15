import logging
import os
from typing import Optional

import streamlit as st
from dotenv import load_dotenv

from voice_to_image import AgentConfig, VoiceToImageAgent, VoiceToImageResult


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    force=True,
)
logger = logging.getLogger("voice_to_image_app")


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

TRANSCRIPTION_MODELS = ["whisper-1"]
TEXT_MODELS = ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"]
IMAGE_MODELS = ["dall-e-3", "dall-e-2"]
IMAGE_SIZES = ["1024x1024", "1792x1024", "1024x1792"]  # DALL-E 3 sizes (DALL-E 2 uses 256x256, 512x512, 1024x1024)


def get_agent(config: AgentConfig) -> VoiceToImageAgent:
    return VoiceToImageAgent(config=config)


def process_audio(agent: VoiceToImageAgent, audio_file) -> Optional[VoiceToImageResult]:
    if audio_file is None:
        return None

    audio_bytes = audio_file.getvalue()
    logger.info("Received audio file %s (%s bytes)", audio_file.name, len(audio_bytes))
    return agent.run(audio_bytes, audio_file.name)


st.set_page_config(page_title="Voice to Image Studio", layout="wide")
st.title("🎙️ Voice to Image Studio")
st.caption("Record or upload a short voice note, let the agent transcribe, craft an image prompt, and visualise the final artwork.")

if not OPENAI_API_KEY:
    st.error("OPENAI_API_KEY is missing. Add it to a .env file or environment variable before running the app.")
    st.stop()

with st.sidebar:
    st.header("Model configuration")
    selected_transcription_model = st.selectbox("Transcription model", TRANSCRIPTION_MODELS, index=0)
    selected_text_model = st.selectbox("Prompt authoring model", TEXT_MODELS, index=0)
    selected_image_model = st.selectbox("Image generator", IMAGE_MODELS, index=0)
    # Adjust sizes based on selected model (DALL-E 2 vs DALL-E 3)
    if selected_image_model == "dall-e-2":
        available_sizes = ["256x256", "512x512", "1024x1024"]
    else:
        available_sizes = IMAGE_SIZES
    default_size = "1024x1024" if "1024x1024" in available_sizes else available_sizes[0]
    selected_image_size = st.select_slider("Image size", available_sizes, value=default_size)
    st.caption("All interactions stream logs to the terminal for observability.")

st.markdown(
    """
1. Upload a voice memo describing the scene you want.
2. The agent transcribes the audio and turns it into a detailed image prompt.
3. An image model renders the scene and displays it here, along with every intermediate artifact.
    """
)

uploaded_audio = st.file_uploader(
    "Upload a short voice message (MP3, WAV, M4A, or WEBM)",
    type=["mp3", "wav", "m4a", "webm"],
    accept_multiple_files=False,
)

if uploaded_audio:
    st.audio(uploaded_audio, format=uploaded_audio.type)

trigger = st.button("Generate image", disabled=uploaded_audio is None, use_container_width=True)

if trigger and uploaded_audio:
    agent_config = AgentConfig(
        transcription_model=selected_transcription_model,
        text_model=selected_text_model,
        image_model=selected_image_model,
        image_size=selected_image_size,
    )
    agent = get_agent(agent_config)

    with st.spinner("Transcribing and painting..."):
        try:
            result = process_audio(agent, uploaded_audio)
            st.session_state["latest_result"] = {
                "result": result,
                "audio_name": uploaded_audio.name,
            }
            st.success("Done! See the transcript, prompt, and generated image below.")
        except Exception as exc:
            logger.exception("Voice to image pipeline failed")
            st.error(f"Something went wrong: {exc}")

st.divider()

stored = st.session_state.get("latest_result")

if stored:
    result = stored["result"]

    st.subheader("Recorded Message Transcript")
    st.write(result.transcript)

    st.subheader("Prompt sent to the image model")
    st.code(result.image_prompt, language="text")

    st.subheader("Models in this run")
    cols = st.columns(len(result.models_used))
    for idx, (label, model_name) in enumerate(result.models_used.items()):
        cols[idx].metric(label.replace("_", " ").title(), model_name)

    st.subheader("Generated Artwork")
    st.image(result.image_bytes, caption="AI generated image", use_column_width=True)
    st.download_button(
        "Download image",
        data=result.image_bytes,
        file_name="voice_to_image.png",
        mime="image/png",
        use_container_width=True,
    )
else:
    st.info("Upload an audio file and click **Generate image** to see your results here.")