# MEKO-test-env-deploy

A simple utility script that deploys a Rancher K3s cluster on an Evergreen VM and then deploys MEKO resources on that cluster.

## Usage

1. Spin up an Ubuntu 22.04 Evergreen VM.
2. Run the following command from your local machine

```
python3 spin_up_meko.py <evergreen-hostname> <ssh-password> <evergreen-vm-username>
```

3. SSH into the Evergreen VM as you normally would.
4. Run the following to confirm a successful deployment:
```
sudo kubectl get all -n mongodb
```
```
sudo kubectl get crds -n mongodb
```
