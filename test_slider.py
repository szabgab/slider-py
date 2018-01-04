import slider

def test_parser():
    assert slider.parse('cases/chapter.md') == {
        'title' : 'Chapter Title'
    }
