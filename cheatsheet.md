## architecture

 * Hub is running in pod `hub-...`
   * See `/srv/jupyterhub_config.py` on the pod
   * `kubectl logs -f hub-84944d897c-7qvtj`
 * User pods are named `jupyter-<username>`
 * Persistent volume claims are named `claim-<username>`

## kubectl

 * `kubectl get pod` list current pods
   * if all pods are "RUNNING", deployment is complete
 * `kubectl describe pod mypod` list current pods
 * `kubectl exec -it mypod -- /bin/bash` get shell in pod
 * `kubectl logs -f mypod` see logs of pod
 * `kubectl describe storageclass stgclass`
 * `kubectl apply -f storageclass.yml`
 * `kubectl delete pvc claim-tal` delete user home dir
 * `kubectl get ingress example-ingress -o yaml` get yaml config of something
