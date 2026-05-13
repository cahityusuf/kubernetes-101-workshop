# Lab 04 — ConfigMap & Secret

**Süre:** ~40 dk | **Müfredat referansı:** Modül 5

## Hedef

- ConfigMap'i hem env hem volume olarak Pod'a bağlamak
- ConfigMap güncellendiğinde volume mount'un anlık tazelendiğini, env'in tazelenmediğini görmek
- Secret'ı güvenli şekilde Pod'a aktarmak

## Adımlar

### 1) Imperative oluşturma

```bash
kubectl create configmap app-config \
  --from-literal=APP_MODE=prod --from-literal=LOG_LEVEL=info \
  --dry-run=client -o yaml
# çıktıyı incele, sonra:
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl get cm,secret
```

### 2) Pod'u oluştur ve değerleri gör

```bash
kubectl apply -f pod.yaml
kubectl exec demo -- env | grep -E 'APP_MODE|LOG_LEVEL|GREETING'
kubectl exec demo -- cat /etc/config/banner.txt
kubectl exec demo -- printenv DB_PASSWORD
```

### 3) ConfigMap canlı güncelleme (volume mount tazelenir)

```bash
kubectl edit configmap app-config
# banner.txt içeriğini değiştir, kaydet

# 30-60 sn bekle
kubectl exec demo -- cat /etc/config/banner.txt
# Yeni içerik görmelisin

# Env tazelendi mi? — Hayır, çünkü envFrom statiktir
kubectl exec demo -- env | grep LOG_LEVEL
# Aynı eski değer
```

### 4) Env'in tazelenmesi için Pod restart

```bash
kubectl delete pod demo
kubectl apply -f pod.yaml
kubectl exec demo -- env | grep LOG_LEVEL
```

## Temizlik

```bash
kubectl delete -f pod.yaml -f configmap.yaml -f secret.yaml
```
