import subprocess
import time


def approve(ip):
    time.sleep(5)

    nodeids = subprocess.getoutput(
        f"ssh root@{ip} \"kubectl get csr|grep Pending |cut -f 1 -d ' '\"").split('\n')
    print(nodeids)
    for id in nodeids:
        out = subprocess.getoutput(
            f"ssh root@{ip} \"kubectl certificate approve {id}\"")
        print(out)

    time.sleep(5)


approve('10.0.0.21')
