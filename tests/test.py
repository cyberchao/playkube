import yaml
from yaml.loader import SafeLoader

# Open the file and load the file
with open('config.yaml') as f:
    data = yaml.load(f, Loader=SafeLoader)
print(data)
etcd_hosts = data['etcd']['hosts'].split(
    ' ')
kube_apiserver_hosts = data['kube-master']['kube-apiserver']['hosts'].split(
    ' ')
kube_controller_manager_hosts = data['kube-master']['kube-controller-manager']['hosts'].split(
    ' ')
kube_scheduler_hosts = data['kube-master']['kube-scheduler']['hosts'].split(
    ' ')
kube_node_hosts = data['kube-node']['hosts'].split(
    ' ')
kube_apiserver_url = data['kube-apiserver-url']['url']
print(etcd_hosts)
print(kube_apiserver_hosts)
print(kube_controller_manager_hosts)
print(kube_scheduler_hosts)
print(kube_node_hosts)
print(kube_apiserver_url)
