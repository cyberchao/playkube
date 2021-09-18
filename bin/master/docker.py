import subprocess
import sys
from bin.tools.color import Msg


def docker(hosts):
    Msg.warn('Start install docker ' + '='*20)
    cmd = '''
cat > /usr/lib/systemd/system/docker.service << EOF
[Unit]
Description=Docker Application Container Engine
Documentation=https://docs.docker.com
After=network-online.target firewalld.service
Wants=network-online.target
[Service]
Type=notify
ExecStart=/usr/bin/dockerd
ExecReload=/bin/kill -s HUP $MAINPID
LimitNOFILE=infinity
LimitNPROC=infinity
LimitCORE=infinity
TimeoutStartSec=0
Delegate=yes
KillMode=process
Restart=on-failure
StartLimitBurst=3
StartLimitInterval=60s
[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl stop docker
systemctl start docker
systemctl enable docker

'''
    for ip in hosts:
        subprocess.getstatusoutput(
            f"scp pkgs/docker/* root@{ip}:/usr/bin")
        status, output = subprocess.getstatusoutput(f"ssh root@{ip} '{cmd}'")
        if status != 0:
            Msg.fail(f'{ip} install docker fail:{output}')
        if subprocess.getoutput(f"ssh root@{ip} 'systemctl status docker |grep running|wc -l'") == '1':
            Msg.success(f"{ip}:docker start success")
            continue
        else:
            Msg.fail(f"{ip}:docker start fail")
    Msg.warn('End install docker ')
