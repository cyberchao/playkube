import subprocess
import sys
from bin.tools.color import Msg


def controller_manager(hosts, kube_apiserver_url):
    Msg.warn('Start install kube-controller-manager ' + '='*20)
    for ip in hosts:
        status, output = subprocess.getstatusoutput(
            f"scp pkgs/kubernetes/server/bin/kube-controller-manager root@{ip}:/opt/kubernetes/bin")
        if status != 0:
            Msg.fail(
                f"scp  pkgs/kubernetes/server/bin/kube-controller-manager error [{ip}]:{output}")
        status, output = subprocess.getstatusoutput(
            f"scp tls/k8s/controller-manager/kube*.pem root@{ip}:/opt/kubernetes/controller")
        if status != 0:
            Msg.fail(f"scp kube-controller-manager.pem fail [{ip}]:{output}")
        cmd = f'''
cat > /opt/kubernetes/cfg/kube-controller-manager.conf << EOF
KUBE_CONTROLLER_MANAGER_OPTS="--logtostderr=false \\
--v=2 \\
--log-dir=/opt/kubernetes/logs \\
--leader-elect=true \\
--kubeconfig=/opt/kubernetes/cfg/kube-controller-manager.kubeconfig \\
--bind-address=127.0.0.1 \\
--allocate-node-cidrs=true \\
--cluster-cidr=10.244.0.0/16 \\
--service-cluster-ip-range=10.0.0.0/24 \\
--cluster-signing-cert-file=/opt/kubernetes/ssl/ca.pem \\
--cluster-signing-key-file=/opt/kubernetes/ssl/ca-key.pem  \\
--root-ca-file=/opt/kubernetes/ssl/ca.pem \\
--service-account-private-key-file=/opt/kubernetes/ssl/ca-key.pem \\
--cluster-signing-duration=87600h0m0s"
EOF
kubectl config set-cluster kubernetes \
  --certificate-authority=/opt/kubernetes/ssl/ca.pem \
  --embed-certs=true \
  --server={kube_apiserver_url} \
  --kubeconfig=/opt/kubernetes/cfg/kube-controller-manager.kubeconfig
kubectl config set-credentials kube-controller-manager \
  --client-certificate=/opt/kubernetes/controller/kube-controller-manager.pem \
  --client-key=/opt/kubernetes/controller/kube-controller-manager-key.pem \
  --embed-certs=true \
  --kubeconfig=/opt/kubernetes/cfg/kube-controller-manager.kubeconfig
kubectl config set-context default \
  --cluster=kubernetes \
  --user=kube-controller-manager \
  --kubeconfig=/opt/kubernetes/cfg/kube-controller-manager.kubeconfig
kubectl config use-context default --kubeconfig=/opt/kubernetes/cfg/kube-controller-manager.kubeconfig
# add systemd
cat > /usr/lib/systemd/system/kube-controller-manager.service << EOF
[Unit]
Description=Kubernetes Controller Manager
Documentation=https://github.com/kubernetes/kubernetes

[Service]
EnvironmentFile=/opt/kubernetes/cfg/kube-controller-manager.conf
ExecStart=/opt/kubernetes/bin/kube-controller-manager \$KUBE_CONTROLLER_MANAGER_OPTS
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# start
systemctl daemon-reload
systemctl stop kube-controller-manager
systemctl start kube-controller-manager
systemctl enable kube-controller-manager
'''
        status, output = subprocess.getstatusoutput(f"ssh root@{ip} '{cmd}'")
        if status != 0:
            Msg.fail(
                f"install kube-controller-manager.pem fail [{ip}]:{output}")

        if subprocess.getoutput(f"ssh root@{ip} 'systemctl status kube-controller-manager |grep running|wc -l'") == '1':
            Msg.success(f"kube-controller-manager start success [{ip}]")
            continue
        else:
            Msg.fail(
                f"kube-controller-manager start fail [{ip}]")
    Msg.warn('End install kube-controller-manager ' + '='*20)
