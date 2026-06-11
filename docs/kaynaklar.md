# Kurs Sonrası Kaynaklar ve Yol Haritası

Bu rehber kursta öğrendiklerinin üstüne nereye gidebileceğini gösterir.

## Repo İçindeki İleri Konu Örnekleri

Kurs ana modülleri (Pod → Ingress) tamamlandıktan sonra incelenmek üzere
`docs/` altında ileri konular için README + YAML setleri vardır:

- **`docs/serviceaccount/`** — ServiceAccount, Role/RoleBinding, ClusterRole,
  RBAC ile API erişimi testi.
- **`docs/securitycontext/`** — runAsNonRoot, readOnlyRootFilesystem,
  capabilities drop, fsGroup, seccomp; Pod Security Standards bağlantısı.
- **`docs/networkpolicy/`** — Default-deny ingress/egress, podSelector ve
  namespaceSelector ile L3/L4 firewall, DNS istisnası.

Her klasörde adım adım çalıştırma talimatı ve beklenen çıktı vardır.


## Resmî Kaynaklar

- **Kubernetes Dokümantasyonu** — https://kubernetes.io/docs/
- **kubectl Cheat Sheet** — https://kubernetes.io/docs/reference/kubectl/quick-reference/
- **K8s API Referansı** — https://kubernetes.io/docs/reference/kubernetes-api/

## Pratik Yapma Ortamları

- **Killercoda** (ücretsiz, tarayıcı) — https://killercoda.com/kubernetes
- **Play with Kubernetes** — https://labs.play-with-k8s.com/
- **kind** (Kubernetes in Docker) — çoklu Node simülasyonu
- **k3d** — k3s tabanlı hafif lokal cluster

## Konularına Göre İleri Okuma

### Paket Yönetimi
- **Helm** — uygulamalar için "yum/apt" gibi. `helm install`
- **Kustomize** — manifest katmanlama (base + overlays)

### GitOps
- **ArgoCD** — git'i source of truth yapan declarative deployment
- **Flux** — benzer alternatif

### Autoscaling
- **HPA** — yatay (replika sayısı) — kursta yapıldı
- **VPA** — dikey (request/limit otomatik)
- **Cluster Autoscaler** — Node sayısını otomatik ayarlar
- **KEDA** — event-driven autoscaling (kuyruk uzunluğu, Kafka lag vs.)

### Güvenlik
- **RBAC** — rol tabanlı erişim kontrolü
- **Pod Security Standards** — restricted/baseline/privileged profilleri
- **NetworkPolicy** — Pod-to-Pod trafik kontrolü (CNI desteği şart)
- **OPA / Gatekeeper / Kyverno** — policy as code

### Servis Ağı
- **Service Mesh: Istio / Linkerd** — mTLS, traffic shifting, observability
- **Gateway API** — Ingress'in modern halefi (1.27+ GA)

### State'ful Uygulamalar
- **StatefulSet** — sıralı, kalıcı kimlikli Pod'lar (veritabanları için)
- **Operators / CRD** — domain-specific controller yazımı
- **Operator Pattern** kitabı — Jason Dobies, Joshua Wood

### Observability
- **Prometheus + Grafana** — metrik toplama ve görselleştirme
- **Loki / Elasticsearch** — log toplama
- **Jaeger / Tempo** — distributed tracing
- **OpenTelemetry** — birleşik instrumentation

## Sertifikasyon Yolları (CNCF)

| Sertifika | Kime? | Süre | Tahmini hazırlık |
|---|---|---|---|
| **CKAD** (Application Developer) | Geliştiriciler | 2 saat | 2-3 ay (kurstan sonra ilk hedef) |
| **CKA** (Administrator) | DevOps/SRE | 2 saat | 3-4 ay |
| **CKS** (Security Specialist) | Güvenlik uzmanları | 2 saat | CKA sonrası 2-3 ay |

Tüm sınavlar pratik (terminal başında problem çözme).

### CKAD için pratik

- **killer.sh** — ücretli ama sınav-benzeri simülator (sertifika alımıyla 2 ücretsiz hak)
- **kubernetes/community/sig-app-delivery** — GitHub'da örnek senaryolar

## Kitaplar

- **Kubernetes Up & Running** — Brendan Burns, Joe Beda, Kelsey Hightower
- **Programming Kubernetes** — Michael Hausenblas, Stefan Schimanski (operator yazımı)
- **The Kubernetes Book** — Nigel Poulton (gentle intro)

## Topluluk

- **Kubernetes Slack** — https://slack.k8s.io/
- **r/kubernetes** — Reddit
- **CNCF YouTube** — KubeCon konuşmaları
- **Türkiye Kubernetes Topluluğu** — Discord/Telegram grupları

## Sonraki Adım Önerisi

Kurstan sonra ilk 4 hafta:

1. **Hafta 1–2:** Her gün 30 dk killercoda senaryosu
2. **Hafta 3:** Kendi uygulamanızı (basit bir REST API + Postgres) lokal cluster'da çalıştırın — Helm chart yazın
3. **Hafta 4:** Helm chart'ı bir GitHub repo'ya koyun, ArgoCD ile minikube'e otomatik deploy edin

Bu 4 haftalık akış CKAD hazırlığının yarısını yapar.
