import os
import sys
import json
import yaml
from tools import compare_dirs, cwd, read_expected

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from slider import MultiSlider, Slider, SliderError, HTML


def test_other_dir(tmpdir):
    root = str(tmpdir)
    original = os.getcwd()
    with cwd(root):
        slider = Slider()

        target_dir = os.path.join(root, 'html')
        os.mkdir(target_dir)
        md_file = os.path.join(original, 'cases', 'all.md')
        pages = slider.parse(md_file)
        with open(os.path.join(original, 'cases/dom/all.json')) as fh:
            expected = json.load(fh)
        assert expected == pages

        html = HTML(
            chapter   = pages,
            includes  = os.path.dirname(md_file),
            ext       = 'html',
        )

        html.generate_html_files(target_dir)
        compare_dirs(target_dir, os.path.join(original, 'cases', 'html', 'all'), 'all')


def test_other_dir_multi(tmpdir):
    root = str(tmpdir)
    original = os.getcwd()

    yml_file = os.path.join(original, 'cases', 'multi.json')

    expected = read_expected(yml_file)

    with cwd(root):
        multi_slider = MultiSlider()
        data = multi_slider.process_yml(yml_file)
        assert data == expected

