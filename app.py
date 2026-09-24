"""ISOM5240: run with `streamlit run app.py`."""

import hashlib
import html
import logging

import streamlit as st

from image_upload import load_image
from story_engine import AGE_GUIDANCE, StoryError, create_audio, create_story, word_count

st.set_page_config(page_title="Picture Story Garden", page_icon="🌈", layout="centered")
st.markdown("""<style>
.stApp {background: #fffaf1;}
h1, h2, h3 {color: #433075;}
[data-testid="stFileUploaderDropzone"] {min-height: 155px; border: 2px dashed #8663b5; border-radius: 20px;}
.stButton button {min-height: 52px; font-size: 1.1rem; border-radius: 16px;}
.story-page {font-size: 1.35rem; line-height: 1.9; color: #302544; background: #fff;
padding: 1.6rem; border-radius: 20px; border: 2px solid #ece2f9;}
</style>""", unsafe_allow_html=True)
st.title("🌈 Picture Story Garden")
st.write("A picture, a little magic, and a story just for you!")
st.caption("1. Pick a picture　 →　 2. Make a story　 →　 3. Listen and imagine")

with st.expander("For grown-ups"):
    st.write("Made for ages 3–10. Read and play together: AI can misread pictures or write unsuitable details. "
             "Simple content checks reduce some problems but cannot guarantee every story is suitable.")
    st.write("Pictures are processed on this app's server and are not intentionally saved. "
             "The story text is sent to Google's text-to-speech service to make audio. "
             "Use pictures without personal information. Stories are in English.")
    st.caption("The first story can take several minutes while the models download. "
               "Later stories still need time on a shared CPU.")

st.subheader("🖼️ Pick your picture")
uploaded = st.file_uploader("Drop a picture here, or click to choose", type=["jpg", "jpeg", "png", "webp"],
                            help="One JPG, PNG, or WebP picture, up to 10 MB.", key="picture")
age_group = st.radio("How old is our reader?", list(AGE_GUIDANCE), horizontal=True)

image = None
image_bytes = uploaded.getvalue() if uploaded is not None else None
input_key = (hashlib.sha256(image_bytes).hexdigest(), age_group) if image_bytes else None
# Never show a previous image's story or audio after the inputs change.
if st.session_state.get("input_key") != input_key:
    for key in ("result", "audio", "audio_failed"):
        st.session_state.pop(key, None)
    st.session_state.input_key = input_key

if uploaded is not None:
    try:
        image = load_image(image_bytes)
        st.image(image, caption="Your story starts here", use_container_width=True)
    except ValueError as exc:
        st.error(str(exc))
else:
    st.info("Try a picture of your favourite animal, a toy, or a beautiful place.")


def speak_story():
    try:
        with st.spinner("Getting our reading voice ready…"):
            st.session_state.audio = create_audio(st.session_state.result.story, age_group)
        st.session_state.audio_failed = False
    except Exception:
        logging.exception("Text-to-speech failed")
        st.session_state.audio_failed = True


if st.button("✨ Make my story", type="primary", use_container_width=True, disabled=image is None):
    for key in ("result", "audio", "audio_failed"):
        st.session_state.pop(key, None)
    with st.status("Opening the story garden…", expanded=True) as status:
        try:
            result = create_story(image, age_group, progress=st.write)
            st.session_state.result = result
            status.update(label="Your story is ready!", state="complete", expanded=False)
        except StoryError as exc:
            status.update(label=str(exc), state="error")
        except Exception:
            logging.exception("Story generation failed")
            status.update(label="The story garden couldn't start. Please try again in a little while.", state="error")
            st.caption("Grown-ups: check the app logs for model download or memory errors.")
    if st.session_state.get("result"):
        speak_story()

if result := st.session_state.get("result"):
    st.subheader("📖 Your little adventure")
    st.markdown(f'<div class="story-page">{html.escape(result.story)}</div>', unsafe_allow_html=True)
    st.caption(f"{word_count(result.story)} words · Made for ages {age_group}")
    if st.session_state.get("audio_failed"):
        st.info("Your story is ready to read! The voice couldn't connect this time.")
        if st.button("🔊 Try the reading voice again"):
            speak_story()
            st.rerun()
    if audio := st.session_state.get("audio"):
        st.subheader("🎧 Listen to your story")
        st.audio(audio, format="audio/mp3")
        st.download_button("⬇️ Keep the audio", audio, "my-story.mp3", "audio/mpeg")
    st.download_button("📄 Keep the story", result.story, "my-story.txt", "text/plain")
    st.write("💬 Your turn: what do you think happens next?")
    with st.expander("What did the storyteller see?"):
        st.write(result.caption)
