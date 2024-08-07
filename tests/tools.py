import filecmp
import os
import json
from contextlib import contextmanager


def compare_dirs(left, right, name):
    print("Left: {} Right: {} name: {}".format(left, right, name))
    dcmp = filecmp.dircmp(left, right)
    #assert 'info.yaml' in dcmp.left_only, "info.yaml missing in '{}' test case".format(name)
    #assert dcmp.left_only == ['info.yaml'], 'some unexpected files were generated: ' + ', '.join(dcmp.left_only)
    assert dcmp.left_only == [], 'some unexpected files were generated: ' + ', '.join(dcmp.left_only)
    assert dcmp.right_only == [], 'some expected files were NOT generated'
    if dcmp.diff_files != []:
        for filename in dcmp.diff_files:
            print("diff {}/{} {}/{}".format(left, filename, right, filename))
    assert dcmp.diff_files == [], 'the content of some files is different. See the diff-lines in the output.'


# See https://code-maven.com/python-context-tools
@contextmanager
def cwd(path):
    oldpwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldpwd)


def read_expected(json_file):
    with open(json_file, 'r', encoding="utf-8") as fh:
        expected = json.load(fh)

    expected['pages'] = []
    for name in expected['files']:
        js_file = "cases/output/dom/{}.json".format(name[:-3])
        with open(js_file) as fh:
            expected['pages'].append(json.load(fh))
    return expected



