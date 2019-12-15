import json
import os
import sys
import subprocess
import yaml

from tools import compare_dirs, read_expected

def qx(cmd):
    proc = subprocess.Popen(cmd,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
    )
    out,err = proc.communicate()
    return out, err, proc.returncode


def test_cli_html(tmpdir):
    temp_dir = str(tmpdir)
    cmd = [sys.executable, "slider.py", "--md", "cases/all.md", "--html", "--dir",  temp_dir]
    out, err, code = qx(cmd)
    print(out)
    print(err)
    assert code == 0
    assert out == b''
    assert err == b''


def test_cli_empty():
    cmd = [sys.executable, "slider.py"]
    out, err, code = qx(cmd)
    #print(out)
    print(err)
    assert code == 0
    assert 'usage: slider.py' in out.decode('utf-8')
    assert err == b''


def test_cli_empty_parse():
    cmd = [sys.executable, "slider.py", '--parse']
    out, err, code = qx(cmd)
    #print(out)
    print(err)
    assert code == 1
    assert 'usage: slider.py' in out.decode('utf-8')
    assert '--md or --yaml is required' in out.decode('utf-8')
    assert err == b''


def test_cli_empty_html():
    cmd = [sys.executable, "slider.py", '--html']
    out, err, code = qx(cmd)
    #print(out)
    print(err)
    assert code == 1
    assert 'usage: slider.py' in out.decode('utf-8')
    assert '--dir was missing' in out.decode('utf-8')
    assert err == b''


def test_cli_empty_html_dir(tmpdir):
    temp_dir = str(tmpdir)
    cmd = [sys.executable, "slider.py", '--html', "--dir", temp_dir]
    out, err, code = qx(cmd)
    #print(out)
    print(err)
    assert code == 1
    assert 'usage: slider.py' in out.decode('utf-8')
    assert '--md or --yaml is required' in out.decode('utf-8')
    assert err == b''


def test_cli_empty_html_md():
    cmd = [sys.executable, "slider.py", '--html', "--md", "cases/all.md"]
    out, err, code = qx(cmd)
    #print(out)
    print(err)
    assert code == 1
    assert 'usage: slider.py' in out.decode('utf-8')
    assert '--dir was missing' in out.decode('utf-8')
    assert err == b''


def test_cli_parse():
    cmd = [sys.executable, "slider.py", "--md", "cases/all.md", "--parse"]
    out, err, code = qx(cmd)
    print(out)
    print(type(out))
    #print(err)
    assert code == 0
    assert err == b''
    data = json.loads(out.decode('utf8'))
    with open('cases/dom/all.json') as fh:
        expected = json.load(fh)
    assert data == expected


def test_cli_parse_yaml():
    yml_file = 'cases/multi.json'
    cmd = [sys.executable, "slider.py", "--yaml", yml_file, "--parse"]
    out, err, code = qx(cmd)
    print(out)
    print(err)
    assert code == 0
    assert err == b''
    data = json.loads(out.decode('utf-8'))

    expected = read_expected(yml_file)

    assert data == expected


def test_cli_html_yaml(tmpdir):
    temp_dir = str(tmpdir)
    yml_file = 'cases/multi.json'
    cmd = [sys.executable, "slider.py", "--yaml", yml_file, "--html", "--dir", temp_dir]
    out, err, code = qx(cmd)
    print(out)
    print(err)
    assert code == 0
    assert err == b''
    assert out == b''
    name = 'multi'
    compare_dirs(temp_dir, os.path.join('cases', 'multi_html', name), name)


def test_cli_html_yaml_ext(tmpdir):
    temp_dir = str(tmpdir)
    #print(temp_dir)
    yml_file = 'cases/multi.json'
    cmd = [sys.executable, "slider.py", "--yaml", yml_file, "--html", "--dir", temp_dir, '--ext', 'html']
    out, err, code = qx(cmd)
    print(out)
    print(err)
    assert code == 0
    assert err == b''
    assert out == b''
    name = 'multi'
    compare_dirs(temp_dir, os.path.join('cases', 'multi_html_ext', name), name)

