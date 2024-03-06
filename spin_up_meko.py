import argparse
import paramiko

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
        local_path = 'mongoDB.yaml'
        remote_path = 'mongoDB.yaml'
        sftp = self.ssh.open_sftp()
        sftp.put(local_path, remote_path)
        
    def install_k3s(self):
        stdin, stdout, stderr = self.ssh.exec_command('curl -sfL https://get.k3s.io | sh -')
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print('Kubernetes cluster successfully deployed!')

    def install_helm(self):
        stdin, stdout, stderr = self.ssh.exec_command(
            'curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3')
        exit_status = stdout.channel.recv_exit_status()
        stdin, stdout, stderr = self.ssh.exec_command('chmod 700 get_helm.sh')
        exit_status = stdout.channel.recv_exit_status()
        stdin, stdout, stderr = self.ssh.exec_command('./get_helm.sh')
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print('Helm successfuly installed!')

    def deploy_meko(self):
        stdin, stdout, stderr = self.ssh.exec_command('sudo kubectl create namespace mongodb')
        exit_status = stdout.channel.recv_exit_status()
        stdin, stdout, stderr = self.ssh.exec_command(
            'sudo helm repo add mongodb https://mongodb.github.io/helm-charts')
        exit_status = stdout.channel.recv_exit_status()
        stdin, stdout, stderr = self.ssh.exec_command(
            'sudo helm install enterprise-operator mongodb/enterprise-operator --namespace mongodb --kubeconfig /etc/rancher/k3s/k3s.yaml')
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print('MEKO successfuly deployed!')

    def deploy_mongodb(self):
        stdin, stdout, stderr = self.ssh.exec_command('sudo kubectl apply -f CRDs/mongoDB.yaml')

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
    print('Deploying uploaded CRDs to Kubernetes on your Evergreen VM ...')
    # mc.deploy_mongodb()
    print('MEKO test environment ready!')


if __name__ == '__main__':
    main()
