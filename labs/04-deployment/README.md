# Lab 02 — Deployment & ReplicaSet

**Süre:** ~45 dk | **Müfredat referansı:** Modül 3

## Hedef

- Deployment → ReplicaSet → Pod zincirini görmek
- Self-healing'i test etmek
- Rolling update + rollback yapmak
- HPA için temel hazırlık

## Adımlar

### 1) Deployment oluştur

```bash
kubectl apply -f deployment.yaml
kubectl get deploy,rs,pods -l app=web
```

### 2) Self-healing testi

```bash
# Bir Pod sil; ReplicaSet hemen yenisini yaratır
kubectl delete pod -l app=web --field-selector=status.phase=Running --wait=false | head -1
kubectl get pods -l app=web -w
```

### 3) Rolling update

```bash
kubectl set image deploy/web nginx=nginx:1.28
kubectl rollout status deploy/web
kubectl get rs -l app=web   # iki RS göreceksin (eski + yeni)
kubectl rollout history deploy/web
```

### 4) Bilerek hatalı image → rollback

```bash
kubectl set image deploy/web nginx=nginx:hatali-tag
kubectl rollout status deploy/web --timeout=30s  # fail
kubectl rollout undo deploy/web
kubectl rollout status deploy/web
```

### 5) Ölçekleme

```bash
kubectl scale deploy/web --replicas=5
kubectl get pods -l app=web
```

## Beklenen Çıktı

- `kubectl get rs` çıktısında her image değişikliğinde yeni bir RS açılmış olmalı
- Pod silindikten saniyeler sonra yenisi yaratılmış olmalı
- Rollback sonrası önceki image'a dönülmüş olmalı

## Temizlik

```bash
kubectl delete -f deployment.yaml
```
