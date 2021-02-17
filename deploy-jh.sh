#!/bin/bash
# Use this script to apply updates from config-template.yaml
set -e

RELEASE=aiidalab

# deploy jupyterhub
j2 config-template.yaml secrets.yaml > config.yaml

helm upgrade --install $RELEASE jupyterhub/jupyterhub \
    --version=0.9.0 \
    --values config.yaml \
    --cleanup-on-fail

# customize login page
kubectl apply -f customization/login-cm.yml
