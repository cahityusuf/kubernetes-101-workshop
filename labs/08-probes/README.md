# Lab 06 — Probe'lar (Liveness, Readiness, Startup)

**Süre:** ~30 dk | **Müfredat referansı:** Modül 8

## Hedef

- 3 probe türünün davranışını görmek
- Liveness fail → restart akışını gözlemlemek
- Readiness fail → endpoint listesinden düşmeyi gözlemlemek

## Adımlar

### 1) Sağlıklı Deployment

```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl get pods -l app=probe-demo
kubectl get endpoints probe-demo
# 3 endpoint listede olmalı
```

### 2) Readiness'i bozarak endpoint kaybı

```bash
POD=$(kubectl get pod -l app=probe-demo -o name | head -1)
kubectl exec $POD -- rm -f /tmp/ready
# 10 saniye sonra:
kubectl get endpoints probe-demo
# 1 endpoint eksik (Pod hâlâ çalışıyor ama trafik almıyor)

kubectl exec $POD -- touch /tmp/ready
# Geri eklenmeli
```

### 3) Liveness'i bozarak restart

```bash
kubectl exec $POD -- rm -f /tmp/healthy
# ~30 saniye sonra:
kubectl get pods -l app=probe-demo
# RESTARTS sütununda 1 göreceksin
kubectl describe pod $POD | grep -A 3 "Last State"
```

## Temizlik

```bash
kubectl delete -f deployment.yaml -f service.yaml
```
