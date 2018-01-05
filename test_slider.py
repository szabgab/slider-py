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
    'chapter',
])
def test_cases_with_html(tmpdir, name):
    slider = Slider()

    pages = slider.parse('cases/{}.md'.format(name))
    with open('cases/dom/{}.json'.format(name)) as fh:
        assert pages == json.load(fh)

    target_dir = str(tmpdir)
#    print(target_dir)
    slider.generate_html_files(target_dir)
    dcmp = filecmp.dircmp(target_dir, os.path.join('cases', 'html', name))
    assert dcmp.left_only == []
    assert dcmp.right_only == []
    assert dcmp.diff_files == []


@pytest.mark.parametrize("name", [
    'pages', 'index', 'ul', 'ol', 'verbatim', 'p', 'all'
])
def test_cases(name):
    slider = Slider()
    pages = slider.parse('cases/{}.md'.format(name))
    with open('cases/dom/{}.json'.format(name)) as fh:
        assert pages == json.load(fh)

def test_include():
    slider = Slider()

    pages = slider.parse('cases/include.md')
    assert pages == {
        'title' : 'Chapter Title',
        'id'    : 'chapter-url',
        'pages' : [
            {
                'title'   : 'Page One Title',
                'id'      : 'page-1-url',
                'content' : [
                    {
                        'name' : 'include',
                        'filename' : 'sample/do.py',
                        'title' : 'This Title',
                        'content' : ["import sys\n\ndef main():\n    print(sys.argv)\n\n\n\nif __name__ == '__main__':\n    main()\n"]
                    }
                ]
            },
            {
                'title': 'Page Two Title',
                'id': 'page-2-url',
                'content': [
                    {
                        'name': 'include',
                        'filename': 'sample/do.py',
                        'title': '',
                        'content': ["import sys\n\ndef main():\n    print(sys.argv)\n\n\n\nif __name__ == '__main__':\n    main()\n"],
                    }
                ]
            },
        ],
    }





def test_multi():
    slider = Slider()

    data = slider.process_yml('cases/multi.yml')
    assert data == {}
