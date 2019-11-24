import sys
import subprocess

def qx(cmd):
    proc = subprocess.Popen(cmd,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
    )
    out,err = proc.communicate()
    return out, err, proc.returncode

def test_cli(tmpdir):
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
    print(out)
    print(err)
    assert code == 0
    assert 'usage: slider.py' in out.decode('utf-8')
    assert err == b''

def test_cli_empty_parse():
    cmd = [sys.executable, "slider.py", '--parse']
    out, err, code = qx(cmd)
    print(out)
    print(err)
    assert code == 1
    assert 'usage: slider.py' in out.decode('utf-8')
    assert '--md was missing' in out.decode('utf-8')
    assert err == b''

