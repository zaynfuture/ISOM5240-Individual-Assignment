"""Run with: streamlit run app.py"""

import streamlit as st

from image_upload import load_image

st.set_page_config(page_title="My Story Picture", page_icon="📚", layout="centered")
st.title("📚 My Story Picture")
st.write("Every story starts with a picture. Choose yours!")

uploaded_file = st.file_uploader(
    "Drag your picture here, or click to choose one",
    type=["jpg", "jpeg", "png", "webp"],
    accept_multiple_files=False,
    help="Choose one JPG, PNG, or WebP picture, up to 10 MB.",
)

if uploaded_file is None:
    st.info("Your picture will appear here after you upload it.")
else:
    try:
        image = load_image(uploaded_file.getvalue())
    except ValueError as exc:
        st.error(str(exc))
    else:
        st.image(image, caption="Your story picture", use_container_width=True)
        st.success("Your picture is ready!")
        st.caption("To change pictures, remove this upload and drop in another one.")
        # Pass `image` to your Hugging Face image-to-text pipeline here.
