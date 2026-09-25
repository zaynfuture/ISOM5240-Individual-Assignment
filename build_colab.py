"""Rebuild a self-contained Colab notebook from the shared application modules."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def cell(kind, source, index):
    value = {"cell_type": kind, "id": f"story-{index}", "metadata": {}, "source": source.splitlines(keepends=True)}
    if kind == "code":
        value.update(execution_count=None, outputs=[])
    return value

setup = '''from pathlib import Path
import gradio as gr
from image_upload import load_image, MAX_BYTES
from story_engine import AGE_GUIDANCE, StoryError, create_story, create_audio


def tell_story(filepath, age_group):
    if not filepath:
        raise gr.Error("Please choose a picture first.")
    try:
        with open(filepath, "rb") as uploaded:
            image = load_image(uploaded.read(MAX_BYTES + 1))
        result = create_story(image, age_group)
    except (ValueError, StoryError) as exc:
        raise gr.Error(str(exc)) from exc
    except Exception as exc:
        raise gr.Error("The storyteller could not start. Check the notebook output and try again.") from exc
    try:
        audio = create_audio(result.story, age_group)
        note = "Press play to hear your story!"
    except Exception:
        audio = None
        note = "Your story is ready. The voice could not connect; use Read my story aloud."
    return result.story, audio, result.caption, note


def retry_audio(story, age_group):
    if not story:
        raise gr.Error("Make a story first.")
    try:
        return create_audio(story, age_group), "Press play to hear your story!"
    except Exception as exc:
        raise gr.Error("The voice could not connect. Please try again later.") from exc


if "demo" in globals():
    demo.close()
with gr.Blocks(title="Picture Story Garden") as demo:
    gr.Markdown("# 🌈 Picture Story Garden\\nPick a picture. Make a story. Listen and imagine!")
    with gr.Accordion("For grown-ups", open=False):
        gr.Markdown("Read and play together. AI may misread images or write unsuitable details; simple checks cannot guarantee suitability. Stories are in English. Story text goes to Microsoft for natural neural speech. Images are processed in this Colab runtime. Gradio temporarily caches uploads and audio; do not use personal pictures on a shared link. The first run downloads the models and may take several minutes.")
    upload = gr.File(label="Drop a picture here, or click to choose", file_types=[".jpg", ".jpeg", ".png", ".webp"], type="filepath")
    age = gr.Radio(list(AGE_GUIDANCE), value="3–5", label="How old is our reader?")
    make = gr.Button("✨ Make my story", variant="primary")
    story = gr.Textbox(label="Your little adventure", lines=7, interactive=False)
    audio = gr.Audio(label="Listen to your story — gentle storytelling voice", autoplay=False)
    note = gr.Textbox(label="Story garden", interactive=False)
    retry = gr.Button("🔊 Read my story aloud")
    with gr.Accordion("What did the storyteller see?", open=False):
        caption = gr.Textbox(label="Picture details", interactive=False)
    make.click(tell_story, [upload, age], [story, audio, caption, note], concurrency_limit=1, concurrency_id="story-inputs")
    retry.click(retry_audio, [story, age], [audio, note], concurrency_id="story-inputs")
    # Share a queue so an input change clears any previous generation result.
    upload.change(lambda: ("", None, "", ""), outputs=[story, audio, caption, note], concurrency_id="story-inputs")
    age.change(lambda: ("", None, "", ""), outputs=[story, audio, caption, note], concurrency_id="story-inputs")
demo.queue(default_concurrency_limit=1)
demo.launch(share=True, inline=True, max_file_size="10mb")
'''
modules = ['image_upload.py', 'story_engine.py']
write_modules = 'from pathlib import Path\n\n' + '\n'.join(
    f'Path({name!r}).write_text({(ROOT / name).read_text()!r})' for name in modules)
cells = [
    cell('markdown', '# ISOM5240 — Picture Story Garden\n\nRun all cells to upload a picture, generate a 50–100-word story with Hugging Face Transformers pipelines, and listen to it. No API key or other project files are needed. A CPU runtime works; allow several minutes for the first model download.\n\nThis notebook uses Gradio for Colab. Deploy `app.py` from the project to Streamlit Cloud for the assignment submission. The notebook creates a temporary public Gradio link while running.', 0),
    cell('code', '%pip -q install "transformers==4.57.6" "torch>=2.6,<3" "Pillow>=11,<13" "edge-tts==7.2.8" "gradio>=5,<7"', 1),
    cell('code', write_modules, 2),
    cell('code', setup, 3),
    cell('markdown', 'When finished, change `STOP_APP` to `True` and run the next cell to close the shared app.', 4),
    cell('code', 'STOP_APP = False\nif STOP_APP:\n    demo.close()\n', 5),
]
notebook = {'nbformat': 4, 'nbformat_minor': 5, 'metadata': {'colab': {'provenance': []}, 'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}, 'language_info': {'name': 'python'}}, 'cells': cells}
(ROOT / 'ISOM5240_Image_Upload_Colab.ipynb').write_text(json.dumps(notebook, indent=2) + '\n')
