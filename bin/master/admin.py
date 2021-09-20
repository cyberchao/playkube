import subprocess
import sys
from bin.tools.color import Msg


def admin(master, kube_apiserver_url):
    Msg.warn('Start install kubeconfig ' + '='*20)
    for ip in master:
        status, output = subprocess.getstatusoutput(
            f"scp pkgs/kubernetes/server/bin/kubectl root@{ip}:/usr/local/bin/")
        if status != 0:
            Msg.fail(
                f"scp  pkgs/kubernetes/server/bin/kubectl error [{ip}]:{output}")
        status, output = subprocess.getstatusoutput(
            f"scp tls/k8s/admin/admin*pem root@{ip}:/opt/kubernetes/admin/")
        if status != 0:
            Msg.fail(f"scp admin.pem fail [{ip}]:{output}")
        cmd = f'''
              kubectl config set-cluster kubernetes \
                --certificate-authority=/opt/kubernetes/ssl/ca.pem \
                --embed-certs=true \
                --server={kube_apiserver_url} \
                --kubeconfig=/root/.kube/config
              kubectl config set-credentials cluster-admin \
                --client-certificate=/opt/kubernetes/admin/admin.pem \
                --client-key=/opt/kubernetes/admin/admin-key.pem \
                --embed-certs=true \
                --kubeconfig=/root/.kube/config
              kubectl config set-context default \
                --cluster=kubernetes \
                --user=cluster-admin \
                --kubeconfig=/root/.kube/config
              kubectl config use-context default --kubeconfig=/root/.kube/config
              kubectl create clusterrolebinding kubelet-bootstrap \
              --clusterrole=system:node-bootstrapper \
              --user=kubelet-bootstrap
              '''
        status, output = subprocess.getstatusoutput(f"ssh root@{ip} '{cmd}'")
        if status != 0:
            if "\"kubelet-bootstrap\" already exists" not in output:
                Msg.fail(f"install kubeconfig fail [{ip}]:{output}")

        Msg.success(f'install kubeconfig ok [{ip}]' + '='*20)
    Msg.warn('End set kubeconfig ')
