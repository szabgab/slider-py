import os
from tools import compare_dirs

def test_other_dir(tmpdir):
    root = str(tmpdir)
    cwd = os.getcwd()
    os.chdir(root)
    from slider import Slider, SliderError
    slider = Slider()

    target_dir = os.path.join(root, 'html')
    os.mkdir(target_dir)
    pages = slider.parse(os.path.join(cwd, 'cases', 'all.md'))
    slider.generate_html_files(target_dir)
    compare_dirs(target_dir, os.path.join(cwd, 'cases', 'html', 'all'), 'all')

    data = slider.process_yml(os.path.join(cwd, 'cases', 'multi.yml'))
    assert data == {}


    os.chdir(cwd)
