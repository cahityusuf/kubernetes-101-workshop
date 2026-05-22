# Lab 07 — Statik PersistentVolume Örneği

**Süre:** ~25 dk | **Müfredat referansı:** Modül 6 (Volumes, PV, PVC, Reclaim Policy)

## Hedef

- **Statik provisioning** ile **dinamik provisioning** arasındaki farkı kavramak
- PV ↔ PVC eşleşme kurallarını (capacity, accessModes, storageClassName, selector) görmek
- `local` tipi PV ve `nodeAffinity` ile scheduler'ın PV topology'sine nasıl uyduğunu deneyimlemek
- `Retain` reclaim policy'sinin "PVC silindi ama PV ve veri korunuyor" davranışını gözlemlemek

## Dinamik vs Statik — Hızlı Karşılaştırma

| Boyut | Dinamik (mevcut `pvc.yaml` + `local-path`) | Statik (bu örnek) |
|---|---|---|
| PV'yi kim oluşturur? | StorageClass'taki provisioner otomatik | Cluster yöneticisi elle |
| `storageClassName` | Var ve aktif provisioner'lı SC | `"manual"` (provisioner'sız) veya `""` |
| Tipik kullanım | Cloud disk, CSI sürücüleri, dev cluster | Önceden hazırlanmış local diskler, NFS export |
| PVC `Pending` riski | Düşük (provisioner anında üretir) | Yüksek (eşleşen PV yoksa kalır) |

## Önkoşullar

Node1 üzerinde PV'nin işaret ettiği dizin önceden var olmalı ve UID 10001 yazabilmeli:

```bash
ssh root@<node1-ip> <<'EOF'
mkdir -p /mnt/k8s-playground/pv-data
chown 10001:10001 /mnt/k8s-playground/pv-data
chmod 0775 /mnt/k8s-playground/pv-data
EOF
```

> Node IP'lerini şununla görebilirsiniz: `kubectl get nodes -o wide`

## Adımlar

### 1) PV'yi oluştur (cluster-scoped)

```bash
kubectl apply -f pv.yaml
kubectl get pv k8s-playground-pv
# STATUS = Available
```

### 2) PVC'yi oluştur (namespace-scoped)

```bash
kubectl apply -f pvc.yaml
kubectl get pv,pvc -n cahit
# PVC STATUS = Bound, PV CLAIM = cahit/k8s-playground-pvc
```

Eşleşme nasıl oldu?

| Alan | PV | PVC | Sonuç |
|---|---|---|---|
| `storageClassName` | `manual` | `manual` | ✓ |
| `accessModes` | `ReadWriteOnce` | `ReadWriteOnce` | ✓ |
| `capacity` / `requests.storage` | `1Gi` | `1Gi` | ✓ (PV ≥ PVC) |

### 3) Deployment'ı uygula

```bash
kubectl apply -f deployment-pv.yaml
kubectl -n cahit get pod -l app=staticpv-demo -o wide
# NODE = node1  (PV nodeAffinity sayesinde — biz nodeSelector vermedik!)
```

### 4) Dosya yükle ve kalıcılığı test et

```bash
kubectl -n cahit port-forward deploy/staticpv-demo 8080:8080
# http://localhost:8080/Storage → "Dosya yükle"

kubectl -n cahit exec deploy/staticpv-demo -- ls -la /data/uploads
# Yüklenen dosyayı görüyorsunuz.

# Pod'u sil → yeni Pod aynı node'a, aynı diske gelir:
kubectl -n cahit delete pod -l app=staticpv-demo
kubectl -n cahit get pod -l app=staticpv-demo -w
kubectl -n cahit exec deploy/staticpv-demo -- ls -la /data/uploads
# Dosya hâlâ orada.
```

### 5) `Retain` reclaim policy'sini gözle

```bash
kubectl -n cahit delete -f deployment-pv.yaml
kubectl -n cahit delete -f pvc.yaml

kubectl get pv k8s-playground-pv
# STATUS = Released  → PV ve veri korundu.
```

Node1'e bağlanıp veriye bakın:

```bash
ssh root@<node1-ip> "ls -la /mnt/k8s-playground/pv-data/uploads"
# Dosyalar hâlâ burada.
```

PV'yi yeniden kullanılabilir yapmak için PVC bağını temizleyin:

```bash
kubectl patch pv k8s-playground-pv --type=json \
  -p='[{"op":"remove","path":"/spec/claimRef"}]'

kubectl get pv k8s-playground-pv
# STATUS = Available  → tekrar bind edilebilir.
```

## Temizlik

```bash
kubectl -n cahit delete -f deployment-pv.yaml --ignore-not-found
kubectl -n cahit delete -f pvc.yaml             --ignore-not-found
kubectl delete -f pv.yaml                       --ignore-not-found

# Node üzerindeki veri:
ssh root@<node1-ip> "rm -rf /mnt/k8s-playground/pv-data"
```

## Sık Yapılan Hatalar

- **PVC `Pending` kalıyor** → PV'nin `storageClassName`, `accessModes`, `capacity` alanlarını PVC ile kontrol edin. `kubectl describe pvc` event'lerine bakın.
- **Pod `Pending` (FailedScheduling)** → PV'nin `nodeAffinity`'si o node'a Pod yerleştirmeyi engelliyor olabilir; node taint/cordon durumunu kontrol edin.
- **`Permission denied` `/data` altına yazarken** → Node'daki dizinin sahibi UID 10001 değil. Önkoşul adımındaki `chown` adımını tekrar edin. (Alternatif: `securityContext.fsGroup` ile kubelet'in dizini chown etmesini tetikleyebilirsiniz; `local` volume için bazı sürümlerde çalışır.)
- **`Retain` ile PV `Released`'de takılıp tekrar bind olmuyor** → `spec.claimRef` alanını manuel kaldırın. Bu Kubernetes'in kasıtlı davranışıdır; eski veriyi temizlemek admin sorumluluğundadır.
- **Yanlışlıkla `replicas: 2`** → RWO PVC tek node'a bağlı; ikinci Pod `MultiAttachError` alır. RWX gerekiyorsa NFS / CephFS / Longhorn RWX kullanın.

## Üretim Notu

Local volume'leri elle PV yazarak yönetmek hızla zahmetlidir. Üretim ortamlarında:

- **`local-volume-provisioner`** (sig-storage): node'da önceden hazırlanmış mount point'leri otomatik PV'leştirir.
- **CSI sürücüleri** (Longhorn, OpenEBS, Rook-Ceph, TopoLVM): dinamik provisioning + replikasyon + snapshot.

Bu cluster'da örneğin `longhorn` default StorageClass olarak hazırdır — production iş yükleri için bunu tercih edin.
