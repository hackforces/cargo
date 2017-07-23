import docker
from docker import APIClient
# client = docker.from_env()
client = APIClient(base_url='unix://var/run/docker.sock')

import unittest
from unittest.mock import patch
import random
import string
import subprocess
from subprocess import PIPE

def selectOs(os):
    if os.lower() in ["ubuntu", "debian"]:
        return "apt-get -qq -y install"
    elif os is "arch":
        return "pacman -S"
    elif os is "centos":
        return "yum"
    else:
        return None

lang  = ['python', 'go', 'php', 'nodejs', 'c', 'c++', 'java', 'ruby', 'rust']
dbms  = ['mysql', 'postgresql', 'mongodb']
os    = ['ubuntu', 'debian']
outf  = ""
# inp = ['\n', '\n', 'test/ /var/www/html\n', 'root\n', '1234\n', 'testdb\n']
inp = '\n\ntest/ /var/www/html\nroot\n1234\ntestdb\n'
strings = []
tmp_path = "--path ~/buffer"
tmp_cmd = "python docker_generator.py"
tmp_os = "-o " + random.choice(os)
tmp_ln = "-l " + random.choice(lang)
tmp_db = "-db " + random.choice(dbms)
tmp_ports = "-p " + ','.join(str(random.randint(1, 65535)) for x in range(5))
tmp_remote = "-s 1234 -t 5678"
tmp_dir = "-a os/ /var/www/html"

strings.append(tmp_cmd)
strings.append(tmp_path)
strings.append(tmp_os)
strings.append(tmp_ln)
strings.append(tmp_db)
strings.append(tmp_ports)
strings.append(tmp_remote)
# strings.append(tmp_dir)

inp = "\n"
if "rust" in tmp_ln:
    inp = ""
if "c++" in tmp_ln:
    inp += "\n"

inp += '\ntest/ /var/www/html\nroot\n1234\ntestdb\n'

request = ' '.join(strings)
print(request)
p = subprocess.Popen(request, stdin=PIPE, stdout=PIPE, shell=True)
try:
    outs, errs = p.communicate(input=inp.encode(), timeout=15)
    # print (str(outs))
    p.kill()
except:
    p.kill()

try:
    # client.containers.list()
    response = [line for line in client.build(
        path='.', tag='docker/test'
    )]
    for i in response:
        print (i.decode("utf-8"))
    if "successful" in response:
        print("BUILD: successful!")
    else:
        print("BUILD: error!")

    # client.build(path='.', nocache=True, tag="docker/test")
except Exception as ex:
    print("BUILD: failed!")
    print (ex)
