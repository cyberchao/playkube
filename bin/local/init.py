import sys, os
import subprocess
import pexpect
from bin.tools.color import Msg

RSAPATH = '/root/.ssh/id_rsa'

def init():
    cwd = os.getcwd()
    cmd = f'''
find tls/ ! -name '*.json*' -type f |xargs rm -f
cp {cwd}/pkgs/cfssl /usr/bin/cfssl
cp {cwd}/pkgs/cfssljson /usr/bin/cfssljson
cp {cwd}/pkgs/cfssl-certinfo /usr/bin/cfssl-certinfo
'''
    subprocess.getoutput(cmd)

class PreInstall():
    def __init__(self, server, rootpass):
        self.server = server
        self.rootpass = rootpass

    @staticmethod
    def create_id():
        ##create id
        if not os.path.exists(RSAPATH):
            status, output = subprocess.getstatusoutput(f"ssh-keygen -b 2048 -t rsa -f {RSAPATH} -q -N ''")
            if status == 0:
                Msg.success("Create local ssh key files successfully.")
            else:
                Msg.fail(f'Create local ssh key files failed: {output}')
        else:
            Msg.warn('Local ssh key files already exist.')

    def __copy_id(self):
        try:
            cmd_copyid = "ssh-copy-id -i {0} {1}".format(RSAPATH + '.pub', self.server)
            child_copyid = pexpect.spawn(cmd_copyid)
            index_copyid = child_copyid.expect(['password:', pexpect.EOF], timeout=5)
            if index_copyid == 0:
                child_copyid.sendline(self.rootpass)
                index_copyid = child_copyid.expect(['password:', pexpect.EOF], timeout=5)
                if index_copyid == 0:
                    Msg.fail('The root password is not correct!')
                child_copyid.close()
                Msg.success('Copy ssh id to {0} successfully.'.format(self.server))
            else:
                Msg.fail('{0}.{1} fatal error'.format(self.__class__.__name__, sys._getframe().f_code.co_name))
        except Exception as e:
            Msg.fail(e)

    def ssh_nopass(self):
        try:
            ##copy id
            cmd_checkssh = "ssh -o ConnectTimeout=5 {0} -o PasswordAuthentication=no -i {1} 'uptime'".format(self.server, RSAPATH)
            child_checkssh = pexpect.spawn(cmd_checkssh)
            index_checkssh = child_checkssh.expect(['continue connecting', 'Connection timed out', 'Permission denied', 'load average', pexpect.EOF])
            if index_checkssh == 0:
                child_checkssh.sendline('yes')
                index_checkssh_2 = child_checkssh.expect(['Permission denied', 'load average'])
                if index_checkssh_2 == 0:
                    child_checkssh.close()
                    self.__copy_id()
                elif index_checkssh_2 == 1:
                    Msg.success('Ssh check ok: {0}'.format(self.server))
                else:
                    Msg.fail('{0}.{1} fatal error'.format(self.__class__.__name__, sys._getframe().f_code.co_name))
            elif index_checkssh == 1:
                Msg.fail('Server can not be connect: {0}'.format(self.server))
            elif index_checkssh == 2:
                self.__copy_id()
            elif index_checkssh == 3:
                Msg.success('Ssh check ok: {0}'.format(self.server))
            else:
                Msg.fail('{0}.{1} fatal error'.format(self.__class__.__name__, sys._getframe().f_code.co_name))
        except Exception as e:
            Msg.fail("{0}.{1} fatal error: {2}".format(self.__class__.__name__, sys._getframe().f_code.co_name, str(e)))
