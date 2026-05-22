# Lab 07 — hostPath Volume Örneği

**Süre:** ~15 dk | **Müfredat referansı:** Modül 6 (Volumes)

## Hedef

- `hostPath` volume'un nasıl çalıştığını ve **node'a bağımlı** olduğunu görmek
- Pod silinse bile aynı node'da gelirse verinin durduğunu gözlemlemek
- Pod farklı bir node'a düşerse verinin "kaybolduğunu" (aslında diğer node'da kaldığını) anlamak
- Üretimde neden `hostPath` yerine PV/PVC veya CSI tabanlı çözümlerin tercih edildiğini kavramak

## Önkoşullar

- Çok node'lu bir cluster (örneklerde `node1`, `node2` kullanılıyor)
- `cahit` namespace'inin baseline veya privileged PSA seviyesinde olması (`hostPath`, `restricted` profile'da yasaklı)

## Adımlar

### 1) Deployment'ı uygula

```bash
kubectl apply -f deployment-hostPath.yaml
kubectl -n cahit get pod -l app=hostpath-demo -o wide
# NODE sütununda 'node1' görmelisiniz (nodeSelector sayesinde).
```

### 2) Uygulamadan dosya yükle

```bash
kubectl -n cahit port-forward deploy/hostpath-demo 8080:8080
# Tarayıcı: http://localhost:8080/Storage → "Dosya yükle"
```

Container içinden doğrula:

```bash
kubectl -n cahit exec deploy/hostpath-demo -- ls -la /data/uploads
```

### 3) Aynı dosyayı node1 üzerinde gör

```bash
ssh root@<node1-ip> "ls -la /mnt/k8s-playground/hostpath/uploads"
# → container'da gördüğünüz aynı dosya burada da var.
```

> **Anahtar fikir:** `hostPath`, node'un dosya sistemine doğrudan açılan bir penceredir. Container ile node aynı dizine bakar.

### 4) Pod'u sil — veri kalmalı

```bash
kubectl -n cahit delete pod -l app=hostpath-demo
kubectl -n cahit get pod -l app=hostpath-demo -w
# yeni Pod Ready olunca:
kubectl -n cahit exec deploy/hostpath-demo -- ls -la /data/uploads
# → Dosya hâlâ orada (nodeSelector node1 olduğu için aynı node'a düştü).
```

### 5) Veri kaybı senaryosu — Pod farklı node'a düşerse

```bash
# Deployment'ı node2'ye yönlendir:
kubectl -n cahit patch deploy hostpath-demo --type=merge \
  -p '{"spec":{"template":{"spec":{"nodeSelector":{"kubernetes.io/hostname":"node2"}}}}}'

kubectl -n cahit get pod -l app=hostpath-demo -o wide
# NODE = node2
kubectl -n cahit exec deploy/hostpath-demo -- ls -la /data/uploads
# → Boş! Çünkü node2'de /mnt/k8s-playground/hostpath dizini yeni oluşturuldu.
#   Veri aslında kayıp değil — node1'de duruyor. Ama Pod ona ulaşamıyor.
```

Bu nokta `hostPath`'in **temel zayıflığıdır**: depolama node'a bağlıdır, Pod'a değil.

## Temizlik

```bash
kubectl -n cahit delete -f deployment-hostPath.yaml

# Node üzerindeki dizini elle silmek isterseniz:
ssh root@<node1-ip> "rm -rf /mnt/k8s-playground/hostpath"
ssh root@<node2-ip> "rm -rf /mnt/k8s-playground/hostpath"
```

## Ne zaman `hostPath` kullanılır?

| Senaryo | Uygunluk |
|---|---|
| Node-level log/metric collector (DaemonSet, `/var/log` okuma) | Uygun |
| Tek node'lu dev/test ortamı | Uygun |
| Multi-node stateful uygulama | Uygun değil → PV/PVC kullanın |
| Üretimde paylaşımlı depolama | Uygun değil → CSI driver (Longhorn, Ceph, NFS) kullanın |

## Sık Yapılan Hatalar

- **`type` alanını atlamak:** `DirectoryOrCreate` belirtmezseniz dizin yoksa Pod `CreateContainerError` alır.
- **`nodeSelector` koymadan kullanmak:** Pod her yeniden scheduling'de farklı node'a düşebilir ve veri "kaybolur".
- **`replicas > 1`:** Aynı `hostPath`'e farklı node'lardan iki Pod yazamaz; ayrıca aynı node'da iki Pod yazarsa concurrency sorunları çıkar. `Recreate` strategy ile bu engellenir.
- **PSA `restricted`:** `hostPath`, restricted profile'da yasaktır. Namespace'i `baseline` veya `privileged` yapın ya da `restricted` uyumlu CSI çözümüne geçin.
