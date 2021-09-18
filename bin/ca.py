import subprocess
import os
from jinja2 import Template
from bin.tools.color import Msg


def gen_json(master):
    with open('tls/etcd/server-csr.json.j2') as f:
        template = Template(f.read())
        content = template.render(master=master)
        with open('tls/etcd/server-csr.json', 'w') as m:
            m.write(content)

    with open('tls/k8s/apiserver/apiserver-csr.json.j2') as f:
        template = Template(f.read())
        content = template.render(master=master)
        with open('tls/k8s/apiserver/apiserver-csr.json', 'w') as m:
            m.write(content)


def gen_cert(master):
    Msg.warn("Start gen cert"+"="*20)
    subprocess.getoutput(
        "find tls/ ! -name '*.json*' -type f |xargs rm -f")
    gen_json(master)
    cwd = os.getcwd()
    gen_cmd = f'''
            cd {cwd}/tls/etcd/;cfssl gencert -initca ca-csr.json | cfssljson -bare ca -  
            cd {cwd}/tls/etcd/;cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=www server-csr.json | cfssljson -bare server
            cd {cwd}/tls/k8s/;cfssl gencert -initca ca-csr.json | cfssljson -bare ca -
            cd {cwd}/tls/k8s/apiserver;cfssl gencert -ca={cwd}/tls/k8s/ca.pem -ca-key={cwd}/tls/k8s/ca-key.pem -config={cwd}/tls/k8s/ca-config.json -profile=kubernetes apiserver-csr.json | cfssljson -bare server
            cd {cwd}/tls/k8s/controller-manager;cfssl gencert -ca={cwd}/tls/k8s/ca.pem -ca-key={cwd}/tls/k8s/ca-key.pem -config={cwd}/tls/k8s/ca-config.json -profile=kubernetes controller-manager-csr.json | cfssljson -bare kube-controller-manager
            cd {cwd}/tls/k8s/scheduler;cfssl gencert -ca={cwd}/tls/k8s/ca.pem -ca-key={cwd}/tls/k8s/ca-key.pem -config={cwd}/tls/k8s/ca-config.json -profile=kubernetes scheduler-csr.json | cfssljson -bare kube-scheduler
            cd {cwd}/tls/k8s/admin;cfssl gencert -ca={cwd}/tls/k8s/ca.pem -ca-key={cwd}/tls/k8s/ca-key.pem -config={cwd}/tls/k8s/ca-config.json -profile=kubernetes admin-csr.json | cfssljson -bare admin
            cd {cwd}/tls/k8s/proxy;cfssl gencert -ca={cwd}/tls/k8s/ca.pem -ca-key={cwd}/tls/k8s/ca-key.pem -config={cwd}/tls/k8s/ca-config.json -profile=kubernetes proxy-csr.json | cfssljson -bare kube-proxy
    '''

    status, output = subprocess.getstatusoutput(gen_cmd)
    if status != 0:
        Msg.fail(f"gen ca cert fail:{output}")
    Msg.warn("End gen cert")
