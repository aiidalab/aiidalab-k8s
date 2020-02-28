#!/bin/bash
# Use this script to apply updates from config-template.yaml
set -e

#RELEASE=jhub-ka
#NAMESPACE=aiidalab

# customize login page
kubectl apply -f customization/login-cm.yml

# deploy jupyterhub
j2 config-template.yaml secrets.yaml > config.yaml
python combine.py > jupyterhub/values.yaml
helm template jupyterhub > full.yaml
kubectl apply -f full.yaml
