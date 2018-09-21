import filecmp
import os

def compare_dirs(left, right, name):
    dcmp = filecmp.dircmp(left, right)
    assert dcmp.left_only == [], 'some unexpected files were generated'
    assert dcmp.right_only == [], 'some expected files were NOT generated'
    if dcmp.diff_files != []:
        for filename in dcmp.diff_files:
            print("diff {}/{} {}/{}".format(left, filename, right, filename))
    assert dcmp.diff_files == [], 'the content of some files is different. See the diff-lines in the output.'
