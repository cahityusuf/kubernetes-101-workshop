# Taint & Toleration

İleri konu — Pod scheduling kontrolü. Klasör çifti: NodeAffinity (cezbeden) vs Taint/Toleration (iten).

## Amaç

- **Taint** Node'a uygulanır → "bu Node'a Pod almak istemiyorum, ben özel rezerveyim."
- **Toleration** Pod'a uygulanır → "bu Node'un kuralını tolere edebilirim, beni oraya yerleştirebilirsin."
- Bir Node'un taint'i varsa, **toleration'ı eşleşmeyen Pod o Node'a SCHEDULE EDİLMEZ.**

> Dikkat: Toleration "yerleşim garantisi" değildir. Toleration *bir izindir*; nereye gideceğine scheduler karar verir. Gönderilmesini istiyorsanız ek olarak **nodeSelector / nodeAffinity** kullanın.

## 3 effect — taint'in şiddeti

| Effect | Davranış |
|---|---|
| `NoSchedule` | Yeni Pod'lar bu Node'a yerleştirilmez (mevcutlar kalır). |
| `PreferNoSchedule` | Yumuşak versiyon; scheduler kaçınmaya çalışır, başka çare yoksa yerleştirir. |
| `NoExecute` | Toleransı olmayan **mevcut Pod'lar da tahliye edilir**. tolerationSeconds ile süre verilebilir. |

## Built-in taint'ler — bilinmesi gereken

| Taint | Ne zaman ortaya çıkar |
|---|---|
| `node-role.kubernetes.io/control-plane:NoSchedule` | Control plane Node'larında — user Pod'ları gelmesin. |
| `node.kubernetes.io/not-ready:NoExecute` | Node Not Ready durumuna geçince. |
| `node.kubernetes.io/unreachable:NoExecute` | Kubelet'ten heartbeat gelmiyorsa. |
| `node.kubernetes.io/disk-pressure:NoSchedule` | Node disk doluyor. |
| `node.kubernetes.io/memory-pressure:NoSchedule` | Node RAM baskıda. |
| `node.kubernetes.io/pid-pressure:NoSchedule` | PID sayısı tükeniyor. |
| `node.kubernetes.io/unschedulable:NoSchedule` | `kubectl cordon` ile manuel. |

## Yaygın kullanım senaryoları

- **Adanmış Node'lar:** GPU, ML, ödeme servisi gibi özel workload için Node'ları rezerve etme.
- **Yöneticisel bakım:** `kubectl drain <node>` (cordon + NoExecute taint + Pod evict).
- **Sistem Pod'ları:** DaemonSet'in tüm Node'larda çalışması için her taint'i tolere etmesi.

## Lab Senaryosu

> **Önkoşul:** Multi-node bir cluster ya da en az tek Node'a manuel taint atılabilmesi.
>
> ```bash
> # Multi-node minikube (önerilen)
> minikube delete && minikube start --nodes=3 --driver=docker --cpus=2 --memory=4g
> kubectl get nodes
> # NAME             STATUS   ROLES
> # minikube         Ready    control-plane
> # minikube-m02     Ready
> # minikube-m03     Ready
> ```

### 1) Node'a taint at

```bash
# minikube-m02'yi sadece 'gpu' workload'larına ayır
kubectl taint nodes minikube-m02 workload=gpu:NoSchedule

# Doğrula
kubectl describe node minikube-m02 | grep Taints
# Taints: workload=gpu:NoSchedule
```

### 2) Toleration'ı olmayan Pod → m02'ye gitmez

```bash
kubectl apply -f 01-pod-no-toleration.yaml
kubectl get pod plain-pod -o wide
# NODE sütununda minikube-m02 YOK
```

### 3) Eşleşen toleration → m02'ye yerleşebilir

```bash
kubectl apply -f 02-pod-with-toleration.yaml
kubectl get pod tolerated-pod -o wide
# m02'ye gidebilir (gitmesi şart değil — scheduler karar verir)
# m02'ye GİTSİN diye nodeSelector da kullanmalısınız (bkz. nodeaffinity klasörü)
```

### 4) Exists operatörü — değer önemsiz

```bash
kubectl apply -f 03-pod-tolerate-exists.yaml
# Sadece 'workload' key'inin VAR olması yeter; gpu / cpu / mem fark etmez
```

### 5) NoExecute + tolerationSeconds — graceful eviction

```bash
# Önce m02'deki taint'i NoExecute'a çevir
kubectl taint nodes minikube-m02 workload=gpu:NoSchedule-      # eski taint'i kaldır
kubectl taint nodes minikube-m02 workload=gpu:NoExecute        # NoExecute olarak ekle

kubectl apply -f 05-pod-noexecute-tolerationseconds.yaml
# Pod m02'ye düşerse 60 sn sonra evict edilir
kubectl get pod evict-test -o wide -w
```

### 6) DaemonSet — tüm taint'leri tolere et

```bash
kubectl apply -f 06-daemonset-tolerate-all.yaml
kubectl get pods -l app=log-agent -o wide
# Her Node'da (control-plane dahil) 1 Pod'u olmalı
```

## Taint'i kaldırma

```bash
# Sonuna eksi (-) işareti
kubectl taint nodes minikube-m02 workload=gpu:NoSchedule-
kubectl taint nodes minikube-m02 workload-              # key tüm effect'leriyle kaldırır
```

## Sık karşılaşılan hatalar

| Hata | Sebep |
|---|---|
| "Toleration ekledim ama Pod yine de gitmedi" | Toleration izindir, garanti değil. nodeSelector/nodeAffinity ekleyin. |
| "Control plane Node'a Pod yerleştiremedim" | Default `node-role.kubernetes.io/control-plane:NoSchedule` taint'i var. |
| "Pod cordon Node'dan tahliye olmuyor" | cordon sadece SCHEDULE engelliyor; tahliye için `drain` kullanın. |
| "NoExecute taint'i koydum ama Pod hâlâ duruyor" | Pod'da tolerationSeconds belirtilmemiş — sonsuz tolere eder. |

## Temizlik

```bash
kubectl delete -f .
kubectl taint nodes minikube-m02 workload- 2>/dev/null
```
