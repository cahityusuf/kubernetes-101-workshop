# Lab 12 — HorizontalPodAutoscaler (HPA)

**Süre:** ~45-60 dk
**Müfredat referansı:** Modül 9 (Autoscaling)
**Önkoşul:** Lab 10 (resources/requests/limits) tamamlanmış olmalı.

## Hedef

Kursiyer:
1. **Metrics-server**'ın HPA için neden zorunlu olduğunu anlar.
2. `resources.requests.cpu`'nun HPA hesabındaki rolünü kavrar.
3. Bir Deployment'ı tek tıkla CPU yüküne sokup HPA'nın replikaları **otomatik artırıp azaltmasını** gözlemler.
4. `scaleUp` / `scaleDown` davranış (behavior) ayarlarının pratik etkisini görür.

## Dosyalar

| Dosya | Görev |
|---|---|
| `deployment.yaml` | Namespace + stateless Deployment (replicas:2, RollingUpdate) + Service |
| `hpa.yaml` | HorizontalPodAutoscaler v2: CPU %60 / Mem %80, min:2 max:8, davranış ayarları |
| `README.md` | Bu rehber |

## HPA hesabı (özet)

### Formül

Kubernetes HPA controller'ının kullandığı **resmi formül**:

```
desiredReplicas = ⌈ currentReplicas × ( currentMetricValue / desiredMetricValue ) ⌉
```

CPU `averageUtilization` metriği için açılımı:

```
utilization (%)  = ( avg(pod_cpu_kullanımı) / container.requests.cpu ) × 100
desiredReplicas  = ⌈ currentReplicas × ( utilization / targetUtilization ) ⌉
```

> `⌈ ⌉` = yukarı yuvarlama (`ceil`). Sonuç her zaman `[minReplicas, maxReplicas]` aralığına **kelepçelenir** (clamp).
> **Tolerance** varsayılan **±%10**: oran `0.9 – 1.1` arasındaysa HPA hiçbir aksiyon almaz (flapping önleme).
> `resources.requests.cpu` **tanımlı değilse** HPA yüzde hesaplayamaz → `TARGETS: <unknown>/60%`.

### Bu lab'ın parametreleri

| Parametre | Değer |
|---|---|
| `resources.requests.cpu` | `100m` (= 0.1 core) |
| `target` (`averageUtilization`) | `%60` → Pod başına ortalama **60m** CPU eşiği |
| `minReplicas` / `maxReplicas` | `2` / `8` |
| Başlangıç `replicas` | `2` |

### Örnek hesaplama — Scale-UP

**T+0** — Stress endpoint tetiklendi, **her Pod 120m CPU** yakıyor (2 Pod var):

```
utilization     = (120m / 100m) × 100 = %120
oran            = 120 / 60 = 2.0     (tolerance ±%10 dışında → aksiyon)
desiredReplicas = ⌈ 2 × 2.0 ⌉ = ⌈ 4 ⌉ = 4
```

→ HPA replicas: **2 → 4**.

**T+30 sn** — 4 Pod var, yük dağıldı ama hâlâ yüksek; ortalama **107m**:

```
utilization     = (107m / 100m) × 100 = %107
oran            = 107 / 60 ≈ 1.78
desiredReplicas = ⌈ 4 × 1.78 ⌉ = ⌈ 7.13 ⌉ = 8   (maxReplicas'a kelepçelendi)
```

→ HPA replicas: **4 → 6 → 8** (her tur `behavior.scaleUp.policies` ile sınırlı).

### Örnek hesaplama — Scale-DOWN

**T+0** — Yük durduruldu, 8 Pod var, ortalama **1m** kullanım:

```
utilization     = (1m / 100m) × 100 = %1
oran            = 1 / 60 ≈ 0.017
desiredReplicas = ⌈ 8 × 0.017 ⌉ = ⌈ 0.13 ⌉ = 1   →   minReplicas=2 kelepçesi devrede
```

→ Teorik hedef 1, fakat `minReplicas=2` kelepçesi devreye girer. Üstüne `behavior.scaleDown.stabilizationWindowSeconds: 120` ve `policies` (60 sn'de 1 Pod) nedeniyle gerçek iniş **adım adım**: `8 → 7 → 6 → … → 2`.

### Tolerance sınırı — aksiyon yok örneği

3 Pod var, ortalama **62m** kullanım:

```
utilization     = (62m / 100m) × 100 = %62
oran            = 62 / 60 ≈ 1.033     (|1.033 − 1| = 0.033 < 0.10 → tolerance içinde)
desiredReplicas = currentReplicas     (HPA hiçbir şey yapmaz)
```

---

## Adım 1 — `metrics-server` kontrolü ve kurulumu

HPA çalışmak için Pod CPU/memory metriklerini `metrics-server`'dan okur. Önce kontrol:

```bash
kubectl top nodes
```

**Çıktı geliyorsa hazırsınız → Adım 2'ye geçin.**

`Metrics API not available` görüyorsanız kurulum:

```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

### Tek-node bare-metal (kubeadm) kümelerde ek patch

Kubelet'in TLS sertifikası IP SAN içermediği için ilk kurulumda metrics-server scrape'i başarısız olur (`x509: cannot validate certificate ... doesn't contain any IP SANs`). Çözüm:

```bash
kubectl -n kube-system patch deployment metrics-server --type='json' -p='[
  {"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}
]'
```

30-60 sn sonra metrics-server hazır olur:

```bash
kubectl -n kube-system get pod -l k8s-app=metrics-server
kubectl top pod -n kube-system | head
```

> Üretim kümelerinde `--kubelet-insecure-tls` **kullanmayın**; bunun yerine kubelet sertifikasına IP SAN ekleyin.

---

## Adım 2 — Deployment'ı uygula

```bash
kubectl apply -f deployment.yaml
kubectl -n hpa-demo get pod -w
```

İki Pod `Running` olduğunda **CTRL+C** ile çıkın. Doğrulama:

```bash
# CPU isteğinin gerçekten 100m olduğunu kanıtla (HPA bu değeri kullanacak)
kubectl -n hpa-demo describe pod -l app=hpa-demo | grep -A 2 'Requests:'
```

> **Henüz HPA YOK.** Replicas: 2 sabittir.

---

## Adım 3 — HPA'yı uygula

```bash
kubectl apply -f hpa.yaml
kubectl -n hpa-demo get hpa hpa-demo
```

İlk durum (idle):

```
NAME       REFERENCE              TARGETS                       MINPODS   MAXPODS   REPLICAS
hpa-demo   Deployment/hpa-demo    cpu: 1%/60%, memory: 8%/80%   2         8         2
```

> HPA ilk 30-60 sn `<unknown>` gösterebilir — metrics-server'ın ilk scrape'ini bekler.

---

## Adım 4 — İzlemeyi başlat (iki terminal)

**Terminal A** — HPA + Pod listesi (her 2 sn):

```bash
watch -n2 'kubectl -n hpa-demo get hpa,pod -l app=hpa-demo'
```

**Terminal B** — Per-Pod CPU kullanımı:

```bash
watch -n2 'kubectl -n hpa-demo top pod'
```

---

## Adım 5 — Sürekli CPU yükü oluştur

Uygulamada bunun için özel bir endpoint var: `/Stress/StartLoad` (kapatana kadar yük üretir).

**Yöntem A — Tarayıcı:**

```bash
kubectl -n hpa-demo port-forward svc/hpa-demo 8080:80
# Tarayıcı: http://localhost:8080/Stress
# "Sürekli CPU Yükü" kartı → Worker: 2 → Başlat
```

**Yöntem B — CLI:**

```bash
kubectl -n hpa-demo port-forward svc/hpa-demo 8080:80 &
sleep 2
curl -X POST -d "workers=2" http://localhost:8080/Stress/StartLoad
```

Doğrulama (metrics endpoint'inden):

```bash
curl -s http://localhost:8080/metrics | grep app_load
# app_load_workers 2
# app_load_seconds_total 4.521
```

---

## Adım 6 — Scale-up'ı gözlemle (60-120 sn)

Terminal A'da beklenen seyir:

```
TARGETS              REPLICAS
cpu: 110%/60%        2          ← T+0    eşik aşıldı
cpu: 107%/60%        4          ← T+30   2 Pod eklendi
cpu:  85%/60%        6          ← T+60   yetmedi, 2 Pod daha
cpu:  74%/60%        8          ← T+90   max'a ulaşıldı
```

`SuccessfulRescale` event'lerini görmek için:

```bash
kubectl -n hpa-demo describe hpa hpa-demo | tail -15
```

> **Bir Pod yüksek, diğerleri düşük mü?**
> Uygulamadaki `BackgroundLoad` her Pod'da bağımsız bir singleton. `port-forward` sadece bir Pod'a yapışır → curl o Pod'a düşer → o Pod yakar. HPA **ortalamaya** baktığı için yine doğru kararı verir. Yükü tüm Pod'lara yaymak isterseniz Service üzerinden eşzamanlı çoklu istek (`hey`, `wrk`) basın.

---

## Adım 7 — Yükü durdur, scale-down'ı gözlemle

**Yöntem A** — Tarayıcı: `/Stress` → **Durdur**
**Yöntem B** — CLI:

```bash
curl -X POST http://localhost:8080/Stress/StopLoad
```

`behavior.scaleDown.stabilizationWindowSeconds: 120` nedeniyle replikalar **~2 dk** sabit kalır, sonra `behavior.scaleDown.policies` gereği **her 60 sn'de 1 Pod** düşer:

```
TARGETS         REPLICAS
cpu: 1%/60%     8     ← T+0      yük durdu
cpu: 1%/60%     8     ← T+120    stabilizationWindow bitti
cpu: 1%/60%     7     ← T+180
cpu: 1%/60%     6     ← T+240
cpu: 1%/60%     5     ← T+300
cpu: 1%/60%     4     ← T+360
cpu: 1%/60%     3     ← T+420
cpu: 1%/60%     2     ← T+480    minReplicas'a ulaşıldı
```

> **Neden hemen düşmüyor?** "Flapping" (sürekli yukarı-aşağı oynama) önlemek için. Üretimde 5-10 dk stabilization tercih edilir.

---

## Tartışma soruları (sınıf için)

1. `resources.requests.cpu`'yu `50m`'e düşürürseniz HPA daha **erken mi yoksa geç mi** tetiklenir? Neden?
2. `maxReplicas: 8` yetmedi varsayalım. Düğüm bittiyse ne olur? (`Pending` Pod'lar, Cluster Autoscaler konusu.)
3. PVC ReadWriteOnce ile bu deployment'ı çalıştırsaydınız ne hata alırdınız? (`MultiAttachError`)
4. HPA neden Job/CronJob için **tasarlanmamıştır**? (Geçici görevler, ölçeklenebilir uzun süreli işler değil.)
5. `Memory`'ye göre scale yapmak neden tehlikelidir? (Bellek serbest bırakmak zordur — yük düşse bile Pod azalmayabilir.)

---

## Temizlik

```bash
kubectl delete -f hpa.yaml
kubectl delete -f deployment.yaml
# kısa yolu:
kubectl delete namespace hpa-demo
```

---

## Yaygın sorunlar

| Belirti | Olası neden | Çözüm |
|---|---|---|
| HPA `TARGETS: <unknown>/60%` | metrics-server hazır değil veya yok | Adım 1'i tekrar et |
| `FailedGetResourceMetric: no metrics returned` | Pod henüz ready değil veya metrics-server kubelet'e ulaşamıyor | `--kubelet-insecure-tls` patch'i + 60 sn bekle |
| Yük başlattım ama scale-up olmuyor | `resources.requests.cpu` tanımlı değil → HPA % hesaplayamaz | `deployment.yaml`'i kontrol et |
| Replikalar artıyor ama Pod'lar `Pending` | Node'da kaynak kalmamış | `kubectl describe node` → Allocatable; daha küçük requests veya yeni node |
| HPA scale-down yapmıyor (uzun süre) | `scaleDown.stabilizationWindow` çok yüksek | manifest'i ayarla veya bekle (varsayılan 5 dk) |
