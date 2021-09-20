import subprocess
from bin.tools.color import Msg


def coredns(ip):
    Msg.warn("Start install coredns "+"="*20)
    subprocess.getstatusoutput(
        f"scp coredns.yml root@{ip}:/opt")

    subprocess.getoutput(
        f"ssh root@{ip} 'kubectl apply -f /opt/coredns.yml'")
    Msg.warn("End install coredns "+"="*20)
