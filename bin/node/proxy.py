import subprocess
import sys
from bin.tools.color import Msg


def proxy(ip, kube_apiserver_url):
    Msg.warn("Start install kube-proxy "+"="*20)
    status, output = subprocess.getstatusoutput(
        f"scp tls/k8s/proxy/kube*.pem root@{ip}:/opt/kubernetes/proxy")
    if status != 0:
        Msg.fail(f"scp tls/k8s/proxy/kube*.pem fail [{ip}]:{output}")
    status, output = subprocess.getstatusoutput(
        f"scp pkgs/kubernetes/server/bin/kube-proxy root@{ip}:/opt/kubernetes/bin")
    if status != 0:
        if "Text file busy" not in output:
            Msg.fail(
                f"scp pkgs/kubernetes/server/bin/kube-proxy fail [{ip}]:{output}")

    cmd = f'''
cat > /opt/kubernetes/cfg/kube-proxy.conf << EOF
KUBE_PROXY_OPTS="--logtostderr=false \\
--v=2 \\
--log-dir=/opt/kubernetes/logs \\
--config=/opt/kubernetes/cfg/kube-proxy-config.yml"
EOF

cat > /opt/kubernetes/cfg/kube-proxy-config.yml << EOF
kind: KubeProxyConfiguration
apiVersion: kubeproxy.config.k8s.io/v1alpha1
bindAddress: 0.0.0.0
metricsBindAddress: 0.0.0.0:10249
clientConnection:
  kubeconfig: /opt/kubernetes/cfg/kube-proxy.kubeconfig
hostnameOverride: {ip}
clusterCIDR: 10.244.0.0/16
EOF

kubectl config set-cluster kubernetes \
  --certificate-authority=/opt/kubernetes/ssl/ca.pem \
  --embed-certs=true \
  --server={kube_apiserver_url} \
  --kubeconfig=/opt/kubernetes/cfg/kube-proxy.kubeconfig
kubectl config set-credentials kube-proxy \
  --client-certificate=/opt/kubernetes/proxy/kube-proxy.pem \
  --client-key=/opt/kubernetes/proxy/kube-proxy-key.pem \
  --embed-certs=true \
  --kubeconfig=/opt/kubernetes/cfg/kube-proxy.kubeconfig
kubectl config set-context default \
  --cluster=kubernetes \
  --user=kube-proxy \
  --kubeconfig=/opt/kubernetes/cfg/kube-proxy.kubeconfig
kubectl config use-context default --kubeconfig=/opt/kubernetes/cfg/kube-proxy.kubeconfig

cat > /usr/lib/systemd/system/kube-proxy.service << EOF
[Unit]
Description=Kubernetes Proxy
After=network.target

[Service]
EnvironmentFile=/opt/kubernetes/cfg/kube-proxy.conf
ExecStart=/opt/kubernetes/bin/kube-proxy \$KUBE_PROXY_OPTS
Restart=on-failure
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl stop kube-proxy
systemctl start kube-proxy
systemctl enable kube-proxy
'''
    status, output = subprocess.getstatusoutput(f"ssh root@{ip} '{cmd}'")
    if status != 0:
        Msg.fail(f"install kube-proxy fail [{ip}]:{output}")
    if subprocess.getoutput(f"ssh root@{ip} 'systemctl status kube-proxy |grep running|wc -l'") == '1':
        Msg.success(f"[{ip}]:kube-proxy start success")
    else:
        Msg.fail(f"[{ip}]:kube-proxy start fail")
    Msg.warn("End install kube-proxy "+"="*20)
