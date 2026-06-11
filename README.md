# Kubernetes 101 Workshop

İki günlük, Docker bilgisi olan geliştiriciler için Kubernetes giriş kursu — tüm eğitim materyalleri tek repoda.

## İçerik

```
.
├── docs/                     Eğitmen dokümantasyonu ve sınav
│   ├── mufredat.pdf            38 sayfa — modül modül detaylı eğitmen rehberi
│   ├── on-degerlendirme-sinavi.pdf   10 soru + cevap anahtarı + seviye yorumlama
│   └── kaynaklar.md            Kurs sonrası okuma listesi, sertifikasyon
│
├── labs/                     Hands-on lab klasörleri — her klasör kendi başına çalıştırılır
│   │                           — Temel müfredat (01-12) —
│   ├── 01-namespace/           Namespace tanımı + label/selector
│   ├── 02-pod/                 Pod yaratma, sidecar, lifecycle
│   ├── 03-replicaset/          Self-healing
│   ├── 04-deployment/          Rolling update, rollback
│   ├── 05-service/             ClusterIP, NodePort, DNS, endpoints
│   ├── 06-configmap-secret/    env + volume mount, canlı tazeleme
│   ├── 07-volume-pvc/          emptyDir vs PVC kalıcılık karşılaştırması
│   ├── 08-probes/              Startup probe + liveness davranışı
│   ├── 09-readiness-probes/    Readiness toggle, endpoint listesi
│   ├── 10-resource-limit-request-limit/   requests/limits, OOMKilled, throttle
│   ├── 11-ingress/             path-based + host-based routing
│   ├── 12-hpa/                 HorizontalPodAutoscaler
│   │                           — İleri konular (13-18) —
│   ├── 13-multi-container/     Init, sidecar (klasik+native), ambassador, adapter
│   ├── 14-serviceaccount/      SA, Role/RoleBinding, ClusterRole, RBAC test
│   ├── 15-securitycontext/     runAsNonRoot, readOnlyRootFS, capabilities, fsGroup
│   ├── 16-networkpolicy/       Deny-all, label/namespace selector, egress DNS
│   ├── 17-taint-toleration/    Taint effect'leri, toleration, NoExecute, DaemonSet
│   ├── 18-nodeaffinity/        required/preferred, podAffinity, topologySpread
│   │                           — Kapanış —
│   └── 19-kapanis-projesi/     Tüm konuları birleştir + 5 hata enjeksiyonu
│
├── playground-app/           .NET 8 MVC test uygulaması (her K8s konusu için bir sayfa)
│   ├── src/                    ASP.NET Core MVC kaynak kodu
│   ├── k8s/                    Tam manifest seti
│   └── Dockerfile
│
├── build/                    PDF üretim script'leri (eğitmen kullanımı)
│   ├── build_detailed_doc.py   Detaylı eğitmen dokümanı build
│   ├── doc_diagrams.py         11 SVG diyagram tanımı
│   └── build_pdfs.py           Kısa müfredat + sınav build
│
├── CHANGELOG.md
├── LICENSE
└── README.md (bu dosya)
```

## Hızlı Başlangıç

### Önkoşullar
- Çalışan Docker
- Minikube + kubectl kurulu
- En az 4 GB boş RAM

```bash
minikube start --driver=docker --cpus=2 --memory=4g
minikube addons enable metrics-server
minikube addons enable ingress
```

### İlk lab — Pod

```bash
cd labs/01-pod
kubectl apply -f pod.yaml
kubectl get pods -o wide
```

### Kapanış projesi — Playground app

```bash
cd playground-app
docker build -t docker.io/cahityusuf/k8s-playground:v1.0.1 .
minikube image load docker.io/cahityusuf/k8s-playground:v1.0.1
kubectl apply -f k8s/
kubectl -n playground port-forward svc/playground 8080:80
# tarayıcı: http://localhost:8080
```

## Kurs Programı (Kurulum hariç)

| Modül | Süre | Konu |
|---|---:|---|
| M1 | 45 dk | Kubernetes Mimarisi |
| M2 | 120 dk | Pod |
| M3 | 120 dk | ReplicaSet & Deployment |
| M4 | 120 dk | Service ve Ağ Modeli |
| M5 | 90 dk | ConfigMap & Secret |
| M6 | 90 dk | Volume, PV ve PVC |
| M7 | 45 dk | Namespace, Label, Annotation |
| M8 | 75 dk | Resource Yönetimi ve Probe'lar |
| M9 | 60 dk | Ingress |
| M10 | 90 dk | Kapanış Projesi & Sorun Giderme |

Toplam: ≈ 14 saat / 2 gün.

## Eğitmen Kullanımı

PDF'leri yeniden üretmek için:

```bash
cd build
pip install reportlab pypdf --break-system-packages
python3 build_detailed_doc.py     # → ../docs/mufredat.pdf konumuna kopyalayın
python3 build_pdfs.py             # kısa müfredat + sınav PDF'leri
```

## Lisans

[MIT](LICENSE)

## Katkı

Hata, eksik bilgi veya iyileştirme önerileri için Issue açabilirsiniz.
