import os
import sys
import json
from tools import compare_dirs, cwd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from slider import Slider, SliderError, HTML

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
            filename  = md_file,
        )

        html.generate_html_files(target_dir)
        compare_dirs(target_dir, os.path.join(original, 'cases', 'html', 'all'), 'all')

        data = slider.process_yml(os.path.join(original, 'cases', 'multi.yml'))
        assert data == {}
