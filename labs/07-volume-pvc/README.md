# Lab 07 — Volume, PV ve PVC

**Süre:** ~60 dk | **Müfredat referansı:** Modül 6

## Hedef

- `emptyDir`, `hostPath`, statik PV ve dinamik PVC arasındaki farkları kavramak
- Pod silindiğinde verinin hangi senaryoda korunduğunu / kaybolduğunu kanıtlamak
- Üretimde neden PV/PVC + CSI sürücüsü tercih edildiğini somut görmek

## Klasör Yapısı

```
07-volume-pvc/
├── README.md                 # bu dosya — genel bakış
├── notlar.txt                # local-path provisioner kurulum komutu
├── deployment.yaml           # Dinamik PVC (local-path) ile demo
├── pvc.yaml                  # Dinamik PVC tanımı
├── hostPath/                 # 1) hostPath volume örneği
│   ├── README.md
│   └── deployment-hostPath.yaml
└── pv/                       # 2) Statik PV + PVC örneği (local volume + nodeAffinity)
    ├── README.md
    ├── pv.yaml
    ├── pvc.yaml
    └── deployment-pv.yaml
```

## Karşılaştırma — Tek Bakışta

| Tip | Node'a bağımlı mı? | Replikalar paylaşır mı? | Pod silinince veri | Üretim için uygun mu? |
|---|---|---|---|---|
| `emptyDir`           | Hayır (Pod-local) | Hayır | **Kaybolur** | Geçici cache için |
| `hostPath`           | Evet (tek node)   | Hayır | Aynı node'a düşerse durur | Sadece DaemonSet / dev |
| Statik `local` PV    | Evet (PV ↔ node)  | Hayır (RWO) | Korunur | Sınırlı (CSI tercih edilir) |
| Dinamik PVC (CSI)    | Hayır (CSI yönetir) | Storage class'a göre | Korunur | **Evet** |

## Önerilen Sıralama

### 1) `emptyDir` ile veri kaybını gör — Lab 04 ana deployment
Workshop'taki `04-deployment` örneği zaten `emptyDir` kullanır; `/Storage` sayfasından dosya yükleyip Pod'u silerek davranışı doğrulayın.

### 2) `hostPath` — node-local kalıcılık ve sınırları
```bash
cd hostPath
kubectl apply -f deployment-hostPath.yaml
# detaylı adımlar için: hostPath/README.md
```

Görülecek olan:
- Pod aynı node'a yeniden ayağa kalkarsa veri orada.
- Pod farklı node'a kayarsa veri "kaybolur" (aslında eski node'da kalır).

### 3) Statik PV — yöneticinin elle oluşturduğu disk
```bash
cd pv
# Önce node1'de hedef dizini hazırlayın (pv/README.md → Önkoşullar).
kubectl apply -f pv.yaml
kubectl apply -f pvc.yaml
kubectl apply -f deployment-pv.yaml
# detaylı adımlar için: pv/README.md
```

Görülecek olan:
- PV ↔ PVC eşleşme kuralları
- `nodeAffinity` scheduler'a topology bilgisi verir → Pod doğru node'a düşer
- `Retain` policy → PVC silinince veri korunur, PV `Released` olur

### 4) Dinamik PVC — production-style
```bash
# notlar.txt'deki local-path-provisioner kurulu olmalı.
kubectl apply -f pvc.yaml
kubectl apply -f deployment.yaml
```

Görülecek olan:
- PVC `Pending`'den `Bound`'a geçer çünkü provisioner anında PV üretir.
- `storageClassName: local-path` → tüm yönetimi storage class yapar.
- Pod silinse de PVC `Bound` kalır, yeni Pod aynı diske bağlanır.

> Bu cluster'da varsayılan StorageClass `longhorn`'dur (`kubectl get sc`). Üretim simülasyonu için `pvc.yaml` içindeki `storageClassName`'i `longhorn` yapabilirsiniz — bu durumda `notlar.txt`'deki kuruluma gerek kalmaz.

## Temizlik (toplu)

```bash
# Dinamik PVC örneği
kubectl -n cahit delete -f deployment.yaml --ignore-not-found
kubectl -n cahit delete -f pvc.yaml        --ignore-not-found

# Statik PV örneği
kubectl -n cahit delete -f pv/deployment-pv.yaml --ignore-not-found
kubectl -n cahit delete -f pv/pvc.yaml           --ignore-not-found
kubectl         delete -f pv/pv.yaml             --ignore-not-found

# hostPath örneği
kubectl -n cahit delete -f hostPath/deployment-hostPath.yaml --ignore-not-found
```

## Referanslar

- [Kubernetes Docs — Volumes](https://kubernetes.io/docs/concepts/storage/volumes/)
- [Kubernetes Docs — Persistent Volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)
- [Local Volume Provisioner (sig-storage)](https://github.com/kubernetes-sigs/sig-storage-local-static-provisioner)
- `CKAD_Ders_24_persistent_volumes_pv_pvc.pdf` — bu klasörde, slayt seti
- `CKAD_Ders_25_storageclass.pdf` — StorageClass detayları
