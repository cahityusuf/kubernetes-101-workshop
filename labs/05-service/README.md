# Lab 03 — Service ve Ağ Modeli

**Süre:** ~45 dk | **Müfredat referansı:** Modül 4

## Hedef

- ClusterIP, NodePort ve LoadBalancer farkını canlı görmek
- Selector → Endpoints zincirini anlamak
- Cluster içi DNS ile Service çağırmak
- Readiness probe'un endpoint listesini nasıl etkilediğini gözlemlemek

## Önkoşul

Önceki lab'taki Deployment çalışıyor olmalı. Yoksa:
```bash
kubectl apply -f ../02-deployment/deployment.yaml
```

## Adımlar

### 1) ClusterIP Service

```bash
kubectl apply -f service-clusterip.yaml
kubectl get svc web
kubectl get endpoints web
```

### 2) Cluster içi DNS testi

```bash
kubectl run probe --rm -it --image=busybox:1.36 --restart=Never -- sh
  # Pod içinde:
  > wget -qO- web.default.svc.cluster.local
  > nslookup web
  > exit
```

### 3) Service round-robin

```bash
# Birden çok kez çağırın; Pod adları değişmeli
for i in 1 2 3 4 5; do
  kubectl run probe-$i --rm -i --image=busybox:1.36 --restart=Never -- \
    wget -qO- http://web/ | grep -i "Welcome"
done
```

### 4) NodePort'a yükselt

```bash
kubectl apply -f service-nodeport.yaml
kubectl get svc web-np
minikube service web-np --url
```

### 5) Readiness ile endpoint kaybı

```bash
# Bir Pod'u "unhealthy" işaretleyin (probe path'ini bozun)
kubectl exec -it $(kubectl get pod -l app=web -o name | head -1) -- \
  sh -c "rm -f /usr/share/nginx/html/index.html"
# Endpoint listesi 3'ten 2'ye düşmeli
kubectl get endpoints web
```

## Temizlik

```bash
kubectl delete -f service-clusterip.yaml -f service-nodeport.yaml
```
