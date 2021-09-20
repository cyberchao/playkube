import subprocess
import sys
from bin.tools.color import Msg


def calico(ip):
    Msg.warn("Start install caili "+"="*20)
    subprocess.getstatusoutput(
        f"scp calico.yml root@{ip}:/opt")

    subprocess.getoutput(
        f"ssh root@{ip} 'kubectl apply -f /opt/calico.yml'")
    Msg.warn("End install calico "+"="*20)
