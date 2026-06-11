# NetworkPolicy

İleri konu — kursun ana modüllerinden sonra işlenir.

## Amaç

Kubernetes'in **default ağ modeli "her şey her şeyle konuşabilir"**dir. Üretimde bunu
kabul edilemez bulan kuruluşlar için **NetworkPolicy** L3/L4 firewall kuralları sağlar:

- **podSelector**: hangi Pod'lara uygulansın
- **policyTypes**: Ingress / Egress
- **ingress.from** + **egress.to**: kaynak/hedef belirleme (Pod label, namespace label, IP block)
- **ports**: protokol + port

## CRİTİK ÖNKOŞUL: CNI desteği

NetworkPolicy yalnızca **policy-aware CNI plugin** ile çalışır:

| CNI | Policy desteği |
|---|---|
| Calico | ✓ |
| Cilium | ✓ |
| Weave Net | ✓ |
| Flannel (default Minikube) | ✗ — NetworkPolicy hiçbir etki yapmaz! |

### Minikube ile Calico kurulumu

```bash
minikube delete                            # mevcut cluster sil
minikube start --cni=calico --driver=docker --cpus=2 --memory=4g
kubectl get pods -n kube-system | grep calico
# calico-node ve calico-kube-controllers Running olmalı
```

## Default davranış

Bir Pod için **hiçbir** NetworkPolicy yoksa: tüm trafiğe izin verilir.
**En az bir** NetworkPolicy bir Pod'u seçerse: o policy'de izin verilmeyen her şey reddedilir.

Bu yüzden tipik desen: önce **deny-all** uygulanır, sonra istenenler **allow** edilir.

## Lab Senaryosu — frontend / backend / db zinciri

3 katmanlı bir uygulama:
- `frontend` (kullanıcıya açık)
- `backend` (yalnız frontend'den erişilebilmeli)
- `db` (yalnız backend'den erişilebilmeli)
- `attacker` (hiçbirine erişememeli)

### 1) Setup — 4 Pod aç

```bash
kubectl apply -f 00-test-pods.yaml
kubectl get pods -l 'tier in (frontend,backend,db,attacker)'
```

### 2) Önce — kural yok, herkes konuşur

```bash
# attacker'dan backend'e erişimi dene — ÇALIŞIR (default-allow)
kubectl exec attacker -- wget -qO- --timeout=3 http://backend
# attacker'dan db'ye erişim — ÇALIŞIR
kubectl exec attacker -- wget -qO- --timeout=3 http://db
```

### 3) Deny-all ingress uygula

```bash
kubectl apply -f 01-deny-all-ingress.yaml
# Şimdi backend ve db'ye HİÇBİR erişim yok
kubectl exec attacker -- wget -qO- --timeout=3 http://backend  # timeout!
kubectl exec frontend -- wget -qO- --timeout=3 http://backend  # bu da timeout!
```

### 4) Frontend → backend izin ver

```bash
kubectl apply -f 02-allow-frontend-to-backend.yaml
kubectl exec frontend -- wget -qO- --timeout=3 http://backend  # OK
kubectl exec attacker -- wget -qO- --timeout=3 http://backend  # hâlâ engelli
```

### 5) Backend → db izin ver

```bash
kubectl apply -f 03-allow-backend-to-db.yaml
kubectl exec backend -- wget -qO- --timeout=3 http://db        # OK
kubectl exec frontend -- wget -qO- --timeout=3 http://db       # frontend db'ye direkt erişemez
```

### 6) Egress kontrolü — backend dışarı çıkamasın

```bash
kubectl apply -f 04-deny-all-egress.yaml
kubectl exec backend -- wget -qO- --timeout=3 http://example.com  # timeout
# Ama DNS lookup da çalışmıyor — bu yüzden DNS'e exception eklenir:
kubectl apply -f 05-allow-egress-dns.yaml
# Hâlâ external HTTP yok, ama DNS çözülür
```

### 7) Namespace tabanlı izolasyon

```bash
kubectl create namespace dev
kubectl label namespace dev tier=trusted
kubectl apply -f 06-allow-from-namespace.yaml
# Yalnızca tier=trusted etiketli namespace'ten gelen trafik backend'e erişebilir
```

## Sık karşılaşılan hatalar

| Hata | Sebep | Çözüm |
|---|---|---|
| Policy uygulandı, etkisi yok | CNI policy desteklemiyor | Calico/Cilium ile cluster kur |
| DNS çözülmüyor | Egress deny eklendi, port 53 unutuldu | UDP/TCP 53'e kube-system'e izin ver |
| Pod kendi kendine konuşamıyor | localhost trafiği yine de izinli ama selector hatalı | Aynı Pod içi her zaman serbest |
| Service IP'sine erişim çalışmıyor | Policy Pod IP'ye değil, hedef seçiciyle bakılır | Hedef Pod'un label'ı doğru mu? |

## Temizlik

```bash
kubectl delete -f .
kubectl delete namespace dev --ignore-not-found
```

## İleri Detaylar

- **Cilium Network Policies (CNP/CCNP)** — L7 (HTTP path, method) ve identity-based policy.
- **AdminNetworkPolicy** (1.27+ alpha) — cluster admin önceliği, namespace policy'lerinden üstün.
- **eBPF** — Cilium'un kullandığı, iptables'tan çok daha hızlı veri yolu.
- **NetworkPolicy debug**:
  - `kubectl describe networkpolicy`
  - Calico için `calicoctl get networkpolicy`
  - Test pod'undan `nc -vz <target>` ile portları sondalama
