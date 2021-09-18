import sys
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


class Config:
    global kube_apiserver_hosts
    global kube_controller_manager_hosts
    global kube_scheduler_hosts
    global kube_node_hosts
    global kube_apiserver_url
    global all_hosts


def configparser():
    with open('config.yaml') as f:
        data = yaml.load(f, Loader=SafeLoader)

    Config.etcd_hosts = data['etcd']['hosts'].split(' ')
    Config.kube_apiserver_hosts = data['kube-master']['kube-apiserver']['hosts'].split(
        ' ')
    Config.kube_controller_manager_hosts = data['kube-master']['kube-controller-manager']['hosts'].split(
        ' ')
    Config.kube_scheduler_hosts = data['kube-master']['kube-scheduler']['hosts'].split(
        ' ')
    Config.kube_node_hosts = data['kube-node']['hosts'].split(' ')
    Config.kube_apiserver_url = data['kube-apiserver-url']['url']

    Config.all_hosts = set(Config.etcd_hosts + Config.kube_apiserver_hosts +
                           Config.kube_controller_manager_hosts +
                           Config.kube_scheduler_hosts + Config.kube_node_hosts)


def cluster():
    # 集群安装
    Msg.warn("Kubernetes Cluster Installation Start...\n\n")
    init()
    for ip in Config.all_hosts:
        system_init(ip)
    gen_etcd_json(Config.etcd_hosts)
    gen_apiserver_json(Config.kube_apiserver_hosts)
    gen_cert()
    etcd(Config.etcd_hosts)
    docker(Config.kube_node_hosts)
    apiserver(Config.kube_apiserver_hosts)
    controller_manager(Config.kube_controller_manager_hosts,
                       Config.kube_apiserver_url)
    scheduler(Config.kube_scheduler_hosts, Config.kube_apiserver_url)
    admin(Config.kube_apiserver_hosts, Config.kube_apiserver_url)

    scale(Config.kube_node_hosts)
    Msg.success("Kubernetes install finished")


def scale(node_list):
    # node扩容
    for ip in node_list:
        kubelet(ip, Config.kube_apiserver_url)
        proxy(ip, Config.kube_apiserver_url)
        Msg.success(f"Node scale success [{ip}]")


def main():
    arg = sys.argv[1]
    configparser()
    if arg:
        if arg.split('=')[0] == '-n':
            Msg.warn('Start Node scale')
            node_list = arg.split('=')[1].split(',')
            scale(node_list)
            Msg.warn('End Node scale')
        else:
            Msg.fail('args error')
    else:
        cluster()


if __name__ == '__main__':
    start = time.time()
    main()
    Msg.warn("Finished, Spend time:" + str(time.time()-start))
