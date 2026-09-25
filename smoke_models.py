"""Opt-in real model + speech check: python smoke_models.py.

Downloads public model weights and the BLIP example image. No private images used.
"""
import json
import sys
import time
from io import BytesIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import requests
from PIL import Image
from story_engine import create_story, create_audio, word_count

url = 'https://storage.googleapis.com/sfr-vision-language-research/BLIP/demo.jpg'
response = requests.get(url, timeout=30)
response.raise_for_status()
image = Image.open(BytesIO(response.content)).convert('RGB')
image.thumbnail((1024, 1024))
started = time.monotonic()
result = create_story(image, '6–8', progress=lambda text: print(text, flush=True))
print(json.dumps({'caption': result.caption, 'story': result.story, 'words': word_count(result.story), 'seconds': round(time.monotonic() - started, 1)}, indent=2), flush=True)
audio = create_audio(result.story, '6–8')
print(f'Audio generated: {len(audio)} bytes', flush=True)
