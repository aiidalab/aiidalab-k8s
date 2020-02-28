#!/bin/bash
set -e

# Install cert-manager
kubectl create namespace cert-manager
kubectl label namespace cert-manager certmanager.k8s.io/disable-validation=true
kubectl apply -f https://github.com/jetstack/cert-manager/releases/download/v0.8.1/cert-manager.yaml

# set up let's encrypt issuer
kubectl apply -f ssl_certs/letsencrypt.yaml

# set up ingress
kubectl apply -f ssl_certs/ingress.yml
