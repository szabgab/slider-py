import pytest
import json
import os

from test_tools import compare_dirs
from slider import Slider, SliderError

def test_exceptions(tmpdir):
    slider = Slider()
    path = os.path.join('cases', 'no-chapter-title.md')
    with pytest.raises(Exception) as exinfo:
        slider.parse(path)
    assert exinfo.type == SliderError
    assert str(exinfo.value) == 'Chapter title is missing in {}'.format(path)


    path = os.path.join('cases', 'no-chapter-id.md')
    with pytest.raises(Exception) as exinfo:
        slider.parse(path)
    assert exinfo.type == SliderError
    assert str(exinfo.value) == 'Chapter id is missing in {}'.format(path)


    path = os.path.join('cases', 'chapters.md')
    with pytest.raises(Exception) as exinfo:
        slider.parse(path)
    assert exinfo.type == SliderError
    assert str(exinfo.value) == 'Second chapter found in the same file in {}'.format(path)


@pytest.mark.parametrize("name", [
    'chapter', 'pages', 'all'
])
def test_cases_with_html(tmpdir, name):
    slider = Slider()

    pages = slider.parse(os.path.join('cases', '{}.md'.format(name)))
    with open(os.path.join('cases', 'dom', '{}.json'.format(name))) as fh:
        assert pages == json.load(fh)

    target_dir = str(tmpdir)
    print(target_dir)
    slider.generate_html_files(target_dir)
    compare_dirs(target_dir, os.path.join('cases', 'html', name), name)


@pytest.mark.parametrize("name", [
    'all'
])
def test_templates(tmpdir, name):
    slider = Slider(templates = os.path.join('cases', 'simple_templates'))

    pages = slider.parse(os.path.join('cases', '{}.md'.format(name)))
    with open(os.path.join('cases', 'dom', '{}.json'.format(name))) as fh:
        assert pages == json.load(fh)

    target_dir = str(tmpdir)
    print(target_dir)
    slider.generate_html_files(target_dir)
    compare_dirs(target_dir, os.path.join('cases', 'simple_html', name), name)

@pytest.mark.parametrize("name", [
    'index', 'ul', 'ol', 'verbatim', 'p', 'include'
])
def test_cases(name):
    slider = Slider()
    pages = slider.parse(os.path.join('cases', '{}.md'.format(name)))
    with open(os.path.join('cases', 'dom', '{}.json'.format(name))) as fh:
        assert pages == json.load(fh)




def test_multi():
    slider = Slider()

    data = slider.process_yml(os.path.join('cases', 'multi.yml'))
    assert data == {}


