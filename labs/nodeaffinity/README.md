# NodeAffinity, PodAffinity, TopologySpread

İleri konu — Pod scheduling kontrolü. Klasör çifti: Taint/Toleration (iten) vs Affinity (cezbeden).

## 3 mekanizma karşılaştırması

| Mekanizma | Ne yapar |
|---|---|
| **nodeSelector** | En basit yöntem; sadece `key=value` eşleşmesi. Eski ama hâlâ geçerli. |
| **nodeAffinity** | Daha esnek; In/NotIn/Exists operatörleri, required/preferred. nodeSelector'ın modern halefi. |
| **podAffinity / podAntiAffinity** | Diğer Pod'larla aynı/farklı Node-Zone'da olma. |
| **topologySpreadConstraints** | Modern alternatif; Pod'ları belirli bir topolojide eşit dağıtma (Zone, Node). |

## nodeAffinity — required vs preferred

| Tip | Davranış | Sonek |
|---|---|---|
| `requiredDuringSchedulingIgnoredDuringExecution` | **Hard kural**. Eşleşme yoksa Pod Pending. | "olmazsa olmaz" |
| `preferredDuringSchedulingIgnoredDuringExecution` | **Soft kural**. weight ile tercih. Eşleşme yoksa yine yerleştirilir. | "varsa iyi olur" |

> **IgnoredDuringExecution:** Pod schedule olduktan SONRA Node label'ı değişirse bu Pod taşınmaz. (Migration için `RequiredDuringExecution` alpha aşamasında.)

## Operatörler

| Operatör | Anlam |
|---|---|
| `In` | Değer listede |
| `NotIn` | Değer listede değil |
| `Exists` | Label var (değer önemsiz) |
| `DoesNotExist` | Label yok |
| `Gt` | Sayısal: büyük (sadece bir değer) |
| `Lt` | Sayısal: küçük |

## Önemli Node label'ları

| Label | Kaynak |
|---|---|
| `kubernetes.io/hostname` | Her zaman var; Node adı |
| `kubernetes.io/os` | linux / windows |
| `kubernetes.io/arch` | amd64 / arm64 |
| `topology.kubernetes.io/zone` | (bulutta) availability zone |
| `topology.kubernetes.io/region` | (bulutta) region |
| `node.kubernetes.io/instance-type` | (bulutta) m5.large, n1-standard-4 vs. |

Kullanıcı kendi etiketlerini ekleyebilir: `kubectl label nodes minikube-m02 disk=ssd workload=gpu`.

## Lab Senaryosu

> **Önkoşul:** Multi-node minikube.
> ```bash
> minikube start --nodes=3 --driver=docker --cpus=2 --memory=4g
> kubectl label nodes minikube-m02 disk=ssd workload=gpu
> kubectl label nodes minikube-m03 disk=hdd
> kubectl get nodes --show-labels | head
> ```

### 1) nodeSelector (legacy, en basit)

```bash
kubectl apply -f 01-pod-nodeselector-legacy.yaml
kubectl get pod legacy-selector -o wide
# m02'de — çünkü disk=ssd
```

### 2) Required nodeAffinity (hard rule)

```bash
kubectl apply -f 02-pod-nodeaffinity-required.yaml
kubectl get pod hard-rule -o wide
# m02'ye yerleşmek ZORUNDA
```

### 3) Preferred nodeAffinity (soft rule + weight)

```bash
kubectl apply -f 03-pod-nodeaffinity-preferred.yaml
kubectl get pod soft-rule -o wide
# m02'ye yerleşmeyi TERCİH eder ama başka Node'a da gidebilir
```

### 4) Multiple terms — AND ile OR mantığı

```bash
kubectl apply -f 04-pod-nodeaffinity-multiple-terms.yaml
# Bir nodeSelectorTerm içindeki matchExpressions → AND
# Birden çok nodeSelectorTerm → OR
```

### 5) PodAffinity — backend ile aynı Node'da çalış

```bash
# Önce backend Pod'u aç (etiket: app=backend)
kubectl run backend --image=nginx:1.27 --labels=app=backend
kubectl apply -f 05-pod-podaffinity.yaml
# frontend, backend'in olduğu Node'a yerleşir
```

### 6) PodAntiAffinity — aynı Node'da iki replika olmasın

```bash
kubectl apply -f 06-pod-podantiaffinity-deployment.yaml
kubectl get pods -l app=web-ha -o wide
# 3 replika, 3 farklı Node'da
```

### 7) TopologySpread — modern alternatif

```bash
kubectl apply -f 07-deployment-topologyspread.yaml
kubectl get pods -l app=spread-demo -o wide
# Pod'lar Node'lar arasında eşit dağılır (skew ≤ 1)
```

## Hangisini ne zaman kullanmalı?

| Durum | Tavsiye |
|---|---|
| Sadece label eşleşmesi | `nodeSelector` (en sade) |
| Esnek hard/soft kurallar | `nodeAffinity` |
| Mikroservis A, B'ye yakın olsun | `podAffinity` (latency için) |
| Replikalar farklı Node'da | `podAntiAffinity` veya `topologySpreadConstraints` |
| Zone/Region bazlı eşit dağıtım | `topologySpreadConstraints` (önerilen) |

## Sık hatalar

| Hata | Sebep |
|---|---|
| Pod Pending kalıyor | required kural hiçbir Node ile eşleşmiyor; `kubectl describe pod` Events. |
| podAffinity etkisini görmüyorum | `topologyKey` yanlış — hostname yerine zone yazmış olabilirsiniz. |
| topologySpread Pod'u yine de aynı Node'a koyuyor | `whenUnsatisfiable: ScheduleAnyway` (soft) seçilmiş; `DoNotSchedule` ile hard yapın. |

## Temizlik

```bash
kubectl delete -f .
kubectl label nodes minikube-m02 disk- workload- 2>/dev/null
kubectl label nodes minikube-m03 disk- 2>/dev/null
```

## İleri Detaylar

- **AffinityDuringExecution** (alpha): label değişince Pod'ları taşıma — şu an mümkün değil.
- **Scheduling Profiles & Scheduler Extender**: kendi scheduler mantığınızı entegre edebilirsiniz.
- **Descheduler**: zamanla dengesizleşen yerleşimleri tekrar düzenlemek için.
- **kubectl get pods -o custom-columns=NAME:.metadata.name,NODE:.spec.nodeName** — yerleşim hızlı kontrolü.
