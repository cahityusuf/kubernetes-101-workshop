# Multi-Container Pod Patterns

İleri konu — bir Pod içinde birden çok konteyner kullanmanın klasik desenleri.

## Neden multi-container?

Pod, dağıtımın **en küçük birimidir** ve içindeki konteynerler şunları paylaşır:

- **Aynı ağ ad uzayı** (aynı IP — birbirine `localhost` ile ulaşır)
- **Aynı IPC ad uzayı** (paylaşılan POSIX semafor, signal, vs.)
- **Paylaşılan volume'ler**
- **Yaşam döngüsü** (birlikte yaratılır, birlikte ölür)

Bu sayede yardımcı işlevleri (log toplama, proxy, dönüştürme) ayrı bir Pod'da değil
aynı Pod'da çalıştırmak doğru olabilir.

## Beş klasik desen

| Desen | Amaç | Tipik örnek |
|---|---|---|
| **Init Container** | Ana konteynerlerden ÖNCE çalışır, tamamlanmadan diğerleri başlamaz. | DB migration, beklemek, dosya indirme |
| **Sidecar (klasik)** | Ana ile paralel çalışır, yardımcı işlev sağlar. | Log shipper, metrics exporter |
| **Sidecar (native — 1.28+)** | `restartPolicy: Always` ile tanımlanan init container. Ana başlamadan önce hazır olur, ana boyunca yaşar. | Aynı ama daha güvenli |
| **Ambassador** | Ana konteynerin dış servislere localhost üzerinden konuşmasını sağlar. | Redis cluster proxy, mTLS adaptör |
| **Adapter** | Ana konteynerin çıktısını standart bir biçime dönüştürür. | Legacy log → Prometheus metrics |

## Önemli kavramlar

### Init container kuralları

- **Sırayla** çalışır (`initContainers` listesindeki sırada).
- Hepsi başarılı tamamlanmadan ana `containers` başlamaz.
- Fail olursa Pod'un `restartPolicy`'sine göre yeniden denenir.
- Ayrı resources/securityContext tanımlayabilir.
- Probe'ları YOKTUR.

### Klasik sidecar problemi

Klasik sidecar düzeninde sidecar konteyner ana konteynerden **sonra** veya **paralel** başlar.
Sorunlar:
- Ana çıkış yaparsa Job/CronJob'lar tamamlanamaz (sidecar sürekli çalışır → Pod hiç bitmez).
- Ana başlar başlamaz log üretmeye başlar; sidecar henüz hazır olmayabilir → ilk loglar kaybolur.

### Native sidecar (1.29 stable) çözümü

`initContainers` altında ama `restartPolicy: Always` ile tanımlanır:

- Init container gibi **ana'dan ÖNCE başlar** ve hazır olduğunda ana başlar.
- Init container'ın aksine **ana boyunca yaşar**.
- Ana exit ettiğinde sidecar da gracefully kapanır.
- Job/CronJob ile uyumludur.

### Paylaşımlar — net haritada

| Paylaşılan | Otomatik | Notlar |
|---|---|---|
| Ağ (IP, port) | Evet | `localhost:8080` ile birbirine erişir |
| IPC | Evet | POSIX shared memory, semaphores |
| Hostname | Evet | `hostname` her konteynerde aynı |
| PID ns | Hayır | `spec.shareProcessNamespace: true` ile açılır |
| Dosya sistemi | Hayır | Volume mount gerekli (emptyDir tipik) |

## Lab Senaryosu

### 1) Init container — başlamak için bekle

```bash
kubectl apply -f 01-init-container.yaml
kubectl get pod init-demo -w
# Önce STATUS = Init:0/1 → sonra PodInitializing → sonra Running
kubectl logs init-demo -c wait-for-db
kubectl logs init-demo -c app
```

### 2) Sıralı init container'lar

```bash
kubectl apply -f 02-init-containers-sequential.yaml
kubectl get pod sequential-init -o jsonpath='{.status.initContainerStatuses[*].state}'
# Her birinin sırayla terminate olduğunu gör
kubectl logs sequential-init -c step-1
kubectl logs sequential-init -c step-2
```

### 3) Klasik sidecar — log shipper

```bash
kubectl apply -f 03-sidecar-classic-log-shipper.yaml
kubectl logs sidecar-classic -c app          # app'in yazdığı loglar
kubectl logs sidecar-classic -c log-shipper  # sidecar'ın tail ettiği aynı log
```

### 4) Native sidecar (1.28+)

```bash
kubectl version --short | grep Server   # 1.29+ stable, 1.28 beta
kubectl apply -f 04-sidecar-native-restartpolicy.yaml
kubectl describe pod sidecar-native | grep -A 2 "Init Containers"
# log-shipper init listede ama Always restart → sidecar
kubectl logs sidecar-native -c log-shipper -f
```

### 5) Ambassador — DB proxy

```bash
kubectl apply -f 05-ambassador-proxy.yaml
kubectl exec ambassador-demo -c app -- wget -qO- http://localhost:8000/
# Uygulama localhost:8000'e bağlanır; ambassador hedefe yönlendirir
```

### 6) Adapter — legacy log → Prometheus

```bash
kubectl apply -f 06-adapter-metrics-exporter.yaml
kubectl exec adapter-demo -c metrics-adapter -- wget -qO- http://localhost:9090/metrics
# Custom format log → Prometheus formatına dönüştürülmüş
```

### 7) Paylaşılan volume + IPC ile koordinasyon

```bash
kubectl apply -f 07-shared-volume-ipc.yaml
kubectl logs shared-pod -c writer
kubectl logs shared-pod -c reader
kubectl exec shared-pod -c reader -- ls -la /shared
```

## Hangi deseni ne zaman?

| Ne istiyorsun? | Desen |
|---|---|
| Ana başlamadan bir hazırlık yap | Init container |
| Birden çok hazırlık adımı | Birden çok init container (sıralı) |
| Sürekli log topla | Sidecar (mümkünse native) |
| Servis yapısını gizle, localhost ver | Ambassador |
| Çıktıyı standart biçime çevir | Adapter |
| Konteynerler birbirinin process'lerini görsün | `shareProcessNamespace: true` |

## Sık karşılaşılan hatalar

| Hata | Sebep |
|---|---|
| Init container sonsuz `Init:0/1` kalıyor | Beklediği koşul gerçekleşmiyor — DNS, Service, izin |
| Sidecar Job/CronJob'u "Completed" yapmıyor | Klasik sidecar Job'la çakışır; native sidecar veya `shareProcessNamespace + kill` çözer |
| Ana konteyner sidecar'ın logları kaybolmuş | Klasik sidecar ana'dan SONRA başlamış olabilir; native sidecar veya init container kullan |
| Volume içinde dosya yok | Volume mount tüm konteynerlere aynı path'le yapılmamış |
| localhost'a bağlanamıyor | İki konteyner aynı portu mu dinliyor? Port çakışması |

## Temizlik

```bash
kubectl delete -f .
```

## İleri Detaylar

- **`shareProcessNamespace: true`** — Pod-level. Konteynerler birbirinin process'lerini görür (`kill` ile sinyal gönderebilir). Üretim için dikkatli.
- **Service Mesh sidecar'ları** (Istio Envoy, Linkerd proxy) — automatic sidecar injection (mutating admission webhook) ile yapılır.
- **Kubelet'in sidecar termination sırası** (1.29+): native sidecar'lar ana konteynerlerden SONRA durdurulur.
- **Pod readiness ve native sidecar**: Pod Ready sayılması için ana + tüm native sidecar'lar Ready olmalı.
- **Job + native sidecar uyumu**: 1.29+ ile Job'lar doğru biten Pod'larda native sidecar'ı gracefully kapatır.
