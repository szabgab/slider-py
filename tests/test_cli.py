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

