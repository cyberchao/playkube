import subprocess
import os


def init():
    cwd = os.getcwd()
    cmd = f'''
cp {cwd}/pkgs/cfssl /usr/bin/cfssl
cp {cwd}/pkgs/cfssljson /usr/bin/cfssljson
cp {cwd}/pkgs/cfssl-certinfo /usr/bin/cfssl-certinfo
'''
    subprocess.getoutput(cmd)
