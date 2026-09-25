# Validation record — 25 September 2026

Current runtime tested locally: Python 3.12.14, Transformers 4.57.6, PyTorch 2.8.0,
Streamlit 1.64.0, Pillow 12.3.0, gTTS 2.5.4. Models: BLIP image captioning and
Qwen3-0.6B text generation, using Transformers pipelines on CPU.

## Current automated checks

`python -m pytest -q`: **24 passed**.

Checks cover valid/corrupt/oversized images, exact 50/100-word acceptance boundaries,
multiple caption details and common synonyms, rejecting unrelated settings,
complete-story rewrites, model-generated extensions of short stories, content
screening, model locking, audio failure/retry, replay without regenerating the story,
age-dependent speech speed, and clearing stale UI results.

No sentences are deleted to fit the word limit. Drafts outside 50–100 words are
expanded or rewritten by the model. Up to three attempts are permitted. A failed
validation produces a retry message rather than displaying an invalid story.

## Real model verification

A public BLIP demonstration image was processed by the final model pair:

- Caption: `a woman sitting on the beach with her dog`.
- Returned narrative: **62 words**.
- Recognizable picture details: a golden retriever (dog) and the beach.
- The final story passed all acceptance checks without deleting sentences.

Generation is sampled: future stories may differ or need another try. Caption
coverage is lexical, not a guarantee that every visual detail is correct. Basic
content checks are not comprehensive child-safety moderation.

The earlier build's real gTTS smoke check generated a 253,248-byte MP3; audio
creation/retry code remains the same. The current build also completed audio generation on Streamlit Cloud, as
recorded below. Timing and memory from earlier model versions are
not treated as measurements of this build.

## UI and Colab

The Streamlit upload, preview, story display, audio controls, and downloads were
inspected in a local browser during development. Automated UI tests cover the
current flow with mocked network/model calls. The self-contained Colab notebook
is rebuilt from the shared source modules. A live Google Colab session has not
been tested.

## Deployment

Existing app: <https://isom5240-individual-assignment-zzhengbj.streamlit.app/>.
Repository: <https://github.com/zaynfuture/ISOM5240-Individual-Assignment>.
Streamlit Cloud's Python setting was changed from 3.14 to the tested 3.12 runtime.
The repository previously contained only the initial uploader. The complete story app is now published. On the live Cloud app, the public BLIP
sample image uploaded and previewed correctly; generation returned a 62-word
story featuring the pictured dog and beach. Audio creation completed and both
the player and MP3 download control appeared. The in-app browser renderer crashed
when Play was clicked, so actual playback in that browser remains unverified.
The source code did not report a TTS error. Test playback in a normal browser
before submission. Cloud logs confirmed Python 3.12.14 and torch 2.8.0+cpu.
The upload control showed the configured 10 MB limit.
