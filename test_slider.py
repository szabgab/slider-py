import pytest
import slider

def test_parser():
    with pytest.raises(Exception) as exinfo:
        slider.parse('cases/no-chapter-title.md')
    assert exinfo.type == slider.SliderError
    assert str(exinfo.value) == 'Chapter title is missing from cases/no-chapter-title.md'


    with pytest.raises(Exception) as exinfo:
        slider.parse('cases/no-chapter-id.md')
    assert exinfo.type == slider.SliderError
    assert str(exinfo.value) == 'Chapter id is missing from cases/no-chapter-id.md'


    assert slider.parse('cases/chapter.md') == {
        'title' : 'Chapter Title',
        'id'    : 'chapter-path'
    }
