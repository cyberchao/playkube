import time
from bin.local.init import init
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


master = ['10.0.0.21', '10.0.0.22', '10.0.0.23']

if __name__ == "__main__":
    Msg.warn("Kubernetes Cluster Installation Start...\n")
    start = time.time()
    init()
    for ip in master:
        system_init(ip)
    gen_cert(master)
    etcd(master)
    docker(master)
    apiserver(master)
    controller_manager(master)
    scheduler(master)
    admin(master)

    kubelet('10.0.0.22')
    proxy('10.0.0.22')

    Msg.success("Kubernetes install finished, cost time:" + time.time()-start)

