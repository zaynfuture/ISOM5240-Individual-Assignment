# Image upload for ISOM5240

Drag and drop a JPG, PNG, or WebP image (up to 10 MB), or use the file picker.
The image is validated, rotated according to its camera metadata, and previewed.
This implements the requested upload feature; story generation is not implemented.

## Google Colab

1. Open https://colab.research.google.com/ and select **File → Upload notebook**.
2. Upload `ISOM5240_Image_Upload_Colab.ipynb`.
3. Select **Runtime → Run all**. A standard CPU runtime is sufficient.
4. Drop your image into the upload box displayed below the last cell.

The notebook is self-contained: it installs dependencies and needs no local files,
Google Drive mount, API key, or GPU. Gradio displays the interface in Colab and
creates a temporary public link while the runtime is running. Run the final cell
to close it. The preview callback returns a Pillow RGB image, ready to pass to
an image-to-text pipeline.

## Streamlit locally or on Streamlit Community Cloud

```sh
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

For Streamlit Community Cloud, use `app.py` as the entry point and include
`image_upload.py`, `requirements.txt`, and `.streamlit/config.toml`.

References: [Streamlit uploader](https://docs.streamlit.io/develop/api-reference/widgets/st.file_uploader),
[Gradio notebooks and Colab](https://www.gradio.app/guides/quickstart).
