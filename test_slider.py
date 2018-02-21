import pytest
from slider import Slider, SliderError
import json
import filecmp
import os


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

def compare_dirs(left, right, name):
    dcmp = filecmp.dircmp(left, right)
    assert dcmp.left_only == []  # some unexpected files were generated
    assert dcmp.right_only == [] # some expected files were NOT generated
    if dcmp.diff_files != []:
        for filename in dcmp.diff_files:
            print("diff {}/{} {}".format(left, filename, os.path.join('cases', 'html', name, filename)))
    assert dcmp.diff_files == [] # the content of some files is different

