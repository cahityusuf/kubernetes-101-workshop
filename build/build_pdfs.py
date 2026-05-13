"""
Kubernetes Giriş Kursu — 2 günlük müfredat ve 10 soruluk ön değerlendirme
sınavının PDF olarak üretilmesi.
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    KeepTogether, ListFlowable, ListItem
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ---------------------------------------------------------------------------
# Türkçe karakter desteği için DejaVuSans fontunu kaydet
# ---------------------------------------------------------------------------
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

pdfmetrics.registerFont(TTFont("DejaVu", FONT_REG))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", FONT_BOLD))
pdfmetrics.registerFont(TTFont("DejaVuMono", FONT_MONO))

# ---------------------------------------------------------------------------
# Stiller
# ---------------------------------------------------------------------------
styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "TitleTR", parent=styles["Title"], fontName="DejaVu-Bold",
    fontSize=22, leading=26, alignment=TA_CENTER, spaceAfter=10,
    textColor=colors.HexColor("#0b3d91"),
)
subtitle_style = ParagraphStyle(
    "SubtitleTR", parent=styles["Normal"], fontName="DejaVu",
    fontSize=12, leading=16, alignment=TA_CENTER, spaceAfter=18,
    textColor=colors.HexColor("#444444"),
)
h1_style = ParagraphStyle(
    "H1TR", parent=styles["Heading1"], fontName="DejaVu-Bold",
    fontSize=16, leading=20, spaceBefore=14, spaceAfter=8,
    textColor=colors.HexColor("#0b3d91"),
)
h2_style = ParagraphStyle(
    "H2TR", parent=styles["Heading2"], fontName="DejaVu-Bold",
    fontSize=13, leading=17, spaceBefore=10, spaceAfter=6,
    textColor=colors.HexColor("#11468f"),
)
h3_style = ParagraphStyle(
    "H3TR", parent=styles["Heading3"], fontName="DejaVu-Bold",
    fontSize=11, leading=15, spaceBefore=8, spaceAfter=4,
    textColor=colors.HexColor("#222222"),
)
body_style = ParagraphStyle(
    "BodyTR", parent=styles["BodyText"], fontName="DejaVu",
    fontSize=10.5, leading=15, alignment=TA_JUSTIFY, spaceAfter=6,
)
bullet_style = ParagraphStyle(
    "BulletTR", parent=body_style, leftIndent=14, bulletIndent=2,
    spaceAfter=2,
)
code_style = ParagraphStyle(
    "CodeTR", parent=styles["Code"], fontName="DejaVuMono",
    fontSize=9, leading=12, leftIndent=10, rightIndent=10,
    backColor=colors.HexColor("#f4f4f4"),
    borderColor=colors.HexColor("#dddddd"), borderWidth=0.5,
    borderPadding=6, spaceBefore=4, spaceAfter=8,
)
note_style = ParagraphStyle(
    "NoteTR", parent=body_style, leftIndent=10, rightIndent=10,
    backColor=colors.HexColor("#fff8e1"),
    borderColor=colors.HexColor("#f0c674"), borderWidth=0.5,
    borderPadding=6, spaceBefore=4, spaceAfter=8,
)

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def bullets(items):
    """Madde işaretli liste döndür."""
    return ListFlowable(
        [ListItem(Paragraph(t, body_style), leftIndent=10) for t in items],
        bulletType="bullet", start="•", leftIndent=14,
    )


def code(text):
    """Kod bloğu paragrafı."""
    safe = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    safe = safe.replace("\n", "<br/>")
    return Paragraph(f'<font face="DejaVuMono">{safe}</font>', code_style)


def note(text):
    return Paragraph(f"<b>Not:</b> {text}", note_style)


# ===========================================================================
# 1) MÜFREDAT PDF
# ===========================================================================
def build_curriculum():
    out_path = os.path.join(OUT_DIR, "kubernetes-giris-kursu-mufredat.pdf")
    doc = SimpleDocTemplate(
        out_path, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
        title="Kubernetes Giriş Kursu — Müfredat",
        author="Eğitim Birimi",
    )

    s = []  # story

    # ---------------- KAPAK ----------------
    s.append(Spacer(1, 4 * cm))
    s.append(Paragraph("Kubernetes Giriş Kursu", title_style))
    s.append(Paragraph("2 Günlük Hands-on Eğitim Programı", subtitle_style))
    s.append(Spacer(1, 1 * cm))

    cover_data = [
        ["Süre", "2 gün (toplam ~14 saat)"],
        ["Hedef Kitle", "Docker bilen yazılım geliştiriciler"],
        ["Lab Ortamı", "Minikube (yerel makine)"],
        ["Ön Koşul", "Docker temel kullanımı, Linux komut satırı"],
        ["Format", "%40 teori, %60 uygulama"],
        ["Kazanım", "Temel K8s nesnelerini kurup çalıştırabilme"],
    ]
    t = Table(cover_data, colWidths=[5 * cm, 10 * cm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "DejaVu"),
        ("FONTNAME", (0, 0), (0, -1), "DejaVu-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10.5),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eef2fb")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#0b3d91")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (1, 0), (1, -1), [colors.white, colors.HexColor("#fafafa")]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cccccc")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    s.append(t)
    s.append(PageBreak())

    # ---------------- KURS HAKKINDA ----------------
    s.append(Paragraph("Kurs Hakkında", h1_style))
    s.append(Paragraph(
        "Bu kurs, Docker konteynerlerini hâlihazırda kullanan geliştiricilere "
        "Kubernetes'in temel yapı taşlarını uygulamalı olarak öğretmek üzere "
        "tasarlanmıştır. İki gün boyunca her kursiyer, kendi makinesinde "
        "Minikube üzerinde Pod, Deployment, Service, ConfigMap, Secret, "
        "Volume, Namespace ve Ingress gibi temel nesneleri oluşturup "
        "yönetebilir hâle gelir.",
        body_style,
    ))

    s.append(Paragraph("Genel Öğrenme Çıktıları", h2_style))
    s.append(bullets([
        "Kubernetes mimarisini (control plane, worker, kubelet, etcd, API server) açıklayabilme.",
        "Minikube ile lokal bir cluster kurup <font face='DejaVuMono'>kubectl</font> ile yönetebilme.",
        "YAML manifest dosyaları yazıp <font face='DejaVuMono'>kubectl apply</font> ile uygulayabilme.",
        "Pod, ReplicaSet ve Deployment arasındaki farkı kavrayıp doğru nesneyi seçebilme.",
        "ClusterIP, NodePort ve LoadBalancer servislerini kullanım senaryosuna göre ayırt edebilme.",
        "ConfigMap ve Secret ile uygulama yapılandırmasını dış kaynağa taşıyabilme.",
        "PersistentVolume / PersistentVolumeClaim ile kalıcı depolama bağlayabilme.",
        "Liveness, readiness probe yapılandırarak uygulama sağlığını izleyebilme.",
        "Temel düzeyde sorun gidermek (logs, describe, events).",
    ]))

    s.append(Paragraph("Önerilen Önkoşul Hazırlığı", h2_style))
    s.append(bullets([
        "Çalışan bir Docker kurulumu (Docker Desktop veya Docker Engine).",
        "Minikube + kubectl kurulumu (kurulum adımları Modül 0'da yer alır).",
        "Bir kod editörü (VS Code önerilir, YAML eklentisi ile).",
        "En az 4 GB boş RAM ve 20 GB disk alanı.",
    ]))
    s.append(PageBreak())

    # ---------------- GÜN 1 ----------------
    s.append(Paragraph("1. Gün — Temel Kavramlar ve Çekirdek Nesneler", h1_style))
    s.append(Paragraph(
        "Birinci gün, Kubernetes'in mimarisinden başlayıp Pod, ReplicaSet, "
        "Deployment ve Service ile çalışan bir uygulamayı cluster üzerinde "
        "yayınlamayı kapsar. Tüm modüller hands-on lab içerir.",
        body_style,
    ))

    # ---- Modül 0 ----
    s.append(Paragraph("Modül 0 — Ortam Kurulumu (60 dk)", h2_style))
    s.append(Paragraph("Konular", h3_style))
    s.append(bullets([
        "Docker'ın çalışır durumda olduğunun doğrulanması.",
        "Minikube ve kubectl kurulumu (macOS / Linux / Windows).",
        "İlk cluster'ı başlatma: <font face='DejaVuMono'>minikube start</font>.",
        "<font face='DejaVuMono'>kubectl</font> bağlamı (context) ve yapılandırma.",
    ]))
    s.append(Paragraph("Lab", h3_style))
    s.append(code(
        "minikube start --driver=docker --cpus=2 --memory=4g\n"
        "kubectl cluster-info\n"
        "kubectl get nodes\n"
        "kubectl version --short"
    ))

    # ---- Modül 1 ----
    s.append(Paragraph("Modül 1 — Kubernetes'e Giriş (90 dk)", h2_style))
    s.append(Paragraph("Konular", h3_style))
    s.append(bullets([
        "Konteyner orkestrasyonu nedir, neden gereklidir?",
        "Docker Compose ile Kubernetes karşılaştırması.",
        "Kubernetes mimarisi: control plane bileşenleri (API server, scheduler, controller manager, etcd) ve worker bileşenleri (kubelet, kube-proxy, container runtime).",
        "Declarative vs imperative yaklaşım, YAML manifestlerin rolü.",
        "<font face='DejaVuMono'>kubectl</font> komut yapısı ve yardım sistemi.",
    ]))
    s.append(Paragraph("Lab", h3_style))
    s.append(code(
        "kubectl get all -A\n"
        "kubectl explain pod\n"
        "kubectl api-resources | head"
    ))

    # ---- Modül 2 ----
    s.append(Paragraph("Modül 2 — Pod'lar (90 dk)", h2_style))
    s.append(Paragraph("Konular", h3_style))
    s.append(bullets([
        "Pod nedir, neden \"en küçük dağıtım birimi\" olarak tanımlanır?",
        "Tek konteynerli ve çok konteynerli (sidecar) Pod desenleri.",
        "Pod yaşam döngüsü ve yeniden başlatma politikaları (restartPolicy).",
        "<font face='DejaVuMono'>kubectl run</font> vs YAML manifest ile Pod oluşturma.",
        "Pod'a erişim: <font face='DejaVuMono'>kubectl exec</font>, <font face='DejaVuMono'>port-forward</font>, <font face='DejaVuMono'>logs</font>.",
    ]))
    s.append(Paragraph("Lab", h3_style))
    s.append(code(
        "# nginx-pod.yaml\n"
        "apiVersion: v1\n"
        "kind: Pod\n"
        "metadata:\n"
        "  name: nginx-demo\n"
        "spec:\n"
        "  containers:\n"
        "  - name: web\n"
        "    image: nginx:1.27\n"
        "    ports:\n"
        "    - containerPort: 80\n"
        "---\n"
        "kubectl apply -f nginx-pod.yaml\n"
        "kubectl get pods -o wide\n"
        "kubectl port-forward pod/nginx-demo 8080:80"
    ))
    s.append(note(
        "Kursiyerler tek başına Pod'un üretim için neden yetersiz olduğunu "
        "(self-healing yok, ölçeklenmiyor) bu modülde deneyimleyerek görür."
    ))

    # ---- Modül 3 ----
    s.append(Paragraph("Modül 3 — ReplicaSet ve Deployment (120 dk)", h2_style))
    s.append(Paragraph("Konular", h3_style))
    s.append(bullets([
        "ReplicaSet ile istenen replika sayısının korunması (self-healing).",
        "Deployment'ın ReplicaSet üzerine getirdiği özellikler: rollout, rollback, history.",
        "<font face='DejaVuMono'>strategy: RollingUpdate</font> ve <font face='DejaVuMono'>Recreate</font> stratejilerinin karşılaştırılması.",
        "Label ve selector mantığı; etiketlerle nesne ilişkilendirme.",
        "Ölçeklendirme: <font face='DejaVuMono'>kubectl scale</font> ve manifest üzerinden değişiklik.",
    ]))
    s.append(Paragraph("Lab", h3_style))
    s.append(code(
        "kubectl create deployment web --image=nginx:1.27 --replicas=3\n"
        "kubectl scale deployment/web --replicas=5\n"
        "kubectl set image deployment/web nginx=nginx:1.28\n"
        "kubectl rollout status deployment/web\n"
        "kubectl rollout undo deployment/web"
    ))

    # ---- Modül 4 ----
    s.append(Paragraph("Modül 4 — Service'ler ve Ağ Modeli (120 dk)", h2_style))
    s.append(Paragraph("Konular", h3_style))
    s.append(bullets([
        "Kubernetes ağ modeli ve Pod IP'lerinin geçiciliği.",
        "Service türleri: ClusterIP, NodePort, LoadBalancer, ExternalName.",
        "Service ile Deployment arasında selector eşleşmesi.",
        "DNS ile servis bulma: <font face='DejaVuMono'>&lt;service&gt;.&lt;namespace&gt;.svc.cluster.local</font>.",
        "<font face='DejaVuMono'>minikube service</font> ve <font face='DejaVuMono'>port-forward</font> ile dış erişim.",
    ]))
    s.append(Paragraph("Lab", h3_style))
    s.append(code(
        "kubectl expose deployment web --port=80 --type=NodePort\n"
        "kubectl get svc\n"
        "minikube service web --url\n"
        "# Cluster içi DNS testi\n"
        "kubectl run test --rm -it --image=busybox -- sh\n"
        "  # wget -qO- web.default.svc.cluster.local"
    ))

    s.append(Paragraph("1. Gün Sonu — Mini Proje (45 dk)", h2_style))
    s.append(bullets([
        "Bir Deployment + Service ile basit bir web uygulamasını yayınla.",
        "Replikaları 1'den 3'e çıkar ve dağılımı gözlemle.",
        "Image versiyonunu güncelle ve rolling update'i izle.",
    ]))
    s.append(PageBreak())

    # ---------------- GÜN 2 ----------------
    s.append(Paragraph("2. Gün — Yapılandırma, Depolama ve Yayın", h1_style))
    s.append(Paragraph(
        "İkinci gün, üretim benzeri uygulamalar için yapılandırma yönetimi, "
        "kalıcı depolama, namespace organizasyonu, sağlık kontrolü ve dış "
        "erişim (Ingress) konularını kapsar.",
        body_style,
    ))

    # ---- Modül 5 ----
    s.append(Paragraph("Modül 5 — ConfigMap ve Secret (90 dk)", h2_style))
    s.append(Paragraph("Konular", h3_style))
    s.append(bullets([
        "Yapılandırmayı uygulama image'ından ayırma ilkesi (12-factor).",
        "ConfigMap oluşturma yolları: literal, dosyadan, manifest.",
        "ConfigMap'i ortam değişkeni veya volume olarak Pod'a bağlama.",
        "Secret nedir, ConfigMap'ten farkı; base64 saklama ve sınırları.",
        "Secret tipleri: generic, docker-registry, tls.",
    ]))
    s.append(Paragraph("Lab", h3_style))
    s.append(code(
        "kubectl create configmap app-config \\\n"
        "  --from-literal=APP_MODE=prod --from-literal=LOG_LEVEL=info\n"
        "kubectl create secret generic db-secret \\\n"
        "  --from-literal=DB_PASSWORD='S3cret!'\n"
        "kubectl get configmap app-config -o yaml\n"
        "# Pod'da envFrom: configMapRef ve secretRef kullanımı"
    ))

    # ---- Modül 6 ----
    s.append(Paragraph("Modül 6 — Volume ve Persistent Storage (90 dk)", h2_style))
    s.append(Paragraph("Konular", h3_style))
    s.append(bullets([
        "Konteyner dosya sisteminin geçiciliği ve veri kaybı problemi.",
        "Volume tipleri: emptyDir, hostPath, configMap, secret, persistentVolumeClaim.",
        "PersistentVolume (PV) ve PersistentVolumeClaim (PVC) ilişkisi.",
        "StorageClass ile dinamik provisioning kavramı.",
        "Minikube'de <font face='DejaVuMono'>standard</font> StorageClass kullanımı.",
    ]))
    s.append(Paragraph("Lab", h3_style))
    s.append(code(
        "# pvc.yaml\n"
        "apiVersion: v1\n"
        "kind: PersistentVolumeClaim\n"
        "metadata:\n"
        "  name: data-pvc\n"
        "spec:\n"
        "  accessModes: [\"ReadWriteOnce\"]\n"
        "  resources:\n"
        "    requests:\n"
        "      storage: 1Gi\n"
        "---\n"
        "kubectl apply -f pvc.yaml\n"
        "kubectl get pvc,pv"
    ))

    # ---- Modül 7 ----
    s.append(Paragraph("Modül 7 — Namespace, Label ve Resource Yönetimi (60 dk)", h2_style))
    s.append(Paragraph("Konular", h3_style))
    s.append(bullets([
        "Namespace ile ortam ve takım izolasyonu.",
        "Label ve annotation'ların organizasyondaki rolü.",
        "<font face='DejaVuMono'>resources.requests</font> ve <font face='DejaVuMono'>limits</font> ile CPU/RAM yönetimi.",
        "LimitRange ve ResourceQuota'ya genel bakış.",
    ]))
    s.append(Paragraph("Lab", h3_style))
    s.append(code(
        "kubectl create namespace dev\n"
        "kubectl -n dev create deployment api --image=hashicorp/http-echo \\\n"
        "  -- -text=hello\n"
        "kubectl get pods -A --show-labels\n"
        "kubectl get pods -l app=api -n dev"
    ))

    # ---- Modül 8 ----
    s.append(Paragraph("Modül 8 — Probe'lar ve Sağlık Kontrolü (60 dk)", h2_style))
    s.append(Paragraph("Konular", h3_style))
    s.append(bullets([
        "Liveness, readiness ve startup probe'ları arasındaki fark.",
        "HTTP, TCP ve exec probe tipleri.",
        "Yanlış yapılandırılmış probe'ların etkileri (sürekli restart, trafik almama).",
        "<font face='DejaVuMono'>kubectl describe</font> ile event okuma.",
    ]))
    s.append(Paragraph("Lab", h3_style))
    s.append(code(
        "# Deployment manifest'ine ekle:\n"
        "livenessProbe:\n"
        "  httpGet: { path: /, port: 80 }\n"
        "  initialDelaySeconds: 5\n"
        "  periodSeconds: 10\n"
        "readinessProbe:\n"
        "  httpGet: { path: /, port: 80 }\n"
        "  initialDelaySeconds: 2\n"
        "  periodSeconds: 5"
    ))

    # ---- Modül 9 ----
    s.append(Paragraph("Modül 9 — Ingress ile Dış Erişim (75 dk)", h2_style))
    s.append(Paragraph("Konular", h3_style))
    s.append(bullets([
        "Ingress ile NodePort/LoadBalancer arasındaki fark.",
        "Ingress controller kavramı; Minikube'de NGINX ingress add-on.",
        "Path-based ve host-based routing örnekleri.",
        "TLS terminasyonuna kısa giriş.",
    ]))
    s.append(Paragraph("Lab", h3_style))
    s.append(code(
        "minikube addons enable ingress\n"
        "kubectl get pods -n ingress-nginx\n"
        "# ingress.yaml dosyasını apply et\n"
        "kubectl apply -f ingress.yaml\n"
        "echo \"$(minikube ip)  demo.local\" | sudo tee -a /etc/hosts\n"
        "curl http://demo.local/"
    ))

    # ---- Modül 10 ----
    s.append(Paragraph("Modül 10 — Kapanış Projesi ve Sorun Giderme (90 dk)", h2_style))
    s.append(Paragraph("Senaryo", h3_style))
    s.append(Paragraph(
        "Kursiyerler, basit bir Python/Node.js uygulaması ile bir Redis "
        "instance'ını birlikte ayağa kaldırır. Uygulama Deployment + "
        "Service + ConfigMap + Secret + PVC + Ingress kullanır. Eğitmen "
        "kasıtlı olarak hata enjekte eder; kursiyerler "
        "<font face='DejaVuMono'>logs</font>, <font face='DejaVuMono'>describe</font>, "
        "<font face='DejaVuMono'>events</font> ile sorunu bulur.",
        body_style,
    ))
    s.append(Paragraph("Hedeflenen Çıktı", h3_style))
    s.append(bullets([
        "<font face='DejaVuMono'>http://demo.local</font> üzerinden erişilebilir bir uygulama.",
        "Replikaları 3 olan, rolling update'e uygun bir Deployment.",
        "Konfigürasyon ve şifrelerin manifest dışında tutulması.",
        "Pod yeniden başlatılsa bile veri kaybetmeyen bir Redis kurulumu.",
    ]))

    # ---------------- DEĞERLENDİRME ----------------
    s.append(Paragraph("Değerlendirme ve Devam Şartları", h1_style))
    s.append(bullets([
        "Kurs öncesi: 10 soruluk seviye tespit (ön değerlendirme) sınavı.",
        "Her modül sonunda 5–10 dakikalık kısa quiz (sözlü/yazılı).",
        "İkinci günün sonunda kapanış projesinin canlı sunumu.",
        "Sertifika için en az %70 katılım ve kapanış projesinin tamamlanması.",
    ]))

    s.append(Paragraph("Kurs Sonunda Önerilen Yol Haritası", h1_style))
    s.append(bullets([
        "Helm ile paket yönetimi.",
        "Kustomize ve GitOps (ArgoCD/Flux) ile yayın akışı.",
        "Horizontal Pod Autoscaler ve metrics-server.",
        "Network Policy ile cluster içi izolasyon.",
        "CKAD (Certified Kubernetes Application Developer) sertifikasyon hazırlığı.",
    ]))

    doc.build(s)
    return out_path


# ===========================================================================
# 2) ÖN DEĞERLENDİRME SINAVI PDF
# ===========================================================================
def build_assessment():
    out_path = os.path.join(OUT_DIR, "kubernetes-on-degerlendirme-sinavi.pdf")
    doc = SimpleDocTemplate(
        out_path, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
        title="Kubernetes Giriş Kursu — Ön Değerlendirme Sınavı",
        author="Eğitim Birimi",
    )

    s = []

    # KAPAK
    s.append(Spacer(1, 3 * cm))
    s.append(Paragraph("Kubernetes Giriş Kursu", title_style))
    s.append(Paragraph("Ön Değerlendirme Sınavı (Seviye Tespit)", subtitle_style))
    s.append(Spacer(1, 0.5 * cm))

    info_data = [
        ["Süre", "20 dakika"],
        ["Soru sayısı", "10 (çoktan seçmeli, tek doğru cevap)"],
        ["Puanlama", "Her soru 10 puan, toplam 100"],
        ["Geçer not", "Bilgi amaçlı; kursa katılım için ön koşul değildir"],
        ["Amaç", "Kursiyerin Docker / K8s ön bilgisini ölçmek"],
    ]
    t = Table(info_data, colWidths=[5 * cm, 10 * cm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "DejaVu"),
        ("FONTNAME", (0, 0), (0, -1), "DejaVu-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10.5),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eef2fb")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#0b3d91")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cccccc")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    s.append(t)
    s.append(Spacer(1, 1 * cm))

    s.append(Paragraph("Yönergeler", h2_style))
    s.append(bullets([
        "Her sorunun yalnızca <b>bir</b> doğru cevabı vardır.",
        "Cevap kâğıdına soru numarasının karşısına seçeneği (A/B/C/D) yazın.",
        "Bilmediğiniz soruyu boş bırakmanız önerilir; yanlış cevap puan düşürmez.",
        "Sınav, kursun zorluk düzeyini hizalamak için kullanılır.",
    ]))

    s.append(PageBreak())

    # ----------------- SORULAR -----------------
    s.append(Paragraph("Sorular", h1_style))

    questions = [
        {
            "q": "Aşağıdakilerden <b>hangisi</b> Kubernetes'in temel görevlerinden biri <b>değildir</b>?",
            "opts": [
                "A) Konteynerleri birden fazla node üzerinde planlamak (scheduling)",
                "B) Hatalı konteynerleri otomatik olarak yeniden başlatmak",
                "C) Konteyner image'larını derlemek (build etmek)",
                "D) Servisler arası yük dengelemek",
            ],
        },
        {
            "q": "Kubernetes'te dağıtımın <b>en küçük birimi</b> hangisidir?",
            "opts": [
                "A) Container",
                "B) Pod",
                "C) Deployment",
                "D) Node",
            ],
        },
        {
            "q": "Bir Pod ile bir Deployment arasındaki temel fark hangisinde doğru ifade edilmiştir?",
            "opts": [
                "A) Pod ölçeklenebilir, Deployment ölçeklenemez.",
                "B) Deployment, ReplicaSet aracılığıyla istenen Pod sayısını sürekli korur ve güncelleme stratejisi sunar.",
                "C) Pod yalnızca üretimde, Deployment yalnızca geliştirmede kullanılır.",
                "D) Deployment yalnızca tek bir Pod örneği çalıştırabilir.",
            ],
        },
        {
            "q": "Aşağıdaki <font face='DejaVuMono'>kubectl</font> komutlarından hangisi cluster'daki tüm namespace'lerdeki Pod'ları listeler?",
            "opts": [
                "A) <font face='DejaVuMono'>kubectl get pods</font>",
                "B) <font face='DejaVuMono'>kubectl get pods --all-namespaces</font>",
                "C) <font face='DejaVuMono'>kubectl list pods</font>",
                "D) <font face='DejaVuMono'>kubectl pods -all</font>",
            ],
        },
        {
            "q": "Bir uygulamanın yalnızca cluster içinden erişilmesini istiyorsunuz. Hangi Service tipi en uygundur?",
            "opts": [
                "A) NodePort",
                "B) LoadBalancer",
                "C) ClusterIP",
                "D) ExternalName",
            ],
        },
        {
            "q": "Aşağıdaki YAML parçasında <b>eksik</b> alan hangisidir?<br/>"
                  "<font face='DejaVuMono'>apiVersion: v1<br/>"
                  "kind: Pod<br/>"
                  "metadata:<br/>"
                  "&nbsp;&nbsp;name: web<br/>"
                  "spec:<br/>"
                  "&nbsp;&nbsp;containers:<br/>"
                  "&nbsp;&nbsp;- image: nginx</font>",
            "opts": [
                "A) <font face='DejaVuMono'>metadata.namespace</font>",
                "B) <font face='DejaVuMono'>spec.replicas</font>",
                "C) <font face='DejaVuMono'>spec.containers[].name</font>",
                "D) <font face='DejaVuMono'>spec.selector</font>",
            ],
        },
        {
            "q": "Veritabanı parolası gibi hassas bilgileri Pod'a aktarmak için en uygun Kubernetes nesnesi hangisidir?",
            "opts": [
                "A) ConfigMap",
                "B) Secret",
                "C) Annotation",
                "D) Environment dosyası (image içine gömme)",
            ],
        },
        {
            "q": "Pod yeniden oluşturulduğunda dahi verinin korunması için aşağıdakilerden hangisi kullanılır?",
            "opts": [
                "A) <font face='DejaVuMono'>emptyDir</font> volume",
                "B) Konteynerin yerel diski",
                "C) PersistentVolumeClaim ile bağlanan PersistentVolume",
                "D) <font face='DejaVuMono'>hostPath</font> (üretim için önerilen yöntem)",
            ],
        },
        {
            "q": "Bir Pod sürekli olarak <font face='DejaVuMono'>CrashLoopBackOff</font> durumuna düşüyor. İlk olarak hangi komutu çalıştırmak en mantıklıdır?",
            "opts": [
                "A) <font face='DejaVuMono'>kubectl delete pod &lt;ad&gt;</font>",
                "B) <font face='DejaVuMono'>kubectl logs &lt;ad&gt;</font> ve <font face='DejaVuMono'>kubectl describe pod &lt;ad&gt;</font>",
                "C) <font face='DejaVuMono'>minikube stop</font>",
                "D) <font face='DejaVuMono'>kubectl rollout restart</font> deployment",
            ],
        },
        {
            "q": "Aşağıdakilerden hangisi <b>declarative</b> yaklaşıma örnektir?",
            "opts": [
                "A) <font face='DejaVuMono'>kubectl run nginx --image=nginx</font>",
                "B) <font face='DejaVuMono'>kubectl create deployment web --image=nginx</font>",
                "C) <font face='DejaVuMono'>kubectl apply -f deployment.yaml</font>",
                "D) <font face='DejaVuMono'>kubectl scale deployment web --replicas=5</font>",
            ],
        },
    ]

    for i, item in enumerate(questions, 1):
        block = [Paragraph(f"<b>Soru {i}.</b> {item['q']}", body_style)]
        for opt in item["opts"]:
            block.append(Paragraph(opt, bullet_style))
        block.append(Spacer(1, 0.3 * cm))
        s.append(KeepTogether(block))

    s.append(PageBreak())

    # ----------------- CEVAP ANAHTARI -----------------
    s.append(Paragraph("Cevap Anahtarı ve Açıklamalar", h1_style))
    s.append(Paragraph(
        "Bu bölüm eğitmen kullanımı içindir. Sınav tamamlandıktan sonra "
        "kursiyerlerle birlikte gözden geçirilmesi önerilir.",
        body_style,
    ))

    answers = [
        ("1", "C", "Kubernetes orkestratördür; image build işlemi Docker / Buildah gibi araçların görevidir."),
        ("2", "B", "Pod, Kubernetes'te dağıtılabilen en küçük birimdir; bir veya birden fazla konteyner içerebilir."),
        ("3", "B", "Deployment, ReplicaSet üzerinden istenen replika sayısını korur ve rolling update / rollback yetenekleri sağlar."),
        ("4", "B", "<font face='DejaVuMono'>--all-namespaces</font> (kısaltması <font face='DejaVuMono'>-A</font>) bayrağı tüm namespace'leri listeler."),
        ("5", "C", "ClusterIP, varsayılan tiptir ve servise yalnızca cluster içinden erişim sağlar."),
        ("6", "C", "<font face='DejaVuMono'>spec.containers[].name</font> zorunludur; her konteynerin Pod içinde benzersiz bir adı olmalıdır."),
        ("7", "B", "Secret hassas verileri taşımak için tasarlanmıştır; ConfigMap yapılandırma içindir."),
        ("8", "C", "PVC ile cluster'a bağlı kalıcı bir depolama (PV) tahsis edilir, Pod yeniden oluşsa bile veri korunur."),
        ("9", "B", "<font face='DejaVuMono'>logs</font> uygulama hatasını, <font face='DejaVuMono'>describe</font> ise event'leri ve probe sonuçlarını gösterir; teşhis için ilk başvurulacak komutlardır."),
        ("10", "C", "<font face='DejaVuMono'>kubectl apply -f</font> manifest dosyasındaki istenen durumu uygular; bu declarative yaklaşımdır."),
    ]

    answer_rows = [["Soru", "Doğru Cevap", "Açıklama"]]
    for n, ans, expl in answers:
        answer_rows.append([n, ans, Paragraph(expl, body_style)])

    t = Table(answer_rows, colWidths=[1.5 * cm, 2.5 * cm, 12 * cm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "DejaVu"),
        ("FONTNAME", (0, 0), (-1, 0), "DejaVu-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0b3d91")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4f6fb")]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cccccc")),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    s.append(t)

    s.append(Spacer(1, 0.5 * cm))
    s.append(Paragraph("Seviye Yorumlama Rehberi", h2_style))

    level_rows = [
        ["Puan", "Seviye", "Öneri"],
        ["0 – 30", "Başlangıç", "Standart müfredatla başla; Modül 1–4'e ekstra zaman ayır."],
        ["40 – 60", "Temel", "Standart müfredatı uygula; lab'larda eşli çalışma öner."],
        ["70 – 80", "Orta", "İleri konulara (probe, Ingress) daha çok zaman ayır."],
        ["90 – 100", "İleri", "Kursiyere mentor / asistan rolü ver; Helm, Operator önerisi yap."],
    ]
    t = Table(level_rows, colWidths=[3 * cm, 3 * cm, 10 * cm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "DejaVu"),
        ("FONTNAME", (0, 0), (-1, 0), "DejaVu-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0b3d91")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4f6fb")]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cccccc")),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    s.append(t)

    doc.build(s)
    return out_path


if __name__ == "__main__":
    p1 = build_curriculum()
    p2 = build_assessment()
    print("OK")
    print(p1)
    print(p2)
