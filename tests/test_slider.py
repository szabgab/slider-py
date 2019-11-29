import sys
import pytest
import json
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools import compare_dirs, read_expected
from slider import MultiSlider, Slider, SliderError, HTML

def test_exceptions():
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

    path = os.path.join('cases', 'duplicate_page_ids.md')
    with pytest.raises(Exception) as exinfo:
        slider.parse(path)
    assert exinfo.type == SliderError
    assert str(exinfo.value) == 'The id page-1-url found twice in file {} in line 11'.format(path)

    path = os.path.join('cases', 'duplicate_ids.md')
    with pytest.raises(Exception) as exinfo:
        slider.parse(path)
    assert exinfo.type == SliderError
    assert str(exinfo.value) == 'The id chapter-url found twice in file {} in line 8'.format(path)

    path = os.path.join('cases', 'missing_page_id.md')
    with pytest.raises(Exception) as exinfo:
        slider.parse(path)
    assert exinfo.type == SliderError
    assert str(exinfo.value) == 'Page id is missing in {} in line 11'.format(path)

    path = os.path.join('cases', 'missing_chapter_id.md')
    with pytest.raises(Exception) as exinfo:
        slider.parse(path)
    assert exinfo.type == SliderError
    assert str(exinfo.value) == 'Chapter id is missing in {}'.format(path)

    path = os.path.join('cases', 'second_page_id.md')
    with pytest.raises(Exception) as exinfo:
        slider.parse(path)
    assert exinfo.type == SliderError
    assert str(exinfo.value) == 'Second page id found in the same file in {} in line 9'.format(path)

    path = os.path.join('cases', 'second_chapter_id.md')
    with pytest.raises(Exception) as exinfo:
        slider.parse(path)
    assert exinfo.type == SliderError
    assert str(exinfo.value) == 'Second chapter id found in the same file in {} in line 4'.format(path)

    path = os.path.join('cases', 'verbatim_outside.md')
    with pytest.raises(Exception) as exinfo:
        slider.parse(path)
    assert exinfo.type == SliderError
    assert str(exinfo.value) == '``` outside of page {} in line 4'.format(path)


@pytest.mark.parametrize("name", [
    'chapter', 'pages', 'all'
])
def test_cases_with_html(tmpdir, name):
    slider = Slider()

    md_file = os.path.join('cases', '{}.md'.format(name))
    pages = slider.parse(md_file)
    with open(os.path.join('cases', 'dom', '{}.json'.format(name))) as fh:
        assert pages == json.load(fh)

    target_dir = str(tmpdir)
    print(target_dir)

    html = HTML(
        chapter  = pages,
        includes = os.path.dirname(md_file),
        ext      = 'html',
    )
    html.generate_html_files(target_dir)
    compare_dirs(target_dir, os.path.join('cases', 'html', name), name)


@pytest.mark.parametrize("name", [
    'all'
])
def test_templates(tmpdir, name):
    slider = Slider()

    md_file = os.path.join('cases', '{}.md'.format(name))
    pages = slider.parse(md_file)
    with open(os.path.join('cases', 'dom', '{}.json'.format(name))) as fh:
        assert pages == json.load(fh)

    target_dir = str(tmpdir)
    print(target_dir)

    html = HTML(
        templates = os.path.join('cases', 'simple_templates'),
        chapter   = pages,
        includes  = os.path.dirname(md_file),
    )
    html.generate_html_files(target_dir)
    compare_dirs(target_dir, os.path.join('cases', 'simple_html', name), name)


@pytest.mark.parametrize("name", [
    'all', 'index'
])
def test_no_extension(tmpdir, name):
    slider = Slider()

    md_file = os.path.join('cases', '{}.md'.format(name))
    pages = slider.parse(md_file)
    with open(os.path.join('cases', 'dom', '{}.json'.format(name))) as fh:
        assert pages == json.load(fh)

    target_dir = str(tmpdir)
    print(target_dir)

    html = HTML(
        chapter   = pages,
        includes  = os.path.dirname(md_file),
    )
    html.generate_html_files(target_dir)
    compare_dirs(target_dir, os.path.join('cases', 'plain_html', name), name)


@pytest.mark.parametrize("name", [
    'index', 'ul', 'ol', 'verbatim', 'p', 'include'
])
def test_cases(name):
    slider = Slider()
    pages = slider.parse(os.path.join('cases', '{}.md'.format(name)))
    with open(os.path.join('cases', 'dom', '{}.json'.format(name))) as fh:
        assert pages == json.load(fh)

def test_multi():
    yml_file = os.path.join('cases', 'multi.yml')

    expected = read_expected(yml_file)

    multi_slider = MultiSlider()

    data = multi_slider.process_yml(yml_file)
    assert data == expected


