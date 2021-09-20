import subprocess
import time
from bin.tools.color import Msg


def approve(ip):
    time.sleep(5)
    Msg.warn('Start approve node ' + '='*20)
    nodeids = subprocess.getoutput(
        f"ssh root@{ip} \"kubectl get csr|grep Pending|grep -v found |cut -f 1 -d ' '\"").split('\n')
    print(nodeids)
    if len(nodeids) == 0:
        Msg.warn('No pending node found ')
        return
    for id in nodeids:
        out = subprocess.getoutput(
            f"ssh root@{ip} \"kubectl certificate approve {id}\"")
        print(out)
        Msg.success('Approve node ok ')
    time.sleep(5)
    Msg.warn('End approve node ' + '='*20)
