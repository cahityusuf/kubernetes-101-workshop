# Lab 08 — Kapanış Projesi

**Süre:** ~90 dk | **Müfredat referansı:** Modül 10

## Hedef

Kursta öğrenilen tüm yapıları tek bir uygulamada birleştirmek + sorun giderme pratiği.

## Senaryo

`playground` namespace'inde, [`playground-app`](../../playground-app/) (ASP.NET Core MVC)
uygulaması ile şunları içeren bir sistem ayağa kalkar:

- **Namespace** — `playground`
- **ConfigMap** — uygulama ayarları
- **Secret** — DB parolası
- **PVC** — `/data` için kalıcı depolama
- **Deployment** — 2 replika, init container, 3 probe, lifecycle preStop
- **Service** — ClusterIP + NodePort
- **Ingress** — `playground.local` üzerinden dış erişim
- **HPA** — CPU %60'ı aşınca 2→6 replika

## Hızlı kurulum

```bash
cd ../../playground-app
docker build -t docker.io/cahityusuf/k8s-playground:v1.0.1 .
minikube image load docker.io/cahityusuf/k8s-playground:v1.0.1
kubectl apply -f k8s/
kubectl -n playground get all
kubectl -n playground port-forward svc/playground 8080:80
# tarayıcı: http://localhost:8080
```

## Eğitmenin enjekte edebileceği 5 hata

Kursiyerlerden 30 dakika içinde bulmaları beklenir. Tanı için
`kubectl describe`, `kubectl logs --previous`, `kubectl get events` üçlüsü.

### Hata 1 — Yanlış image tag

`k8s/04-deployment.yaml` içinde `image: docker.io/cahityusuf/k8s-playground:v1.0.1` → `k8s-playground:9.9.9`.

**Beklenen tanı:** ImagePullBackOff. `kubectl describe pod` Events bölümünde
"Failed to pull image" görünür.

### Hata 2 — Selector mismatch

`k8s/05-service.yaml` içinde `selector: app: playground` → `app: playGround` (büyük G).

**Beklenen tanı:** `kubectl get endpoints playground` boş döner; Pod'lar Ready ama
Service trafik almıyor.

### Hata 3 — readiness path yanlış

`readinessProbe.httpGet.path: /healthz/ready` → `/healthz/yanlis`.

**Beklenen tanı:** Pod'lar sürekli "0/1 Ready". `kubectl describe pod` probe sonuçları.

### Hata 4 — Bellek limit'i çok düşük

`resources.limits.memory: 256Mi` → `64Mi`.

**Beklenen tanı:** Pod başlar ama hızla OOMKilled. `kubectl describe pod`
"Last State: Terminated, Reason: OOMKilled, Exit Code: 137".

### Hata 5 — ConfigMap adı yanlış

`envFrom: configMapRef: name: playground-config` → `playground-cofig` (typo).

**Beklenen tanı:** Pod CreateContainerConfigError. `kubectl describe pod`:
"configmap 'playground-cofig' not found".

## Lab akışı önerisi

| Süre | Aktivite |
|---|---|
| 0–15 dk | Manifest'leri grup halinde gözden geçir, her nesnenin görevini söyle |
| 15–60 dk | Eğitmen 3 hata enjekte eder; gruplar hatayı bulup düzeltir |
| 60–80 dk | Rolling update + rollback + HPA tetikleme demosu (Stress sayfasından) |
| 80–90 dk | Sınıfta kısa Q&A; cluster temizliği |

## Temizlik

```bash
kubectl delete namespace playground
```
