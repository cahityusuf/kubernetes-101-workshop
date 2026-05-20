# Lab 01 — Pod

**Süre:** ~30 dk | **Müfredat referansı:** Modül 2

## Hedef

- Tek konteynerli ve çok konteynerli (sidecar) Pod yaratmak
- Pod yaşam döngüsünü gözlemlemek
- `logs`, `exec`, `port-forward` komutlarına alışmak
- Pod IP'sinin geçici olduğunu deneyimlemek

## Adımlar

### 1) Imperative — kubectl run

```bash
kubectl run web --image=nginx:1.27 --port=80 --labels=app=web
kubectl get pods -o wide
kubectl describe pod web | head -30
kubectl port-forward pod/web 8080:80
# yeni terminal:
curl http://localhost:8080
```

### 2) Declarative — YAML manifest

```bash
kubectl apply -f pod.yaml
kubectl get pods -l app=demo
kubectl logs demo
kubectl exec -it demo -- sh
```

### 3) Çok konteynerli Pod (sidecar)

```bash
kubectl apply -f sidecar-pod.yaml
kubectl logs sidecar -c app
kubectl logs sidecar -c log-shipper
```

### 4) Pod IP geçicidir (deneyim)

```bash
kubectl get pod web -o jsonpath='{.status.podIP}'; echo
kubectl delete pod web
kubectl run web --image=nginx:1.27 --port=80 --labels=app=web
kubectl get pod web -o jsonpath='{.status.podIP}'; echo
# Yeni IP! Bu yüzden başka uygulamalar Service kullanır.
```

## Beklenen Çıktı

- `web` Pod'u Running durumda
- `sidecar` Pod'unda iki konteynerin (app + log-shipper) aynı IP'yi paylaştığı görülebilmeli
- Pod silinip yeniden yaratıldığında IP'nin değiştiği gözlemlenmiş olmalı

## Temizlik

```bash
kubectl delete pod web demo sidecar --ignore-not-found
```
