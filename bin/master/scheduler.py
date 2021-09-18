import subprocess
import sys
from bin.tools.color import Msg


def scheduler(master):
    Msg.warn('Start install kube-scheduler ' + '='*20)
    for ip in master:
        status, output = subprocess.getstatusoutput(
            f"scp tls/k8s/scheduler/kube*.pem root@{ip}:/opt/kubernetes/scheduler")
        if status != 0:
            Msg.fail(f"{ip} scp tls/k8s/scheduler/kube*.pem error:{output}")
        cmd = f'''
cat > /opt/kubernetes/cfg/kube-scheduler.conf << EOF
KUBE_SCHEDULER_OPTS="--logtostderr=false \\
--v=2 \\
--log-dir=/opt/kubernetes/logs \\
--leader-elect \\
--kubeconfig=/opt/kubernetes/cfg/kube-scheduler.kubeconfig \\
--bind-address=0.0.0.0"
EOF

kubectl config set-cluster kubernetes \
  --certificate-authority=/opt/kubernetes/ssl/ca.pem \
  --embed-certs=true \
  --server=https://{ip}:6443 \
  --kubeconfig=/opt/kubernetes/cfg/kube-scheduler.kubeconfig
kubectl config set-credentials kube-scheduler \
  --client-certificate=/opt/kubernetes/scheduler/kube-scheduler.pem \
  --client-key=/opt/kubernetes/scheduler/kube-scheduler-key.pem \
  --embed-certs=true \
  --kubeconfig=/opt/kubernetes/cfg/kube-scheduler.kubeconfig
kubectl config set-context default \
  --cluster=kubernetes \
  --user=kube-scheduler \
  --kubeconfig=/opt/kubernetes/cfg/kube-scheduler.kubeconfig
kubectl config use-context default --kubeconfig=/opt/kubernetes/cfg/kube-scheduler.kubeconfig

cat > /usr/lib/systemd/system/kube-scheduler.service << EOF
[Unit]
Description=Kubernetes Scheduler
Documentation=https://github.com/kubernetes/kubernetes

[Service]
EnvironmentFile=/opt/kubernetes/cfg/kube-scheduler.conf
ExecStart=/opt/kubernetes/bin/kube-scheduler \$KUBE_SCHEDULER_OPTS
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl stop kube-scheduler
systemctl start kube-scheduler
systemctl enable kube-scheduler
'''
        status, output = subprocess.getstatusoutput(f"ssh root@{ip} '{cmd}'")
        if status != 0:
            Msg.fail(f"{ip}:install kube-scheduler fail:{output}")
        if subprocess.getoutput(f"ssh root@{ip} 'systemctl status kube-scheduler |grep running|wc -l'") == '1':
            Msg.success(f"{ip}:kube-scheduler start success")
            continue
        else:
            Msg.fail(f"{ip}:kube-scheduler start fail")
    Msg.warn('End install kube-scheduler ' + '='*20)
