# SecurityContext

İleri konu — kursun ana modüllerinden sonra işlenir.

## Amaç

Konteynerin Linux seviyesinde **kim olarak** ve **hangi yetkilerle** çalışacağını belirler.
Üretim kümelerinde **default ayarlar tehlikelidir** — konteyner image'ları sıklıkla
root kullanıcısıyla, dolu capability setiyle ve yazılabilir kök dosya sistemiyle gelir.

## Pod seviyesi vs Container seviyesi

| Alan | Pod seviyesi | Container seviyesi | Hangisi kazanır? |
|---|---|---|---|
| `runAsUser` | ✓ | ✓ | container |
| `runAsGroup` | ✓ | ✓ | container |
| `runAsNonRoot` | ✓ | ✓ | container |
| `fsGroup` | ✓ | ✗ | yalnız Pod |
| `seccompProfile` | ✓ | ✓ | container |
| `capabilities` | ✗ | ✓ | yalnız container |
| `allowPrivilegeEscalation` | ✗ | ✓ | yalnız container |
| `readOnlyRootFilesystem` | ✗ | ✓ | yalnız container |
| `privileged` | ✗ | ✓ | yalnız container |

## En önemli alanlar

| Alan | Anlam |
|---|---|
| `runAsNonRoot: true` | UID 0 ise konteyner başlamaz (CreateContainerError). |
| `runAsUser: 10001` | Süreç bu UID ile çalışır. |
| `runAsGroup: 10001` | Süreç bu GID ile çalışır. |
| `fsGroup: 10001` | Pod'daki tüm volume'lerin grup sahibi bu olur. |
| `allowPrivilegeEscalation: false` | setuid/setgid çağrılarıyla yetki yükseltmeyi engeller. |
| `privileged: false` | Host'a tam erişimi engeller (varsayılan). |
| `readOnlyRootFilesystem: true` | / yazılamaz; sadece volume mount edilen dizinler yazılabilir. |
| `capabilities.drop: ["ALL"]` | Tüm Linux capabilities düşürülür. |
| `capabilities.add: ["NET_BIND_SERVICE"]` | Yalnızca gerekli olanlar geri eklenir (örn. 80 portuna bind). |
| `seccompProfile.type: RuntimeDefault` | Container runtime'ın syscall filtre profili kullanılır. |

## Lab Senaryosu

### 1) Default Pod (sertleştirilmemiş) — neyi izin verdiğini gör

```bash
kubectl apply -f 01-pod-default.yaml
kubectl exec default-pod -- id
# uid=0(root) gid=0(root) groups=0(root) — DİKKAT
kubectl exec default-pod -- sh -c "touch /naughty-file && ls -la /naughty-file"
# root sahipli, kök FS yazılabilir
```

### 2) runAsNonRoot — image root'sa başlatmaz

```bash
kubectl apply -f 02-pod-runasnonroot.yaml
kubectl get pod nonroot-pod
# Status: CreateContainerError (nginx default root çalışır)
kubectl describe pod nonroot-pod | grep -A3 'Last State'
# Reason: containerd: container has runAsNonRoot and image will run as root
```

### 3) readOnlyRootFilesystem — / yazılamaz

```bash
kubectl apply -f 03-pod-readonly-rootfs.yaml
kubectl exec readonly-pod -- sh -c "touch /naughty"
# touch: cannot create '/naughty': Read-only file system
kubectl exec readonly-pod -- sh -c "touch /tmp/ok && ls /tmp/ok"
# /tmp emptyDir mount edildiği için yazılabilir
```

### 4) Capabilities drop — root iken bile kısıtlı

```bash
kubectl apply -f 04-pod-drop-capabilities.yaml
kubectl exec capdrop-pod -- sh -c "ping -c1 8.8.8.8"
# permission denied — NET_RAW düşürüldüğü için ping çalışmaz
kubectl exec capdrop-pod -- sh -c "capsh --print | head -3"
# Current: = sadece NET_BIND_SERVICE
```

### 5) fsGroup ile PVC sahibi

```bash
kubectl apply -f 05-pod-fsgroup-pvc.yaml
kubectl exec fsgroup-pod -- ls -ld /data
# /data grup sahibi 2000 (fsGroup) olmalı
kubectl exec fsgroup-pod -- sh -c "echo merhaba > /data/test && cat /data/test"
```

### 6) Seccomp profili

```bash
kubectl apply -f 06-pod-seccomp.yaml
kubectl exec seccomp-pod -- sh -c "uname -a"
# normal çalışır — RuntimeDefault çoğu syscall'a izin verir
```

## Pod Security Standards (PSS)

K8s 1.25+ ile gelen 3 profil:

| Profil | Açıklama |
|---|---|
| `privileged` | Hiç kısıt yok. Sistem Pod'ları için. |
| `baseline` | Bilinen ayrıcalık yükseltmelerini engeller. Geliştirme için yeterli. |
| `restricted` | Sıkı sertleştirme. runAsNonRoot, drop ALL, seccomp RuntimeDefault şart. |

Namespace'e label ile uygulanır:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: prod
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

## Temizlik

```bash
kubectl delete -f .
```

## İleri Detaylar

- **runAsUser >= 10000** önerisi: host kullanıcısıyla çakışmasın.
- **readOnlyRootFilesystem + emptyDir** ASP.NET/Java gibi /tmp gerektiren uygulamalar için zorunlu kalıp.
- **Kyverno / OPA Gatekeeper**: PSS dışında özel policy'ler için.
- **AppArmor / SELinux**: linux güvenlik modülleri annotation ile bağlanabilir.
