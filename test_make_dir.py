import os

def make_directory_test(tmpdir):
    root = str(tmpdir)
    target_dir = os.path.join(root, 'abcd')
    generate_html_files(self, target_dir)
    assert os.path.exists(target_dir) == 1
