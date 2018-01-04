import pytest
from slider import Slider, SliderError

def test_chapter():
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


    pages = slider.parse('cases/chapter.md')
    assert pages == {
        'title' : 'Chapter Title',
        'id'    : 'chapter-path',
        'pages' : [],
    }
    assert slider.generate_html() == [{'html': '<h1>Chapter Title</h1>', 'id': 'chapter-path'}]


def test_pages():
    slider = Slider()
    pages = slider.parse('cases/pages.md')
    assert pages == {
        'title' : 'Chapter Title',
        'id'    : 'chapter-url',
        'pages' : [
            {
                'title' : 'Page One Title',
                'id'    : 'page-1-url',
            },
            {
                'title': 'Page Two Title',
                'id': 'page-2-url',
            },
        ],
    }

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
