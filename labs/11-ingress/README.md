# Lab 07 — Ingress

**Süre:** ~30 dk | **Müfredat referansı:** Modül 9

## Önkoşul

```bash
minikube addons enable ingress
kubectl get pods -n ingress-nginx
```

## Hedef

- Path-based ve host-based routing yapmak
- Aynı IP üzerinden birden çok Service'e erişmek

## Adımlar

### 1) İki ayrı backend Service hazırla

```bash
kubectl apply -f app-foo.yaml
kubectl apply -f app-bar.yaml
kubectl get svc | grep -E 'foo|bar'
```

### 2) Ingress kuralını uygula

```bash
kubectl apply -f ingress.yaml
kubectl get ingress
```

### 3) /etc/hosts'a giriş ekle

```bash
echo "$(minikube ip)  apps.local" | sudo tee -a /etc/hosts
```

### 4) Test

```bash
curl http://apps.local/foo
# foo backend'inden cevap

curl http://apps.local/bar
# bar backend'inden cevap
```

### 5) Host-based routing varyasyonu

```bash
echo "$(minikube ip)  foo.local bar.local" | sudo tee -a /etc/hosts
kubectl apply -f ingress-host-based.yaml

curl http://foo.local/
curl http://bar.local/
```

## Temizlik

```bash
kubectl delete -f .
```
