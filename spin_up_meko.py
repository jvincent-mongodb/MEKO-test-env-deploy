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
        # TODO: recursively loop through CRD resources to be uploaded
        local_path = 'test.txt'
        remote_path = 'test.txt'
        sftp = self.ssh.open_sftp()
        sftp.put(localpath=local_path, remotepath=remote_path)
        

    def install_k3s(self):
        stdin, stdout, stderr = self.ssh.exec_command('curl -sfL https://get.k3s.io | sh -')
        print(stdout.readlines())

    def install_helm(self):
        pass

    def deploy_meko(self):
        stdin, stdout, stderr = self.ssh.exec_command('kubectl create namespace mongodb')
        stdin, stdout, stderr = self.ssh.exec_command('helm add ')
        stdin, stdout, stderr = self.ssh.exec_command('helm install ')

    def deploy_mongodb(self):
        stdin, stdout, stderr = self.ssh.exec_command('kubectl ')

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
    mc.open_ssh_connection()
    # mc.install_k3s()
    mc.upload_resources()
    # mc.install_helm()
    # mc.deploy_meko()
    # mc.deploy_mongodb()


if __name__ == '__main__':
    main()
