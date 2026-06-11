# ServiceAccount & RBAC

İleri konu — kursun ana modüllerinden sonra işlenir.

## Amaç

- **ServiceAccount (SA)**: bir Pod'un Kubernetes API'sine kendini nasıl tanıttığını belirler.
- Her namespace'te otomatik olarak bir `default` SA vardır.
- ServiceAccount + **Role/ClusterRole** + **RoleBinding/ClusterRoleBinding** üçlüsü RBAC'in (Role-Based Access Control) temelidir.

## Önemli kavramlar

| Kavram | Açıklama |
|---|---|
| `ServiceAccount` | Pod kimliği. Namespace seviyesindedir. |
| `Role` | Belirli bir namespace içinde izinler. |
| `ClusterRole` | Tüm cluster geneli izinler (örn. nodes, persistentvolumes). |
| `RoleBinding` | Bir Role'u SA/User/Group ile namespace içinde eşler. |
| `ClusterRoleBinding` | ClusterRole'u cluster geneli eşler. |
| `automountServiceAccountToken` | SA token'ının Pod'a otomatik mount edilip edilmemesi (default: true). |
| Token mount yolu | `/var/run/secrets/kubernetes.io/serviceaccount/token` |
| CA mount yolu | `/var/run/secrets/kubernetes.io/serviceaccount/ca.crt` |
| Namespace mount yolu | `/var/run/secrets/kubernetes.io/serviceaccount/namespace` |

## Kubernetes 1.24+ değişikliği

K8s 1.24'ten itibaren ServiceAccount oluşturulduğunda **otomatik token Secret yaratılmaz**.
- Pod'a mount edilen token artık **projected volume** ile **TokenRequest API**'sinden üretilir (kısa ömürlü, rotate edilir).
- Kalıcı bir Secret token gerekiyorsa (örn. CI/CD için) manuel olarak `kubernetes.io/service-account-token` türünde Secret yaratılır — bkz. `05-token-secret-legacy.yaml`.

## Lab Senaryosu

### 1) Custom SA ve onun için Role oluştur

```bash
kubectl apply -f 01-serviceaccount.yaml
kubectl apply -f 02-role-rolebinding.yaml
kubectl get sa,role,rolebinding
```

### 2) SA'yı kullanan Pod aç

```bash
kubectl apply -f 04-pod-with-sa.yaml
kubectl get pods
```

### 3) Pod içinden token'ı doğrula

```bash
kubectl exec -it sa-demo -- sh

# Pod içinde:
> cat /var/run/secrets/kubernetes.io/serviceaccount/namespace
> ls /var/run/secrets/kubernetes.io/serviceaccount/
> TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
> CACERT=/var/run/secrets/kubernetes.io/serviceaccount/ca.crt
> curl --cacert $CACERT -H "Authorization: Bearer $TOKEN" \
    https://kubernetes.default.svc/api/v1/namespaces/default/pods
# Pod listesi dönmeli — Role'da pods get/list verildi
```

### 4) İzni olmayan kaynağı dene

```bash
# Pod içinde:
> curl --cacert $CACERT -H "Authorization: Bearer $TOKEN" \
    https://kubernetes.default.svc/api/v1/namespaces/default/secrets
# 403 Forbidden — secrets için izin yok
```

### 5) ClusterRole ile cluster-wide erişim

```bash
kubectl apply -f 03-clusterrole-clusterrolebinding.yaml
# Aynı Pod artık tüm namespace'lerden Pod listesi alabilir
```

### 6) automountServiceAccountToken: false testi

`04-pod-with-sa.yaml`'de `automountServiceAccountToken: false` yaparsanız Pod token'sız kalır;
`/var/run/secrets/kubernetes.io/serviceaccount/` dizini olmaz. Bu, "hiç API çağırmayacak"
Pod'lar için güvenli default'tur.

## kubectl auth can-i — Hızlı kontrol

Bir SA'nın belirli bir izni var mı?

```bash
kubectl auth can-i list pods --as=system:serviceaccount:default:reader-sa
# yes / no
kubectl auth can-i delete pods --as=system:serviceaccount:default:reader-sa
# no
```

## Temizlik

```bash
kubectl delete -f .
```

## İleri Detaylar

- **Default SA tehlikesi**: Default SA'ya RoleBinding eklemek namespace'teki TÜM Pod'lara o izni verir.
- **Workload Identity (GKE) / IRSA (EKS) / Azure Workload Identity**: bulut sağlayıcıların kendi IAM rollerini SA'ya bağlamak için.
- **OIDC token volume projection**: cloud IAM'e karşı SA tokeni federasyonu için (audience belirleme).
- **Pod Security Standards** ile `automountServiceAccountToken: false` zorunlu kılınabilir.
