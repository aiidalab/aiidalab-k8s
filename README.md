# AiiDA lab kubernetes deployment

Follow these instructions in order to set up an AiiDA lab on a kubernetes cluster.

The AiiDA lab setup is based on [z2jh](https://zero-to-jupyterhub.readthedocs.io/en/latest/). Helpful links:

* [z2jh customization guide](https://zero-to-jupyterhub.readthedocs.io/en/latest/customizing/index.html)
* [binderhub helm chart](https://github.com/jupyterhub/binderhub/blob/master/helm-chart/binderhub/values.yaml)
* [extending docker stack](https://github.com/jupyterhub/zero-to-jupyterhub-k8s/tree/master/images/singleuser-sample)
* [kubernetes cheatsheet](cheatsheet.md)

## Prerequisites

This sets up the environment of your local machine for deployment.

### kubernetes setup
* Download kubectl: https://kubernetes.io/docs/tasks/tools/install-kubectl/#install-kubectl
* Follow instructions of your kubernetes provider in order to authenticate. `kubectl get pods` should work
* Download `helm`: https://github.com/helm/helm/releases 
  Note: Only needed locally. Your kuberenetes cluster does not need to support `helm`

### python packages
```
git clone https://github.com/aiidalab/aiidalab-k8s.git
cd aiidalab-k8s/
pip install -r requirements.txt
```

### JupyterHub helm chart
```
wget https://jupyterhub.github.io/helm-chart/jupyterhub-0.7.0.tgz
tar xzvf jupyterhub-0.7.0.tgz 
cp jupyterhub/values.yaml jupyterhub/values.yaml.orig
```

## Deployment

This deploys AiiDA lab on your kubernetes cluster.

### JupyterHub

 1. `cp secrets.yaml.template secrets.yaml` and edit `secrets.yaml` to provide
 2. Run `./deploy-jh.sh`
 3. Wait until `kubectl get pods` shows all pods as `running`

Note: Updating the login page via `configmap.yml` takes ~1min to take effect after `kubectl apply -f configmap.yml`.

### SSL certificates and ingress

If you have a (sub)domain available, you can make your AiiDA lab reachable via that domain as follows:

 1. Point the DNS record of the subdomain to the external IP of your kubernetes cluster
 2. Edit `./ssl_certs/ingress.yml`, replacing `aiidalab-demo.materialscloud.org` with your DNS host
 3. Run `./deploy-certs.sh` (uses [cert-manager](https://docs.cert-manager.io/en/latest/getting-started/install/kubernetes.html))
 4. Wait until `kubectl get certificate` shows a valid cert (may take a minute or two)

Requests to you domain should now be routed directly to the AiiDA lab (and support HTTPS).

### User login via OpenID Connect 

See commented sections in `config-template.yaml`.
To document fully...
