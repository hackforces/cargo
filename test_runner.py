import docker
client = docker.from_env()

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

class testAppFunctions(unittest.TestCase):
    lang  = ['python', 'go', 'php', 'nodejs', 'c', 'c++', 'java', 'ruby', 'rust']
    dbms  = ['mysql', 'postgresql', 'mongodb']
    os    = ['ubuntu', 'debian', 'arch', 'centos']
    outf  = ""

    # @patch('builtins.input', side_effect=['\n', 'test/ /var/www/html', 'root', '1234', 'testdb'])
    def test_build(self):
        inp = ['\n', 'test/ /var/www/html\n', 'root\n', '1234\n', 'testdb\n']
        strings = []
        tmp_cmd = "python docker_generator.py"
        tmp_os = "-o " + random.choice(self.os)
        tmp_ln = "-l " + random.choice(self.lang)
        tmp_db = "-db " + random.choice(self.dbms)
        tmp_ports = "-p "
        for i in range(4):
            tmp_ports += str(random.randint(1, 65535)) + ","
        tmp_remote = "-s 1234 -t 5678"
        tmp_dir = "-a os/ /var/www/html"

        strings.append(tmp_cmd)
        strings.append(tmp_os)
        strings.append(tmp_ln)
        strings.append(tmp_db)
        strings.append(tmp_ports)
        # strings.append(tmp_remote)
        # strings.append(tmp_dir)

        request = ' '.join(strings)
        print(request)
        p = subprocess.Popen(request, stdin=PIPE, stdout=PIPE, shell=True)
        try:
            outs, errs = p.communicate(input=inp, timeout=15)
            # for i in inp:
            #     p.stdout.read()
            #     p.stdin.write(i)
        except TimeoutExpired:
            p.kill()
            outs, errs = p.communicate()


if __name__ == '__main__':
    unittest.main(verbosity=2)
