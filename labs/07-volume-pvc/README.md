# Lab 05 — Volume, PV ve PVC

**Süre:** ~40 dk | **Müfredat referansı:** Modül 6

## Hedef

- `emptyDir` ile kalıcılık olmadığını görmek
- PVC + PV ile kalıcı veriyi deneyimlemek
- Pod silindiğinde verinin korunduğunu kanıtlamak

## Adımlar

### 1) Önce emptyDir — kaybolan veri

```bash
kubectl apply -f pod-emptydir.yaml
kubectl exec emptydir-demo -- sh -c "echo 'Kalıcı mıyım?' > /data/note.txt"
kubectl exec emptydir-demo -- cat /data/note.txt

kubectl delete pod emptydir-demo
kubectl apply -f pod-emptydir.yaml
kubectl exec emptydir-demo -- cat /data/note.txt
# "No such file" — kaybolmuş
```

### 2) Şimdi PVC ile — kalıcı veri

```bash
kubectl apply -f pvc.yaml
kubectl get pvc,pv
kubectl apply -f pod-pvc.yaml

kubectl exec pvc-demo -- sh -c "echo 'Ben kalıyorum!' > /data/note.txt"
kubectl exec pvc-demo -- cat /data/note.txt

kubectl delete pod pvc-demo
kubectl apply -f pod-pvc.yaml
kubectl exec pvc-demo -- cat /data/note.txt
# Veri orada!
```

## Temizlik

```bash
kubectl delete pod pvc-demo emptydir-demo --ignore-not-found
kubectl delete pvc data
```
