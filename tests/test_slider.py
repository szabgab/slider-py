import sys
import pytest
import json
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools import compare_dirs, read_expected
from slider import MultiSlider, Slider, SliderError, Book, OnePage


def test_exceptions():
    slider = Slider()

    path = os.path.join('cases', 'input', 'no-chapter-title.md')
    with pytest.raises(Exception) as exinfo:
        slider.parse(path)
    assert exinfo.type == SliderError
    assert str(exinfo.value) == 'Chapter title is missing in {}'.format(path)

    path = os.path.join('cases', 'input', 'no-chapter-id.md')
    with pytest.raises(Exception) as exinfo:
        slider.parse(path)
    assert exinfo.type == SliderError
    assert str(exinfo.value) == 'Chapter id is missing in {}'.format(path)

    path = os.path.join('cases', 'input', 'chapters.md')
    with pytest.raises(Exception) as exinfo:
        slider.parse(path)
    assert exinfo.type == SliderError
    assert str(exinfo.value) == "Second chapter 'Chapters Title 1' found in the same file in '{}'".format(path)

    path = os.path.join('cases', 'input', 'duplicate_page_ids.md')
    with pytest.raises(Exception) as exinfo:
        slider.parse(path)
    assert exinfo.type == SliderError
    assert str(exinfo.value) == 'The id page-1-url found twice in file {} in line 11'.format(path)

    path = os.path.join('cases', 'input', 'duplicate_ids.md')
    with pytest.raises(Exception) as exinfo:
        slider.parse(path)
    assert exinfo.type == SliderError
    assert str(exinfo.value) == 'The id chapter-url found twice in file {} in line 8'.format(path)

    path = os.path.join('cases', 'input', 'missing_page_id.md')
    with pytest.raises(Exception) as exinfo:
        slider.parse(path)
    assert exinfo.type == SliderError
    assert str(exinfo.value) == 'Page id is missing in {} in line 11'.format(path)

    path = os.path.join('cases', 'input', 'missing_chapter_id.md')
    with pytest.raises(Exception) as exinfo:
        slider.parse(path)
    assert exinfo.type == SliderError
    assert str(exinfo.value) == 'Chapter id is missing in {}'.format(path)

    path = os.path.join('cases', 'input', 'second_page_id.md')
    with pytest.raises(Exception) as exinfo:
        slider.parse(path)
    assert exinfo.type == SliderError
    assert str(exinfo.value) == "Second page id 'page-1-url' found in the same file in '{}' in line '9'".format(path)

    path = os.path.join('cases', 'input', 'second_chapter_id.md')
    with pytest.raises(Exception) as exinfo:
        slider.parse(path)
    assert exinfo.type == SliderError
    assert str(exinfo.value) == 'Second chapter id found in the same file in {} in line 4'.format(path)

    path = os.path.join('cases', 'input', 'verbatim_outside.md')
    with pytest.raises(Exception) as exinfo:
        slider.parse(path)
    assert exinfo.type == SliderError
    assert str(exinfo.value) == '``` outside of page {} in line 4'.format(path)

    path = os.path.join('cases', 'input', 'incorrect-include.md')
    with pytest.raises(Exception) as exinfo:
        slider.parse(path)
    assert exinfo.type == SliderError
    assert str(exinfo.value) == 'Included file "cases/input/some/not/existing/place" does not exist. In {} in line 9.'.format(path)


@pytest.mark.parametrize("name", [
    'chapter', 'index', 'pages', 'tables', 'all', 'verbatim'
])
def test_md_to_html(tmpdir, name):
    slider = Slider()

    md_file = os.path.join('cases', 'input', '{}.md'.format(name))
    pages = slider.parse(md_file)
    with open(os.path.join('cases', 'output', 'dom', '{}.json'.format(name))) as fh:
        assert pages == json.load(fh)

    target_dir = str(tmpdir)
    print(target_dir)

    html = OnePage(
        chapter  = pages,
        includes = os.path.dirname(md_file),
        ext      = 'html',
    )
    html.generate_html_files(target_dir)
    compare_dirs(target_dir, os.path.join('cases', 'output', 'html', name), name)


@pytest.mark.parametrize("name", [
    'all'
])
def test_md_to_html_other_templates(tmpdir, name):
    slider = Slider()

    md_file = os.path.join('cases', 'input', '{}.md'.format(name))
    pages = slider.parse(md_file)
    with open(os.path.join('cases', 'output', 'dom', '{}.json'.format(name))) as fh:
        assert pages == json.load(fh)

    target_dir = str(tmpdir)
    print(target_dir)

    html = OnePage(
        templates = os.path.join('cases', 'input', 'simple_templates'),
        chapter   = pages,
        includes  = os.path.dirname(md_file),
    )
    html.generate_html_files(target_dir)
    compare_dirs(target_dir, os.path.join('cases', 'output', 'simple_html', name), name)


@pytest.mark.parametrize("name", [
    'all', 'index'
])
def test_md_to_html_no_file_extension(tmpdir, name):
    slider = Slider()

    md_file = os.path.join('cases', 'input', '{}.md'.format(name))
    pages = slider.parse(md_file)
    with open(os.path.join('cases', 'output', 'dom', '{}.json'.format(name))) as fh:
        assert pages == json.load(fh)

    target_dir = str(tmpdir)
    print(target_dir)

    html = OnePage(
        chapter   = pages,
        includes  = os.path.dirname(md_file),
    )
    html.generate_html_files(target_dir)
    compare_dirs(target_dir, os.path.join('cases', 'output', 'plain_html', name), name)


@pytest.mark.parametrize("name", [
    'all', 'chapter', 'include', 'index', 'ul', 'ol', 'p', 'pages', 'verbatim', 'one_chapter', 'tables',
])
def test_md_to_dom(name):
    slider = Slider()
    pages = slider.parse(os.path.join('cases', 'input', '{}.md'.format(name)))
    with open(os.path.join('cases', 'output', 'dom', '{}.json'.format(name))) as fh:
        assert pages == json.load(fh)


@pytest.mark.parametrize("name", [
    'multi',
])
def test_json_to_dom(name):
    yml_file = os.path.join('cases', 'input', name + '.json')

    expected = read_expected(yml_file)

    multi_slider = MultiSlider()

    data = multi_slider.process_yml(yml_file)
    assert data == expected


@pytest.mark.parametrize("name", [
    'multi',
])
def test_json_to_html(tmpdir, name):
    yml_file = os.path.join('cases', 'input', name + '.json')
    target_dir = str(tmpdir)
    print(target_dir)

    multi_slider = MultiSlider()
    book = multi_slider.process_yml(yml_file)
    html = Book(
        book      = book,
        includes  = os.path.dirname(yml_file),
        ext       = '',
    )
    html.generate_book(target_dir)
    compare_dirs(target_dir, os.path.join('cases', 'output', 'multi_html', name), name)


def test_duplicate_id_in_chapters_of_multi():
    yml_file = os.path.join('cases', 'input', 'duplicate_id.json')

    multi_slider = MultiSlider()

    with pytest.raises(Exception) as exinfo:
        multi_slider.process_yml(yml_file)
    assert exinfo.type == SliderError
    assert str(exinfo.value) == 'Duplicate id chapter-path'


def test_duplicate_id_in_pages_of_multi():
    yml_file = os.path.join('cases', 'input', 'duplicate_page_ids.json')

    multi_slider = MultiSlider()

    with pytest.raises(Exception) as exinfo:
        multi_slider.process_yml(yml_file)
    assert exinfo.type == SliderError
    assert str(exinfo.value) == 'Duplicate id page-1-url'

