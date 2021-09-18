import subprocess
import sys
from bin.tools.color import Msg


def system_init(ip):
    Msg.warn(f'Start system init [{ip}]' + '='*20)
    status, output = subprocess.getstatusoutput(
        f"ssh root@{ip} \"sed -i 's/enforcing/disabled/' /etc/selinux/config\"")
    if status != 0:
        Msg.fail(f"{ip}:init fail:{output}")
    status, output = subprocess.getstatusoutput(
        f"ssh root@{ip} \"sed -ri 's/.*swap.*/#&/' /etc/fstab\"")
    if status != 0:
        Msg.fail(f"{ip}:init fail:{output}")

    cmd = r'''# 关闭防火墙
systemctl stop firewalld
systemctl disable firewalld
setenforce 0
swapoff -a
# 将桥接的IPv4流量传递到iptables的链
cat > /etc/sysctl.d/k8s.conf << EOF
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
EOF
sysctl --system
mkdir -p /opt/kubernetes/{bin,cfg,ssl,logs,admin,controller,scheduler}
mkdir -p /root/.kube
'''
    status, output = subprocess.getstatusoutput(f"ssh root@{ip} '{cmd}'")
    if status != 0:
        Msg.fail(f'System init fail [{ip}]:{output}')
    Msg.success(f'System init success [{ip}]')
    Msg.warn('End System init')
