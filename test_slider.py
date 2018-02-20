import pytest
from slider import Slider, SliderError
import json
import filecmp
import os

def test_exceptions(tmpdir):
    slider = Slider()
    with pytest.raises(Exception) as exinfo:
        slider.parse('cases/no-chapter-title.md')
    assert exinfo.type == SliderError
    assert str(exinfo.value) == 'Chapter title is missing in cases/no-chapter-title.md'


    with pytest.raises(Exception) as exinfo:
        slider.parse('cases/no-chapter-id.md')
    assert exinfo.type == SliderError
    assert str(exinfo.value) == 'Chapter id is missing in cases/no-chapter-id.md'


    with pytest.raises(Exception) as exinfo:
        slider.parse('cases/chapters.md')
    assert exinfo.type == SliderError
    assert str(exinfo.value) == 'Second chapter found in the same file in cases/chapters.md'


@pytest.mark.parametrize("name", [
    'chapter', 'pages', 'all'
])
def test_cases_with_html(tmpdir, name):
    slider = Slider()

    pages = slider.parse('cases/{}.md'.format(name))
    with open('cases/dom/{}.json'.format(name)) as fh:
        assert pages == json.load(fh)

    target_dir = str(tmpdir)
    print(target_dir)
    slider.generate_html_files(target_dir)
    dcmp = filecmp.dircmp(target_dir, os.path.join('cases', 'html', name))
    assert dcmp.left_only == []  # some unexpected files were generated
    assert dcmp.right_only == [] # some expected files were NOT generated
    if dcmp.diff_files != []:
        for filename in dcmp.diff_files:
            print("diff {}/{} {}".format(target_dir, filename, os.path.join('cases', 'html', name, filename)))
    assert dcmp.diff_files == [] # the content of some files is different


@pytest.mark.parametrize("name", [
    'index', 'ul', 'ol', 'verbatim', 'p', 'include'
])
def test_cases(name):
    slider = Slider()
    pages = slider.parse('cases/{}.md'.format(name))
    with open('cases/dom/{}.json'.format(name)) as fh:
        assert pages == json.load(fh)


def test_multi():
    slider = Slider()

    data = slider.process_yml('cases/multi.yml')
    assert data == {}
