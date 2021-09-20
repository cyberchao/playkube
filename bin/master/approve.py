import subprocess
import time
from bin.tools.color import Msg


def approve(ip):
    time.sleep(5)
    Msg.warn('Start approve node ' + '='*20)
    nodeids = subprocess.getoutput(
        f"ssh root@{ip} \"kubectl get csr|grep Pending |cut -f 1 -d ' '\"").split('\n')
    print(nodeids)
    for id in nodeids:
        out = subprocess.getoutput(
            f"ssh root@{ip} \"kubectl certificate approve {id}\"")
        print(out)
        Msg.success('Approve node ok ')
    time.sleep(5)
    Msg.warn('End approve node ' + '='*20)
