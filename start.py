import time
from bin.local.init import init
from bin.ca import gen_etcd_json
from bin.ca import gen_apiserver_json
from bin.ca import gen_cert
from bin.master.system_init import system_init
from bin.master.etcd import etcd
from bin.master.docker import docker
from bin.master.kube_apiserver import apiserver
from bin.master.controller_manager import controller_manager
from bin.master.scheduler import scheduler
from bin.master.admin import admin
from bin.node.kubelet import kubelet
from bin.node.proxy import proxy
from bin.tools.color import Msg
import yaml
from yaml.loader import SafeLoader

with open('config.yaml') as f:
    data = yaml.load(f, Loader=SafeLoader)

etcd_hosts = data['etcd']['hosts'].split(' ')
kube_apiserver_hosts = data['kube-master']['kube-apiserver']['hosts'].split(
    ' ')
kube_controller_manager_hosts = data['kube-master']['kube-controller-manager']['hosts'].split(
    ' ')
kube_scheduler_hosts = data['kube-master']['kube-scheduler']['hosts'].split(
    ' ')
kube_node_hosts = data['kube-node']['hosts'].split(' ')
kube_apiserver_url = data['kube-apiserver-url']['url']

all_hosts = etcd_hosts + kube_apiserver_hosts + \
    kube_controller_manager_hosts + kube_scheduler_hosts + kube_node_hosts

all_hosts = set(all_hosts)

master = ['10.0.0.21', '10.0.0.22', '10.0.0.23']

if __name__ == "__main__":
    Msg.warn("Kubernetes Cluster Installation Start...\n")
    start = time.time()
    init()
    for ip in all_hosts:
        system_init(ip)
    gen_etcd_json(etcd_hosts)
    gen_apiserver_json(kube_apiserver_hosts)
    gen_cert()
    etcd(etcd_hosts)
    docker(kube_node_hosts)
    apiserver(kube_apiserver_hosts)
    controller_manager(kube_controller_manager_hosts, kube_apiserver_url)
    scheduler(kube_scheduler_hosts, kube_apiserver_url)
    admin(kube_apiserver_hosts, kube_apiserver_url)

    for ip in kube_node_hosts:
        kubelet(ip, kube_apiserver_url)
        proxy(ip, kube_apiserver_url)

    Msg.success("Kubernetes install finished, cost time:" +
                str(time.time()-start))
