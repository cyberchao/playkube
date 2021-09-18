import subprocess
import sys
from jinja2 import Template
from bin.tools.color import Msg
'''
ETCDCTL_API=3 /opt/etcd/bin/etcdctl --cacert=/opt/etcd/ssl/ca.pem --cert=/opt/etcd/ssl/server.pem --key=/opt/etcd/ssl/server-key.pem --endpoints="https://10.0.0.21:2379,https://10.0.0.22:2379,https://10.0.0.23:2379" endpoint health --write-out=table 
'''


def etcd(hosts):
    Msg.warn('Start install etcd ' + '='*20)
    urls = list()
    for ip in hosts:
        urls.append(f'etcd-{hosts.index(ip)+1}=https://{ip}:2380')
    cluster = ','.join(urls)
    for ip in hosts:
        conf = f'''
rm -rf /var/lib/etcd/default.etcd
# etcd.conf
cat > /opt/etcd/cfg/etcd.conf << EOF
#[Member]
ETCD_NAME="etcd-{hosts.index(ip)+1}"
ETCD_DATA_DIR="/var/lib/etcd/default.etcd"
ETCD_LISTEN_PEER_URLS="https://{ip}:2380"
ETCD_LISTEN_CLIENT_URLS="https://{ip}:2379"
#[Clustering]
ETCD_INITIAL_ADVERTISE_PEER_URLS="https://{ip}:2380"
ETCD_ADVERTISE_CLIENT_URLS="https://{ip}:2379"
ETCD_INITIAL_CLUSTER="{cluster}"
ETCD_INITIAL_CLUSTER_TOKEN="etcd-cluster"
ETCD_INITIAL_CLUSTER_STATE="new"
EOF
# add systemd
cat > /usr/lib/systemd/system/etcd.service << EOF
[Unit]
Description=Etcd Server
After=network.target
After=network-online.target
Wants=network-online.target
[Service]
Type=notify
EnvironmentFile=/opt/etcd/cfg/etcd.conf
ExecStart=/opt/etcd/bin/etcd \
--cert-file=/opt/etcd/ssl/server.pem \
--key-file=/opt/etcd/ssl/server-key.pem \
--peer-cert-file=/opt/etcd/ssl/server.pem \
--peer-key-file=/opt/etcd/ssl/server-key.pem \
--trusted-ca-file=/opt/etcd/ssl/ca.pem \
--peer-trusted-ca-file=/opt/etcd/ssl/ca.pem \
--logger=zap
Restart=on-failure
LimitNOFILE=65536
[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload 
systemctl stop etcd
systemctl start etcd
systemctl enable etcd
    '''
        cmd = f'''
                ssh root@{ip} 'mkdir /opt/etcd/{{bin,cfg,ssl}} -p'
                scp pkgs/etcd-v3.4.14-linux-amd64/{{etcd,etcdctl}} root@{ip}:/opt/etcd/bin/
                scp tls/etcd/ca*pem tls/etcd/server*pem root@{ip}:/opt/etcd/ssl/
                ssh root@{ip} '{conf.replace('{ip}',ip)}'
                '''
        subprocess.getoutput(cmd)
        # subprocess.Popen(
        #    cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    Msg.warn(f'End install etcd')
