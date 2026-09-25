from io import BytesIO
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from PIL import Image
from streamlit.testing.v1 import AppTest

import story_engine as engine
from image_upload import MAX_BYTES, load_image

STORY = (
    "A little dog found a bright ball beside a tree. He rolled it toward his friend, "
    "a happy rabbit. Together they made a game of gentle passes across the grass. "
    "When the ball stopped under a leaf, they looked together and found it. "
    "They shared one last turn before resting in the warm sunshine."
)


def picture(fmt='PNG'):
    data = BytesIO()
    Image.new('RGB', (30, 20), 'blue').save(data, format=fmt)
    data.seek(0)
    return data


@pytest.mark.parametrize('fmt', ['JPEG', 'PNG', 'WEBP'])
def test_valid_picture_formats(fmt):
    image = load_image(picture(fmt).getvalue())
    assert image.mode == 'RGB' and image.size == (30, 20)


@pytest.mark.parametrize('data', [b'', b'invalid', b'x' * (MAX_BYTES + 1), picture('GIF').getvalue()])
def test_invalid_picture(data):
    with pytest.raises(ValueError):
        load_image(data)


def test_large_pixel_image_rejected():
    data = BytesIO()
    Image.new('1', (5000, 4000)).save(data, format='PNG')
    with pytest.raises(ValueError, match='pixels'):
        load_image(data.getvalue())


def test_story_constraints_preserve_entire_narrative():
    assert 50 <= engine.word_count(STORY) <= 100
    assert engine.grounded_in_caption(STORY, 'a dog playing with a ball')
    assert not engine.grounded_in_caption(STORY, 'a spaceship above an ocean')
    assert not engine.grounded_in_caption('A fish swam at the beach.', 'a dog at the beach')
    assert engine.grounded_in_caption('A puppy played at the beach.', 'a dog at the beach')
    complete = engine.normalize_story(STORY + ' ' + STORY)
    assert complete.startswith('A little dog')
    assert complete.endswith('They shared one last turn before resting in the warm sunshine.')
    assert complete == STORY + " " + STORY
    assert engine.validation_issues(complete, "a dog with a ball")


def test_rejects_unsafe_story_then_retries():
    generator = Mock(side_effect=[
        [{'generated_text': STORY.replace('bright ball', 'dangerous gun')}],
        [{'generated_text': STORY}],
    ])
    with patch.object(engine, 'make_pipeline', return_value=generator):
        assert engine.generate_story('a dog playing with a ball', '3–5') == STORY
    assert generator.call_count == 2


def test_invalid_generations_never_displayed():
    generator = Mock(return_value=[{'generated_text': 'A dog plays.'}])
    with patch.object(engine, 'make_pipeline', return_value=generator):
        with pytest.raises(engine.StoryError):
            engine.generate_story('a dog playing', '6–8')
    assert generator.call_count == 3


def test_model_lock_released_on_failure():
    with patch.object(engine, 'caption_image', side_effect=RuntimeError('offline')):
        with pytest.raises(RuntimeError):
            engine.create_story(Image.new('RGB', (10, 10)), '3–5')
    assert not engine.MODEL_LOCK.locked()


def test_busy_model_rejected_without_loading():
    with engine.MODEL_LOCK:
        with patch.object(engine, 'make_pipeline') as factory:
            with pytest.raises(engine.StoryError, match='another reader'):
                engine.create_story(Image.new('RGB', (10, 10)), '3–5')
            factory.assert_not_called()


def test_ui_audio_failure_preserves_story_and_retry_works():
    with patch('streamlit.file_uploader', return_value=picture()), \
         patch.object(engine, 'create_story', return_value=engine.StoryResult('a dog', STORY)), \
         patch.object(engine, 'create_audio', side_effect=[RuntimeError('offline'), b'mock mp3']):
        app = AppTest.from_file(Path(__file__).resolve().parent / 'app.py').run()
        app.button[0].click().run()
        assert not app.exception
        assert app.session_state['result'].story == STORY
        assert app.session_state['audio_failed']
        app.button[1].click().run()
        assert app.session_state['audio'] == b'mock mp3'
        app.radio[0].set_value('9–10').run()
        assert 'result' not in app.session_state
        assert 'audio' not in app.session_state


def test_empty_ui_and_corrupt_upload():
    app = AppTest.from_file(Path(__file__).resolve().parent / 'app.py').run()
    assert not app.exception and app.button[0].disabled
    with patch('streamlit.file_uploader', return_value=BytesIO(b'bad')):
        app = AppTest.from_file(Path(__file__).resolve().parent / 'app.py').run()
        assert app.error and app.button[0].disabled


def test_setting_alone_cannot_ground_unrecognized_subject():
    assert not engine.grounded_in_caption("We played at the beach.", "a turtle on the beach")
    assert engine.grounded_in_caption("A turtle rested at the beach.", "a turtle on the beach")
    assert not engine.grounded_in_caption("A dog ran in the park.", "a woman with a dog at the beach")
    assert engine.grounded_in_caption("A lady walked her puppy along the shore.", "a woman with a dog at the beach")


def test_overlong_story_is_rewritten_with_feedback():
    generator = Mock(side_effect=[
        [{"generated_text": STORY + " " + STORY}],
        [{"generated_text": STORY}],
    ])
    with patch.object(engine, 'make_pipeline', return_value=generator):
        assert engine.generate_story('a dog with a ball', '6–8') == STORY
    repair_messages = generator.tokenizer.apply_chat_template.call_args_list[1].args[0]
    assert repair_messages[-2]['content'] == STORY + " " + STORY
    assert 'Rewrite' in repair_messages[-1]['content']
    assert 'words' in repair_messages[-1]['content']


def test_word_boundaries_are_inclusive():
    for length in (49, 50, 100, 101):
        story = 'dog ball ' + 'happy ' * (length - 2)
        issues = engine.validation_issues(story.strip() + '.', 'a dog with a ball')
        assert bool(issues) == (length not in (50, 100))


def test_short_story_gets_generated_continuation():
    draft = "A dog found a ball."
    generator = Mock(side_effect=[
        [{"generated_text": draft}], [{"generated_text": STORY}],
    ])
    with patch.object(engine, 'make_pipeline', return_value=generator):
        story = engine.generate_story('a dog with a ball', '6–8')
    assert story == draft + " " + STORY
    assert not engine.validation_issues(story, 'a dog with a ball')


def test_decorative_emoji_does_not_hide_complete_ending():
    assert engine.normalize_story('The dog smiled. 🐾') == 'The dog smiled.'
    assert engine.grounded_in_caption('Lila played with her retriever by the shore.',
                                      'a woman with a dog on the beach')
