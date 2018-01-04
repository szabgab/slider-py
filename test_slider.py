import pytest
import slider

def test_parser():
    with pytest.raises(Exception) as exinfo:
        slider.parse('cases/no-chapter-title.md')
    assert exinfo.type == slider.SliderError
    assert str(exinfo.value) == 'Chapter title is missing from cases/no-chapter-title.md'

    assert slider.parse('cases/chapter.md') == {
        'title' : 'Chapter Title'
    }
