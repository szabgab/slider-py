import json
import sys
import subprocess

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



def test_cli_parse(tmpdir):
    temp_dir = str(tmpdir)
    cmd = [sys.executable, "slider.py", "--md", "cases/all.md", "--parse"]
    out, err, code = qx(cmd)
    #print(out)
    #print(err)
    assert code == 0
    assert err == b''
    data = json.loads(out)
    with open('cases/dom/all.json') as fh:
        expected = json.load(fh)
    assert data == expected


