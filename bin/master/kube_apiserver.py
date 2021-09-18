import subprocess
import sys
from bin.tools.color import Msg


def apiserver(master):
    Msg.warn('Start install kube-apiserver ' + '='*20)
    urls = list()
    for ip in master:
        urls.append(f'https://{ip}:2379')
    etcd_servers = ','.join(urls)

    for ip in master:
        status, out = subprocess.getstatusoutput(
            f"scp pkgs/kubernetes/server/bin/{{kube-apiserver,kube-scheduler,kube-controller-manager}} root@{ip}:/opt/kubernetes/bin")
        subprocess.getstatusoutput(
            f"scp pkgs/kubernetes/server/bin/kubectl root@{ip}:/usr/local/bin/")
        subprocess.getstatusoutput(
            f"scp tls/k8s/ca*pem tls/k8s/apiserver/server*pem root@{ip}:/opt/kubernetes/ssl/")
        cmd = f'''
cat > /opt/kubernetes/cfg/kube-apiserver.conf << EOF
KUBE_APISERVER_OPTS="--logtostderr=false \\
--v=2 \\
--log-dir=/opt/kubernetes/logs \\
--etcd-servers={etcd_servers} \\
--bind-address={ip} \\
--secure-port=6443 \\
--advertise-address={ip} \\
--allow-privileged=true \\
--service-cluster-ip-range=10.254.0.0/16 \\
--enable-admission-plugins=NamespaceLifecycle,LimitRanger,ServiceAccount,ResourceQuota,NodeRestriction \\
--authorization-mode=RBAC,Node \\
--enable-bootstrap-token-auth=true \\
--token-auth-file=/opt/kubernetes/cfg/token.csv \\
--service-node-port-range=30000-32767 \\
--kubelet-client-certificate=/opt/kubernetes/ssl/server.pem \\
--kubelet-client-key=/opt/kubernetes/ssl/server-key.pem \\
--tls-cert-file=/opt/kubernetes/ssl/server.pem  \\
--tls-private-key-file=/opt/kubernetes/ssl/server-key.pem \\
--client-ca-file=/opt/kubernetes/ssl/ca.pem \\
--service-account-key-file=/opt/kubernetes/ssl/ca-key.pem \\
--service-account-issuer=api \\
--service-account-signing-key-file=/opt/kubernetes/ssl/server-key.pem \\
--etcd-cafile=/opt/etcd/ssl/ca.pem \\
--etcd-certfile=/opt/etcd/ssl/server.pem \\
--etcd-keyfile=/opt/etcd/ssl/server-key.pem \\
--requestheader-client-ca-file=/opt/kubernetes/ssl/ca.pem \\
--proxy-client-cert-file=/opt/kubernetes/ssl/server.pem \\
--proxy-client-key-file=/opt/kubernetes/ssl/server-key.pem \\
--requestheader-allowed-names=kubernetes \\
--requestheader-extra-headers-prefix=X-Remote-Extra- \\
--requestheader-group-headers=X-Remote-Group \\
--requestheader-username-headers=X-Remote-User \\
--enable-aggregator-routing=true \\
--audit-log-maxage=30 \\
--audit-log-maxbackup=3 \\
--audit-log-maxsize=100 \\
--audit-log-path=/opt/kubernetes/logs/k8s-audit.log"
EOF
cat > /usr/lib/systemd/system/kube-apiserver.service << EOF
[Unit]
Description=Kubernetes API Server
Documentation=https://github.com/kubernetes/kubernetes
[Service]
EnvironmentFile=/opt/kubernetes/cfg/kube-apiserver.conf
ExecStart=/opt/kubernetes/bin/kube-apiserver \$KUBE_APISERVER_OPTS
Restart=on-failure
[Install]
WantedBy=multi-user.target
EOF
'''
        status, output = subprocess.getstatusoutput(f"ssh root@{ip} '{cmd}'")
        if status != 0:
            Msg.fail(f"write apiserver config error [{ip}]:{output}")
        #  启用 TLS Bootstrapping 机制自动签发证书
        cmd = '''
cat > /opt/kubernetes/cfg/token.csv << EOF
c47ffb939f5ca36231d9e3121a252940,kubelet-bootstrap,10001,"system:node-bootstrapper"
EOF
systemctl daemon-reload
systemctl stop kube-apiserver
systemctl start kube-apiserver
systemctl enable kube-apiserver
'''
        status, output = subprocess.getstatusoutput(f"ssh root@{ip} '{cmd}'")
        if status != 0:
            Msg.fail(f"start apiserver fail [{ip}]:{output}")
        if subprocess.getoutput(f"ssh root@{ip} 'systemctl status kube-apiserver |grep running|wc -l'") == '1':
            Msg.success(f"kube-apiserver start success [{ip}]")
            continue
        else:
            Msg.fail(f"kube-apiserver start fail [{ip}]")
    Msg.warn('End install kube-apiserver ')
