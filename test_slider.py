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
    'pages', 'index'
])
def test_cases(name):
    slider = Slider()
    pages = slider.parse('cases/{}.md'.format(name))
    with open('cases/dom/{}.json'.format(name)) as fh:
        assert pages == json.load(fh)


def test_ul():
    slider = Slider()

    pages = slider.parse('cases/ul.md')
    assert pages == {
        'title' : 'Chapter Title',
        'id'    : 'chapter-url',
        'pages' : [
            {
                'title'   : 'Page One Title',
                'id'      : 'page-1-url',
                'content' : [
                    {
                        'name' : 'ul',
                        'content' : [
                            'Several Bullet',
                            'Points',
                            'There is a 3rd point',
                        ]
                    }
                ]
            },
            {
                'title': 'Page Two Title',
                'id': 'page-2-url',
            },
        ],
    }


def test_ol():
    slider = Slider()

    pages = slider.parse('cases/ol.md')
    assert pages == {
        'title' : 'Chapter Title',
        'id'    : 'chapter-url',
        'pages' : [
            {
                'title'   : 'Page One Title',
                'id'      : 'page-1-url',
                'content' : [
                    {
                        'name' : 'ol',
                        'content' : [
                            'Several Bullet',
                            'Points',
                            'There is a 3rd point',
                        ]
                    }
                ]
            },
            {
                'title': 'Page Two Title',
                'id': 'page-2-url',
            },
        ],
    }

def test_verbatim():
    slider = Slider()

    pages = slider.parse('cases/verbatim.md')
    assert pages == {
        'title' : 'Chapter Title',
        'id'    : 'chapter-url',
        'pages' : [
            {
                'title'   : 'Page One Title',
                'id'      : 'page-1-url',
                'content' : [
                    {
                        'name' : 'verbatim',
                        'content' : [
'''
code
    indentend line of this
another
'''
                        ]
                    }
                ]
            },
            {
                'title': 'Page Two Title',
                'id': 'page-2-url',
            },
        ],
    }


def test_paragraphs():
    slider = Slider()

    pages = slider.parse('cases/p.md')
    assert pages == {
        'title' : 'Chapter Title',
        'id'    : 'chapter-url',
        'pages' : [
            {
                'title'   : 'Page One Title',
                'id'      : 'page-1-url',
                'content' : [
                    {
                        'name' : 'p',
                        'content' : [
'''
First line
    Indented line
3rd line
'''
                        ]
                    }
                ]
            },
            {
                'title': 'Page Two Title',
                'id': 'page-2-url',
            },
        ],
    }


def test_include():
    slider = Slider()

    with open('cases/sample/do.py', 'r') as fh:
        file_content = fh.read()

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
                        'content' : [file_content]
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
                        'content': [file_content],
                    }
                ]
            },
        ],
    }



def test_all():
    slider = Slider()

    pages = slider.parse('cases/all.md')
    assert pages == {
        'title' : 'Chapter Title',
        'id'    : 'chapter-url',
        'pages' : [
            {
                'title'   : 'Page One Title',
                'id'      : 'page-1-url',
                'content' : [
                    {
                        'name' : 'ol',
                        'content' : [
                            'Several Bullet',
                            'Points',
                            'There is a 3rd point',
                        ]
                    }
                ]
            },
            {
                'title': 'Page Two Title',
                'id': 'page-2-url',
                'content': [
                    {
                        'name': 'ul',
                        'content': [
                            'Bullets',
                            'Without',
                            'Numbers. There is a 3rd point',
                        ]
                    },
                    {
                        'name': 'verbatim',
                        'content': [
'''
code
    indentend line of this
another
'''
                        ]
                    }
                ]
            },
        ],
    }

def test_multi():
    slider = Slider()

    data = slider.process_yml('cases/multi.yml')
    assert data == {}
