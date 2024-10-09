import argparse
import paramiko
import time

class SpinUpMekoCluster:
    def __init__(self, args):
        self.ssh = paramiko.SSHClient()
        self.hostname = args.hostname
        self.password = args.password
        self.username = args.username
        self.port = 22

    def open_ssh_connection(self):
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(self.hostname, self.port, self.username, self.password)

    def upload_resources(self):
        paths = ['mongoDB.yaml','opsManager.yaml']
        sftp = self.ssh.open_sftp()
        for path in paths:
            sftp.put(path, path)
        
    def install_k3s(self):
        stdin, stdout, stderr = self.ssh.exec_command('curl -sfL https://get.k3s.io | sh -')
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print('*****************************************')
            print('Kubernetes cluster successfully deployed!')
            print('*****************************************')

    def install_helm(self):
        stdin, stdout, stderr = self.ssh.exec_command(
            'curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3')
        stdout.channel.recv_exit_status()
        stdin, stdout, stderr = self.ssh.exec_command('chmod 700 get_helm.sh')
        stdout.channel.recv_exit_status()
        stdin, stdout, stderr = self.ssh.exec_command('./get_helm.sh')
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print('***************************')
            print('Helm successfuly installed!')
            print('***************************')

    def deploy_meko(self):
        stdin, stdout, stderr = self.ssh.exec_command('sudo kubectl create namespace mongodb')
        stdout.channel.recv_exit_status()
        stdin, stdout, stderr = self.ssh.exec_command(
            'sudo helm repo add mongodb https://mongodb.github.io/helm-charts')
        stdout.channel.recv_exit_status()
        stdin, stdout, stderr = self.ssh.exec_command(
            'sudo helm install enterprise-operator mongodb/enterprise-operator --namespace mongodb --kubeconfig /etc/rancher/k3s/k3s.yaml')
        stdout.channel.recv_exit_status()

    def confirm_meko_deployment(self):
        stdin, stdout, stderr = self.ssh.exec_command('sudo kubectl get pods -n mongodb')
        r = stdout.readlines()
        try:
            if 'Running' in r[1]:
                print('**************************')
                print('MEKO successfuly deployed!')
                print('**************************')
            else:
                time.sleep(5)
                self.confirm_meko_deployment()
        except:
                time.sleep(5)
                self.confirm_meko_deployment()

    def deploy_mongodb_crds(self):
        stdin, stdout, stderr = self.ssh.exec_command('sudo kubectl apply -f mongoDB.yaml -n mongodb')
        exit_status = stdout.channel.recv_exit_status()
        stdin, stdout, stderr = self.ssh.exec_command('sudo kubectl apply -f opsManager.yaml -n mongodb')
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print('****************************')
            print('MEKO test environment ready!')
            print('****************************')

def parse_args():
    args = argparse.ArgumentParser()
    args.add_argument('hostname')
    args.add_argument('password')
    args.add_argument('username')
    args = args.parse_args()
    return args

def main():
    args = parse_args()
    mc = SpinUpMekoCluster(args)
    print('Connecting to your Evergreen VM with SSH ...')
    mc.open_ssh_connection()
    print('Uploading local CRDs to your Evergreen VM ...')
    mc.upload_resources()
    print('Installing the Kubernetes (K3s) cluster on your Evergreen VM ...')
    mc.install_k3s()
    print('Installing Helm on your Evergreen VM ...')
    mc.install_helm()
    print('Deploying MEKO via Helm to your Evergreen VM ...')
    mc.deploy_meko()
    mc.confirm_meko_deployment()
    print('Deploying uploaded CRDs to Kubernetes on your Evergreen VM ...')
    mc.deploy_mongodb_crds()
    

if __name__ == '__main__':
    main()
