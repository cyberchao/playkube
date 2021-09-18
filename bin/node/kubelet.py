import subprocess
import sys
from bin.tools.color import Msg


def kubelet(ip, kube_apiserver_url):
    Msg.warn("start install kubelet "+"="*20)
    subprocess.getoutput(
        f"ssh root@{ip} 'mkdir -p /opt/kubernetes/{{proxy,bin,cfg,ssl,logs}}'")
    status, output = subprocess.getstatusoutput(
        f"scp pkgs/kubernetes/server/bin/kubelet root@{ip}:/opt/kubernetes/bin")
    if status != 0:
        if "Text file busy" not in output:
            Msg.fail(f"scp kubelet fail [{ip}]:{output}")
    cmd = f'''
cat > /opt/kubernetes/cfg/kubelet.conf << EOF
KUBELET_OPTS="--logtostderr=false \\
--v=2 \\
--log-dir=/opt/kubernetes/logs \\
--hostname-override={ip} \\
--network-plugin=cni \\
--kubeconfig=/opt/kubernetes/cfg/kubelet.kubeconfig \\
--bootstrap-kubeconfig=/opt/kubernetes/cfg/bootstrap.kubeconfig \\
--config=/opt/kubernetes/cfg/kubelet-config.yml \\
--cert-dir=/opt/kubernetes/ssl \\
--pod-infra-container-image=lizhenliang/pause-amd64:3.0"
EOF

cat > /opt/kubernetes/cfg/kubelet-config.yml << EOF
kind: KubeletConfiguration
apiVersion: kubelet.config.k8s.io/v1beta1
address: 0.0.0.0
port: 10250
readOnlyPort: 10255
cgroupDriver: cgroupfs
clusterDNS:
- 10.0.0.2
clusterDomain: cluster.local 
failSwapOn: false
authentication:
  anonymous:
    enabled: false
  webhook:
    cacheTTL: 2m0s
    enabled: true
  x509:
    clientCAFile: /opt/kubernetes/ssl/ca.pem 
authorization:
  mode: Webhook
  webhook:
    cacheAuthorizedTTL: 5m0s
    cacheUnauthorizedTTL: 30s
evictionHard:
  imagefs.available: 15%
  memory.available: 100Mi
  nodefs.available: 10%
  nodefs.inodesFree: 5%
maxOpenFiles: 1000000
maxPods: 110
EOF

kubectl config set-cluster kubernetes \
  --certificate-authority=/opt/kubernetes/ssl/ca.pem \
  --embed-certs=true \
  --server={kube_apiserver_url} \
  --kubeconfig=/opt/kubernetes/cfg/bootstrap.kubeconfig
kubectl config set-credentials "kubelet-bootstrap" \
  --token=c47ffb939f5ca36231d9e3121a252940 \
  --kubeconfig=/opt/kubernetes/cfg/bootstrap.kubeconfig
kubectl config set-context default \
  --cluster=kubernetes \
  --user="kubelet-bootstrap" \
  --kubeconfig=/opt/kubernetes/cfg/bootstrap.kubeconfig
kubectl config use-context default --kubeconfig=/opt/kubernetes/cfg/bootstrap.kubeconfig

cat > /usr/lib/systemd/system/kubelet.service << EOF
[Unit]
Description=Kubernetes Kubelet
After=docker.service

[Service]
EnvironmentFile=/opt/kubernetes/cfg/kubelet.conf
ExecStart=/opt/kubernetes/bin/kubelet \$KUBELET_OPTS
Restart=on-failure
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl stop kubelet
systemctl start kubelet
systemctl enable kubelet

'''
    status, output = subprocess.getstatusoutput(f"ssh root@{ip} '{cmd}'")
    if status != 0:
        Msg.fail(f"install kubelet fail [{ip}]:{output}")
    if subprocess.getoutput(f"ssh root@{ip} 'systemctl status kubelet |grep running|wc -l'") == '1':
        Msg.success(f"kubelet start success [{ip}]")
    else:
        Msg.fail(f"start kubelet fail [{ip}]")
    Msg.warn("End install kubelet")
