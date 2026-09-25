# ISOM5240 — Picture Story Garden

A Python storytelling app for children aged **3–10**. Upload a picture, generate an
English **50–100-word narrative**, then listen to it or download the text and MP3.

## Assignment requirements

| Requirement | Implementation |
|---|---|
| Python and Hugging Face Transformers pipelines | Modular `story_engine.py` uses `pipeline()` for both models |
| User-provided image | Drag-and-drop or file picker; JPG, PNG, WebP; preview and validation |
| Pretrained image captioning | `Salesforce/blip-image-captioning-base`, task `image-to-text` |
| Narrative based on image details | `Qwen/Qwen3-0.6B`, task `text-generation`; caption included in the prompt |
| 50–100 words | Count validated before display; up to three generation attempts; complete drafts are checked; short drafts get model-generated continuations and overlong drafts are rewritten |
| Text to speech | gTTS, audio player, MP3 download, retry on connection failure |
| Ages 3–10 | Three age bands, short-story prompts, large text, simple controls, gentle-content prompts and basic word screening |
| Streamlit Cloud | `app.py`, root requirements, `.streamlit/config.toml`; deployment steps below |

Deployment target: <https://isom5240-individual-assignment-zzhengbj.streamlit.app/>.
The project is linked to `zaynfuture/ISOM5240-Individual-Assignment` on GitHub.
Check `TESTING.md` for the latest observed deployment status.

## Run locally

Use **Python 3.12**, matching the tested runtime.

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

No API key is required. On the first story request, public model weights download
from Hugging Face. Allow several minutes and an internet connection. CPU inference
also takes time after download. Model weights remain in Hugging Face's disk cache.

The text model uses native BF16 precision on CPU to reduce RAM.
The models are loaded one at a time and released between stages. A process-wide
lock prevents concurrent model loading from multiplying memory use. When busy,
other visitors receive a friendly retry message. Qwen3 runs with thinking disabled so only story text is generated.
Models are deliberately not kept
in `st.cache_resource`, which would retain both models in memory. Image and story
results live in the user's Streamlit session, not a shared results cache.

## Deploy to Streamlit Community Cloud

1. Create a GitHub repository and upload:

   ```text
   app.py
   story_engine.py
   image_upload.py
   requirements.txt
   .streamlit/config.toml
   ```

   Keep these paths at the repository root. Do not upload virtual environments,
   model caches, personal pictures, or secrets. The notebook and tests may be
   included for submission but are not needed by the deployed app.
2. Sign in at <https://share.streamlit.io/> and choose **Create app**.
3. Select your repository and the branch containing the files.
4. Set **Main file path** to `app.py`.
5. In **Advanced settings**, select **Python 3.12**. Leave **Secrets** empty.
6. Choose an available app URL and click **Deploy**.
7. Upload a cheerful image, generate a story, check the 50–100-word count, play
   the audio, then change the image to confirm old results clear.
8. Submit the resulting `https://...streamlit.app` URL with the source files.

Cloud memory and CPU availability vary. If logs show memory exhaustion, do not
claim deployment succeeded: verify the current hosting allocation before using
larger models. Keeping inference sequential limits memory but does not guarantee
compatibility with every allocation. Transformers is pinned to 4.57.6 because
this implementation uses its `image-to-text` pipeline.

## Google Colab

Upload `ISOM5240_Image_Upload_Colab.ipynb` to
<https://colab.research.google.com/> and select **Runtime → Run all**. It installs
dependencies, writes the same shared source modules, and opens a Gradio interface
for the complete image → story → audio flow. No other project files are needed.
A CPU runtime works. The notebook creates a temporary public Gradio link;
close the app with its final optional cell when finished.

After changing the shared Python modules, regenerate the notebook with:

```sh
python build_colab.py
```

The notebook retains its original filename so existing links still work.
Streamlit Cloud uses `app.py`; it does not run the notebook or Gradio.

## Children, privacy, and limitations

- English stories only. Age bands guide reading complexity; they do not measure
  a child's individual reading level.
- An adult should read and play with the child. Prompting and a small word filter
  are **not comprehensive image or text moderation**. They can miss harmful
  content or block innocent wording. No automatic safety guarantee is made.
- Image captioning can be wrong; the generated story is imaginative. The grounding
  check requires multiple caption details when available, with synonyms for common
  subjects and places. It cannot prove visual or semantic accuracy.
- A story that repeatedly fails length, caption-detail, or content validation produces a retry message rather than
  a fabricated template claimed to be model output.
- Pictures are processed on the hosting server, not sent to a hosted inference
  API. Streamlit does not intentionally persist uploads in this app. Gradio uses
  temporary files for uploads/audio in Colab. Do not upload personal information.
- gTTS sends the **story text** to Google's speech service. Internet or service
  failures leave the written story available with a separate audio retry button.
- The app intentionally does not autoplay audio.

## Tests

```sh
python -m pip install pytest nbformat
python -m pytest -q
python smoke_models.py
```

Unit/UI tests mock model and speech calls; they exercise upload validation,
length/grounding checks, unsafe-output retries, failure handling, model locking,
audio retries, and clearing stale results. The separate smoke script downloads
the public BLIP example photograph and runs real models and real gTTS. See
`TESTING.md` for observed results and remaining deployment checks.

## References

- [BLIP model card](https://huggingface.co/Salesforce/blip-image-captioning-base)
- [Qwen3 model card](https://huggingface.co/Qwen/Qwen3-0.6B)
- [Streamlit deployment](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)
- [gTTS API](https://gtts.readthedocs.io/en/stable/module.html)
