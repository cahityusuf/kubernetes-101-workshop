"""
Kubernetes Giriş Kursu — Detaylı Eğitmen Dokümantasyonu (2 gün).
Her konu 5 başlık şablonu ile işlenir:
  1) Amaç ve mantık
  2) Mimarideki yer (diyagram/görsel)
  3) Komutlar ve flag'ler (kapsamlı tablo)
  4) Declarative YAML
  5) İleri detaylar / sık karşılaşılan hatalar / best practice

Diyagramlar doc_diagrams.py içinde tanımlıdır.
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    KeepTogether, ListFlowable, ListItem, Preformatted
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing

import doc_diagrams as dg

# ---------------------------------------------------------------------------
pdfmetrics.registerFont(TTFont("DejaVu",      "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DejaVuMono",  "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"))

PRIMARY = colors.HexColor("#0b3d91")
ACCENT  = colors.HexColor("#f59e0b")
SUCCESS = colors.HexColor("#16a34a")
DANGER  = colors.HexColor("#dc2626")
NEUTRAL = colors.HexColor("#475569")
LIGHT   = colors.HexColor("#eef2ff")

# ---------------------------------------------------------------------------
# Stiller
# ---------------------------------------------------------------------------
base = getSampleStyleSheet()

title_style = ParagraphStyle("T", parent=base["Title"], fontName="DejaVu-Bold",
    fontSize=24, leading=28, alignment=TA_CENTER, spaceAfter=8, textColor=PRIMARY)
sub_style = ParagraphStyle("S", parent=base["Normal"], fontName="DejaVu",
    fontSize=12, leading=16, alignment=TA_CENTER, spaceAfter=20, textColor=NEUTRAL)
h1 = ParagraphStyle("H1", parent=base["Heading1"], fontName="DejaVu-Bold",
    fontSize=18, leading=22, spaceBefore=14, spaceAfter=8, textColor=PRIMARY)
h2 = ParagraphStyle("H2", parent=base["Heading2"], fontName="DejaVu-Bold",
    fontSize=14, leading=18, spaceBefore=12, spaceAfter=6, textColor=colors.HexColor("#11468f"))
h3 = ParagraphStyle("H3", parent=base["Heading3"], fontName="DejaVu-Bold",
    fontSize=11.5, leading=15, spaceBefore=8, spaceAfter=4, textColor=colors.HexColor("#222"))
body = ParagraphStyle("B", parent=base["BodyText"], fontName="DejaVu",
    fontSize=10, leading=14, alignment=TA_JUSTIFY, spaceAfter=5)
bullet = ParagraphStyle("Bl", parent=body, leftIndent=14, bulletIndent=2, spaceAfter=2)
code_p = ParagraphStyle("C", parent=base["Code"], fontName="DejaVuMono",
    fontSize=8.5, leading=11.5, leftIndent=8, rightIndent=8,
    backColor=colors.HexColor("#f4f4f4"),
    borderColor=colors.HexColor("#dddddd"), borderWidth=0.5,
    borderPadding=6, spaceBefore=4, spaceAfter=6)
note_p = ParagraphStyle("N", parent=body, leftIndent=10, rightIndent=10,
    backColor=colors.HexColor("#fff8e1"),
    borderColor=colors.HexColor("#f0c674"), borderWidth=0.5,
    borderPadding=6, spaceBefore=4, spaceAfter=8)
tip_p = ParagraphStyle("Tp", parent=body, leftIndent=10, rightIndent=10,
    backColor=colors.HexColor("#ecfdf5"),
    borderColor=colors.HexColor("#16a34a"), borderWidth=0.5,
    borderPadding=6, spaceBefore=4, spaceAfter=8)
warn_p = ParagraphStyle("W", parent=body, leftIndent=10, rightIndent=10,
    backColor=colors.HexColor("#fee2e2"),
    borderColor=colors.HexColor("#dc2626"), borderWidth=0.5,
    borderPadding=6, spaceBefore=4, spaceAfter=8)

OUT = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------------------
# Ortak helper'lar
# ---------------------------------------------------------------------------
def P(s, st=body): return Paragraph(s, st)

def bullets(items, style=body):
    return ListFlowable(
        [ListItem(P(t, style), leftIndent=10) for t in items],
        bulletType="bullet", start="•", leftIndent=14)

def code(text):
    """Çok satırlı kod bloğu — Preformatted ile YAML indentation korunur."""
    return Preformatted(text, code_p)

def note(t): return Paragraph(f"<b>Not:</b> {t}", note_p)
def tip(t):  return Paragraph(f"<b>İpucu:</b> {t}", tip_p)
def warn(t): return Paragraph(f"<b>Dikkat:</b> {t}", warn_p)

def diagram(drawing: Drawing, max_width=17 * cm):
    """Drawing'i sayfa genişliğine sığacak şekilde döndür."""
    if drawing.width > max_width:
        scale = max_width / drawing.width
        drawing.width *= scale
        drawing.height *= scale
        drawing.scale(scale, scale)
    return drawing

def cmd_table(rows, col_widths=None):
    """[(komut, açıklama), ...]"""
    data = [["Komut", "Açıklama"]] + [
        [Paragraph(f'<font face="DejaVuMono" size="8.5">{c}</font>', body),
         P(d)] for c, d in rows]
    t = Table(data, colWidths=col_widths or [7 * cm, 10 * cm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "DejaVu"),
        ("FONTNAME", (0, 0), (-1, 0), "DejaVu-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f6f8fb")]),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#cccccc")),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t

def flag_table(rows):
    """[(flag, anlam, örnek), ...]"""
    data = [["Flag", "Anlam", "Örnek"]] + [
        [Paragraph(f'<font face="DejaVuMono" size="8.5">{f}</font>', body),
         P(d),
         Paragraph(f'<font face="DejaVuMono" size="8">{e}</font>', body)]
        for f, d, e in rows]
    t = Table(data, colWidths=[4.5 * cm, 7.5 * cm, 5 * cm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "DejaVu"),
        ("FONTNAME", (0, 0), (-1, 0), "DejaVu-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#11468f")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f6f8fb")]),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#cccccc")),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t

def info_table(rows, widths=None):
    data = [[Paragraph(f"<b>{k}</b>", body), P(v)] for k, v in rows]
    t = Table(data, colWidths=widths or [4.5 * cm, 12.5 * cm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "DejaVu"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eef2fb")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (1, 0), (1, -1), [colors.white, colors.HexColor("#fafafa")]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cccccc")),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t

# ---------------------------------------------------------------------------
# Şablon: bir konuyu 5 başlık ile yazan helper
# ---------------------------------------------------------------------------
def topic_section(s, title, purpose_paras, place_paras, place_diagram,
                  commands_intro, command_rows, flag_intro, flag_rows,
                  yaml_intro, yaml_code, advanced_items):
    s.append(Paragraph(title, h1))
    s.append(Paragraph("1) Amaç ve Mantık", h2))
    for p in purpose_paras: s.append(P(p))

    s.append(Paragraph("2) Mimarideki Yeri", h2))
    for p in place_paras: s.append(P(p))
    if place_diagram is not None:
        s.append(Spacer(1, 4))
        s.append(diagram(place_diagram))
        s.append(Spacer(1, 4))

    s.append(Paragraph("3) Komutlar ve Önemli Flag'ler", h2))
    for p in commands_intro: s.append(P(p))
    s.append(Spacer(1, 4))
    s.append(cmd_table(command_rows))
    if flag_rows:
        s.append(Spacer(1, 6))
        for p in flag_intro: s.append(P(p))
        s.append(flag_table(flag_rows))

    s.append(Paragraph("4) Declarative — YAML Manifest", h2))
    for p in yaml_intro: s.append(P(p))
    s.append(code(yaml_code))

    s.append(Paragraph("5) İleri Detaylar, Best Practice ve Sık Hatalar", h2))
    s.append(bullets(advanced_items))


# ---------------------------------------------------------------------------
# İÇERİK BÖLÜMLERİ
# ---------------------------------------------------------------------------
def cover(s):
    s.append(Spacer(1, 4 * cm))
    s.append(Paragraph("Kubernetes Giriş Kursu", title_style))
    s.append(Paragraph("Detaylı Eğitmen Dokümantasyonu — 2 Gün", sub_style))
    s.append(Spacer(1, 1 * cm))
    s.append(info_table([
        ("Süre",           "2 gün — toplam ≈14 saat (kurulum hariç)"),
        ("Hedef kitle",    "Docker kullanan yazılım geliştiriciler"),
        ("Lab ortamı",     "Önceden kurulu Minikube + kubectl"),
        ("Format",         "Eğitmen anlatım + her bölümde uygulamalı lab"),
        ("Hedef çıktı",    "Temel ve orta seviye K8s nesnelerini ezbere değil anlayarak kullanabilme"),
    ]))
    s.append(Spacer(1, 1 * cm))
    s.append(Paragraph("Doküman Yapısı", h2))
    s.append(P("Her konu beş başlık altında işlenir:"))
    s.append(bullets([
        "<b>Amaç ve mantık</b> — neden var, hangi sorunu çözüyor?",
        "<b>Mimarideki yeri</b> — diğer K8s nesneleri ile ilişkisi (diyagramla)",
        "<b>Komutlar ve flag'ler</b> — imperative kullanım (tablolar)",
        "<b>Declarative — YAML manifest</b> — üretimde tercih edilen yöntem",
        "<b>İleri detaylar, best practice ve sık hatalar</b> — eğitmen notları",
    ]))
    s.append(PageBreak())


def timeline_section(s):
    s.append(Paragraph("Zaman Planı (Kurulum Hariç)", h1))
    s.append(P(
        "Kurulum (Minikube, kubectl, Docker doğrulaması) kurs öncesinde "
        "tamamlandığı varsayılır. İlk dakikadan itibaren mimari ile başlanır "
        "ve uygulamalı çalışma için en fazla zaman Pod, Deployment ve Service "
        "konularına ayrılır."))
    s.append(Spacer(1, 6))

    plan_rows = [
        ("M1. Kubernetes mimarisi",             "45 dk", "Anlatım + 2 mini lab"),
        ("M2. Pod",                              "120 dk", "5 lab senaryosu"),
        ("M3. ReplicaSet & Deployment",          "120 dk", "Rolling update, rollback"),
        ("M4. Service ve Ağ Modeli",             "120 dk", "ClusterIP/NodePort/LoadBalancer"),
        ("Toplam 1. gün",                        "≈ 6 saat 45 dk", "+ aralar"),
        ("M5. ConfigMap & Secret",               "90 dk",  "envFrom, volume mount"),
        ("M6. Volume, PV ve PVC",                "90 dk",  "emptyDir → PVC karşılaştırması"),
        ("M7. Namespace, Label, Annotation",     "45 dk",  "RBAC scope'u"),
        ("M8. Resource Yönetimi ve Probe'lar",   "75 dk",  "requests/limits + 3 probe"),
        ("M9. Ingress",                          "60 dk",  "Path/host routing"),
        ("M10. Kapanış projesi & sorun giderme", "90 dk",  "Tüm konuları birleştir"),
        ("Toplam 2. gün",                        "≈ 7 saat 30 dk", "+ aralar"),
    ]
    data = [["Modül", "Süre", "Açıklama"]] + [list(r) for r in plan_rows]
    t = Table(data, colWidths=[8 * cm, 3 * cm, 6 * cm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "DejaVu"),
        ("FONTNAME", (0, 0), (-1, 0), "DejaVu-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f6f8fb")]),
        ("BACKGROUND", (0, 4), (-1, 4), colors.HexColor("#eef2fb")),
        ("BACKGROUND", (0, 11), (-1, 11), colors.HexColor("#eef2fb")),
        ("FONTNAME", (0, 4), (-1, 4), "DejaVu-Bold"),
        ("FONTNAME", (0, 11), (-1, 11), "DejaVu-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#cccccc")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    s.append(t)
    s.append(PageBreak())


# ===========================================================================
# MODÜL 1 — Kubernetes Mimarisi (45 dk)
# ===========================================================================
def module_architecture(s):
    s.append(Paragraph("M1. Kubernetes Mimarisi (45 dk)", h1))
    s.append(P(
        "Kubernetes, deklaratif olarak belirtilen \"istenen durumu\" "
        "(<i>desired state</i>) sürekli olarak mevcut durumla karşılaştırıp "
        "farkı kapatmaya çalışan bir <b>kontrol döngüsü</b> sistemidir. "
        "Tüm bileşenler bu fikrin etrafında tasarlanmıştır."))

    s.append(Paragraph("Üst Seviye Görünüm", h2))
    s.append(diagram(dg.architecture_diagram()))

    s.append(Paragraph("Control Plane Bileşenleri — Detaylı", h2))

    s.append(Paragraph("kube-apiserver", h3))
    s.append(P(
        "Cluster'ın <b>tek giriş kapısıdır</b>. kubectl, kubelet, scheduler, "
        "controller'lar, dashboard — herkes RESTful HTTP üzerinden yalnızca "
        "API server ile konuşur. API server'ın görevleri:"))
    s.append(bullets([
        "REST endpoint'leri yayınlamak (örn. <code>/api/v1/namespaces/default/pods</code>).",
        "Kimlik doğrulama (authentication): mTLS sertifika, bearer token, OIDC.",
        "Yetkilendirme (authorization): RBAC, ABAC, Webhook.",
        "Admission control: kuralları (NamespaceLifecycle, ResourceQuota, "
            "MutatingWebhook, ValidatingWebhook) uygular; nesneyi reddedebilir veya değiştirebilir.",
        "etcd'ye yazma/okuma; <b>etcd'ye doğrudan erişebilen tek bileşendir</b>.",
        "Watch akışları: client'lar bir kaynağı izlerken API server değişiklikleri uzun süreli HTTP bağlantısı üzerinden push eder.",
    ]))

    s.append(Paragraph("etcd", h3))
    s.append(P(
        "Raft konsensüs algoritması kullanan, tutarlı, dağıtık bir <b>key-value "
        "store</b>'dur. Cluster'ın tüm durumu (Pod, Service, ConfigMap, Secret, "
        "RBAC, vs.) burada saklanır. Birkaç önemli detay:"))
    s.append(bullets([
        "Üretim kurulumlarında genellikle 3 veya 5 etcd üyesi (odd sayı) kullanılır; çoğunluk kaybı = cluster down.",
        "Yedek alınmazsa cluster geri getirilemez (<code>etcdctl snapshot save</code>).",
        "Encryption at rest <b>default kapalıdır</b>; üretimde mutlaka açın (KMS provider).",
        "Yalnızca kube-apiserver'a güvenir; doğrudan etcd'ye erişim üretimde tehlikelidir.",
    ]))

    s.append(Paragraph("kube-scheduler", h3))
    s.append(P(
        "Henüz <code>spec.nodeName</code> atanmamış Pod'ları izler ve onlara uygun "
        "Node'u seçer. İki ana evreden oluşur:"))
    s.append(bullets([
        "<b>Filtering (predicate):</b> Hangi Node'lar bu Pod'u çalıştırabilir? "
            "Yeterli CPU/RAM, uygun nodeSelector, taint/toleration, podAffinity/anti-affinity, "
            "volume topolojisi, port çakışması — bunlar değerlendirilir.",
        "<b>Scoring (priority):</b> Aday Node'lar puanlanır (least-requested, balanced-allocation, "
            "image-locality vs.); en yüksek puanlı seçilir.",
        "Karar verdikten sonra Pod tanımındaki <code>spec.nodeName</code>'i set eder ve API server'a yazar.",
        "Scheduler <b>Pod'u Node'a göndermez</b>; sadece atama yapar. Asıl çalıştırma kubelet'in işidir.",
    ]))

    s.append(Paragraph("kube-controller-manager (KCM) — En Önemli Bileşen", h3))
    s.append(P(
        "Tek bir binary içinde çalışan <b>onlarca controller</b>'ın bütünüdür. "
        "Her controller bağımsız bir kontrol döngüsü çalıştırır: <i>watch</i> "
        "→ <i>diff</i> (desired vs current) → <i>act</i>. Hepsi API server'a "
        "watch açıp ilgili kaynak tipini izler ve farkı kapatmaya çalışır."))
    s.append(P("KCM içindeki başlıca controller'lar:"))
    s.append(cmd_table([
        ("Deployment Controller",
            "Deployment nesnesini izler; her image/template değişiminde yeni bir <b>ReplicaSet</b> oluşturur, "
            "eskisini ölçeklemeye başlayıp yenisini büyüterek rolling update'i yönetir."),
        ("ReplicaSet Controller",
            "Bir RS için \"istenen replika sayısı\" ile \"mevcut Pod sayısı\" arasındaki farkı kapatır. "
            "Eksikse <b>Pod yaratır</b>, fazlaysa siler."),
        ("Node Controller",
            "Node sağlığını izler. <code>--node-monitor-grace-period</code> (default 40s) içinde "
            "kubelet'ten heartbeat gelmezse Node'u <i>NotReady</i> işaretler; "
            "<code>--pod-eviction-timeout</code> sonra üzerindeki Pod'ları siler (taint-based eviction)."),
        ("Endpoints / EndpointSlice Controller",
            "Service'in selector'ına uyan ve <b>Ready</b> olan Pod'ların IP:port listesini günceller. "
            "Bu liste kube-proxy'nin iptables/IPVS kurallarını yazması için kaynaktır."),
        ("ServiceAccount + Token Controller",
            "Her namespace için default ServiceAccount yaratır; ilgili Pod'lara "
            "ServiceAccount token Secret'ını otomatik mount eder."),
        ("Namespace Controller",
            "Namespace silindiğinde içindeki tüm kaynakları temizler (finalizer mekanizması)."),
        ("Job / CronJob Controller",
            "Job için gereken sayıda Pod oluşturur; CronJob zamana göre Job tetikler."),
        ("StatefulSet / DaemonSet Controller",
            "StatefulSet sıralı Pod yaratımı + PVC bağlama; DaemonSet her Node'a tam 1 Pod yerleştirir."),
        ("HPA Controller",
            "metrics-server'dan okur, hedef metriğe göre Deployment/StatefulSet replicas alanını günceller."),
        ("PersistentVolume Controller",
            "PVC'yi uygun PV ile bind eder; <i>provisioner</i> ile çalışıyorsa dinamik PV oluşturur."),
        ("Garbage Collector",
            "OwnerReferences zincirini takip eder; örnek: Deployment silinince ona ait RS ve Pod'lar otomatik silinir."),
    ]))
    s.append(tip(
        "Akılda kalsın: <b>scheduler Pod'u Node'a yerleştirir; kubelet Pod'u çalıştırır; "
        "geri kalan TÜM otomasyon (Pod'u kim yaratacak, kim canlı tutacak, kim sayacak, "
        "kim Service'e bağlayacak) kube-controller-manager içindedir.</b>"))

    s.append(Paragraph("cloud-controller-manager (CCM)", h3))
    s.append(P(
        "Cloud sağlayıcısına özgü controller'lar burada toplanır. Yalnızca bulut "
        "cluster'larında vardır (Minikube'de yoktur)."))
    s.append(bullets([
        "<b>Node Controller (cloud):</b> cloud API'sinden Node metadata'sını "
            "(zone, region, instance-type) çeker, etiketler.",
        "<b>Route Controller:</b> Pod CIDR'ları için VPC route table'larını günceller.",
        "<b>Service Controller:</b> <code>type: LoadBalancer</code> Service yaratıldığında "
            "cloud sağlayıcısının gerçek LoadBalancer'ını (ELB, GLB) provision eder, "
            "EXTERNAL-IP'yi geri yazar.",
    ]))

    s.append(Paragraph("Worker Node Bileşenleri", h2))
    s.append(cmd_table([
        ("kubelet",
            "Her Node'da bir adet. API server'a sürekli watch açar; "
            "kendisine atanan Pod'ları runtime üzerinde yaratır, probe'ları çalıştırır."),
        ("kube-proxy",
            "Service'in ClusterIP'sine gelen paketleri uygun Pod IP'sine "
            "yönlendiren iptables/IPVS kurallarını yönetir."),
        ("Container runtime",
            "containerd, CRI-O ya da Docker (deprecated). CRI arabirimi üzerinden konuşur."),
    ]))

    s.append(Paragraph("Reconciliation Loop (Kontrol Döngüsü)", h2))
    s.append(P(
        "Her controller şu kalıbı uygular: <b>watch</b> ile API server'dan ilgili "
        "kaynak değişikliklerini dinler, <b>diff</b> alır (desired vs current), "
        "ardından <b>act</b> ederek farkı kapatır. Pod silindiğinde ReplicaSet "
        "yeni Pod yaratır; Pod tanımı değiştiğinde Deployment yeni ReplicaSet açar."))

    s.append(Paragraph("Bir Pod Yaratılırken Olanlar — İki Senaryo", h2))
    s.append(P(
        "Pod nasıl yaratılırsa yaratılsın, her bileşen aynı kontrol döngüsü "
        "mantığını izler. Aşağıda iki yaygın senaryo karşılaştırmalı verilmiştir."))

    s.append(Paragraph("Senaryo A — Pod doğrudan oluşturuluyor", h3))
    s.append(P("<code>kubectl apply -f pod.yaml</code> ile çıplak bir Pod yaratıldığında:"))
    s.append(bullets([
        "<b>1. kubectl → kube-apiserver:</b> Manifest API server'a POST edilir.",
        "<b>2. kube-apiserver:</b> Authentication → Authorization (RBAC) → "
            "Admission Controllers (LimitRanger, ResourceQuota, MutatingWebhook, "
            "ValidatingWebhook) sırasıyla geçirilir. <b>ServiceAccount Admission</b> "
            "Pod'a default ServiceAccount token Secret'ını mount eder. "
            "Sonra etcd'ye yazılır; Pod <i>Pending</i> durumunda durur.",
        "<b>3. kube-scheduler:</b> nodeName'i boş olan Pod'u watch ile görür. "
            "Filtering + Scoring çalıştırır, en uygun Node'u seçer, "
            "<code>spec.nodeName</code>'i set ederek API server'a yazar.",
        "<b>4. kubelet (hedef Node'da):</b> kendisine atanmış Pod'u görür; container "
            "runtime'a (containerd/CRI-O) image pull + container start çağrısı yapar. "
            "Probe'ları yönetir, status'u günceller.",
        "<b>5. kube-controller-manager — Endpoints Controller:</b> Pod <i>Ready</i> "
            "olduğunda, eğer bu Pod'un label'larına uyan bir Service varsa, "
            "Service'in EndpointSlice'ına Pod IP'sini ekler. Kube-proxy bu değişikliği "
            "watch eder, iptables/IPVS kurallarını yazar — Pod artık trafik alır.",
        "<b>6. (Pod ölürse) Node Controller (KCM içinde):</b> kubelet heartbeat "
            "kesilirse Node'u NotReady işaretler; Pod'u <i>Terminating</i>'e geçirir. "
            "Çıplak Pod yeniden yaratılmaz — bu yüzden üretimde Deployment kullanılır.",
    ]))

    s.append(Paragraph("Senaryo B — Pod, Deployment ile oluşturuluyor (üretim)", h3))
    s.append(P("Üretimde Pod'lar genellikle Deployment üzerinden yaratılır. Akış zinciri uzar:"))
    s.append(bullets([
        "<b>1. kubectl → kube-apiserver:</b> Deployment manifest'i POST.",
        "<b>2. kube-apiserver:</b> Admission'dan geçer, Deployment etcd'ye yazılır.",
        "<b>3. KCM — Deployment Controller:</b> Yeni Deployment'ı görür; "
            "<code>pod-template-hash</code> etiketli yeni bir <b>ReplicaSet</b> yaratır.",
        "<b>4. KCM — ReplicaSet Controller:</b> RS'nin istenen replicas sayısını görür; "
            "her bir replika için bir <b>Pod nesnesi yaratır</b> ve API server'a yazar. "
            "Pod hâlâ nodeName boş (Pending).",
        "<b>5. kube-scheduler:</b> her Pod'a uygun Node seçer.",
        "<b>6. kubelet:</b> Pod'ları çalıştırır, runtime'a komut verir.",
        "<b>7. KCM — Endpoints / EndpointSlice Controller:</b> Ready olan Pod'ları "
            "Service'in endpoint listesine ekler.",
        "<b>8. (Bir Pod ölürse) KCM — ReplicaSet Controller</b> tekrar devreye girer, "
            "eksik replikayı kapatmak için yeni Pod yaratır → self-healing budur.",
        "<b>9. (Image güncellenirse) KCM — Deployment Controller</b> yeni RS açar, "
            "eskisini ölçek aşağı çekerek rolling update başlatır.",
    ]))
    s.append(tip(
        "Görüldüğü gibi <b>kube-controller-manager iki seviyede</b> aktiftir: "
        "(a) Pod yaratımı için Deployment → ReplicaSet zincirini sürmek, "
        "(b) Pod yaratıldıktan sonra hayatta tutmak, Service'e bağlamak, "
        "Node arızasını yönetmek. Scheduler ve kubelet \"tek seferlik\" işler "
        "yaparken, KCM <b>sürekli</b> çalışan beyin gibidir."))

    s.append(Paragraph("45 Dakikalık Akış Önerisi", h2))
    s.append(info_table([
        ("0-10 dk", "Kontrol döngüsü fikrini anlat; cluster topolojisini çiz."),
        ("10-25 dk", "Control plane bileşenlerini sırayla işle; her birinin sorumluluğunu örneklerle göster."),
        ("25-35 dk", "Worker tarafı: kubelet'in API server'a watch açması, kube-proxy'nin iptables kuralları."),
        ("35-45 dk", "Lab: kubectl get nodes -o wide, kubectl get pods -n kube-system, kubectl logs -n kube-system kube-controller-manager-... — bileşenleri yaşayan halde göster."),
    ], widths=[3 * cm, 14 * cm]))

    s.append(Paragraph("Mini Lab — Cluster'ı tanıyın", h3))
    s.append(code(
        "kubectl cluster-info\n"
        "kubectl get nodes -o wide\n"
        "kubectl get pods -n kube-system           # control plane Pod'ları\n"
        "kubectl get pods -n kube-system -l component=kube-controller-manager\n"
        "kubectl logs -n kube-system -l component=kube-controller-manager --tail=20\n"
        "kubectl api-resources | head -20\n"
        "kubectl explain pod.spec --recursive | head -40"
    ))

    s.append(PageBreak())


# ===========================================================================
# MODÜL 2 — POD
# ===========================================================================
def module_pod(s):
    topic_section(
        s,
        title="M2. Pod (120 dk)",
        purpose_paras=[
            "Pod, Kubernetes'te <b>dağıtımın en küçük birimidir</b>. Bir Pod, "
            "birlikte çalışması mantıklı olan bir veya birden fazla "
            "konteynerden oluşur ve şu kaynakları <b>paylaşır</b>: aynı ağ "
            "ad uzayı (Pod IP), aynı IPC ad uzayı, paylaşılan volume'ler.",
            "Tek konteynerli Pod en yaygın kullanımdır. Çok konteynerli Pod "
            "kalıbına klasik örnek <i>sidecar</i> (log toplayıcı, proxy, "
            "config reloader gibi).",
            "Pod, kendi başına <b>yeniden başlatılmaz</b> ve <b>ölçeklenmez</b>. "
            "Self-healing isteniyorsa ReplicaSet veya Deployment kullanılmalıdır. "
            "Tek başına Pod, ancak özel durumlarda (debug, geçici görev) anlamlıdır.",
        ],
        place_paras=[
            "Pod, scheduler tarafından bir Node'a yerleştirilir ve o Node'daki "
            "kubelet tarafından yaşatılır. Aynı Pod'daki konteynerler her "
            "zaman aynı Node'da olur; bunlar başka Pod'lara dağıtılamaz."
        ],
        place_diagram=dg.pod_anatomy_diagram(),
        commands_intro=[
            "Pod'u imperative yaratmanın en hızlı yolu <code>kubectl run</code> "
            "komutudur. Üretimde bunun yerine YAML manifest tercih edilir."
        ],
        command_rows=[
            ("kubectl run nginx --image=nginx:1.27",
                "Tek bir Pod yaratır (eski sürümlerde Deployment yaratırdı; 1.18+ artık sadece Pod)."),
            ("kubectl get pods -o wide",
                "Pod listesi + IP, Node, durum."),
            ("kubectl describe pod &lt;ad&gt;",
                "Events, container status, probe sonuçları, mount detayları."),
            ("kubectl logs &lt;ad&gt; [-c &lt;container&gt;] [-f] [--tail=N]",
                "Konteyner stdout/stderr. Çok konteynerli Pod'da <code>-c</code> zorunludur. "
                "<code>-f</code> follow (canlı izleme), <code>--tail=N</code> son N satır, "
                "<code>--since=10m</code> son 10 dakika, <code>--timestamps</code> her satıra zaman damgası ekler."),
            ("kubectl logs &lt;ad&gt; --previous (veya -p)",
                "<b>Bir önceki</b> konteyner instance'ının loglarını gösterir. Konteyner crash olup restart edildiğinde "
                "<code>kubectl logs &lt;ad&gt;</code> sadece yeni başlayan instance'ı gösterir — ama yeni instance henüz "
                "hata üretmediyse boş çıkar. <code>--previous</code> ile <b>az önce ölen</b> konteynerin son stdout/stderr "
                "çıktısını okursunuz; CrashLoopBackOff teşhisinde birinci başvurulan komuttur. "
                "Yalnızca bir önceki instance'ı saklar; iki önce öleni gösteremez. "
                "<code>-c</code> ile çok konteynerli Pod'da hedef konteyneri seçin."),
            ("kubectl exec -it &lt;ad&gt; -- sh",
                "Pod içinde shell. <code>--</code> sonrası komut çalışır."),
            ("kubectl port-forward pod/&lt;ad&gt; 8080:80",
                "Lokal makineden Pod'a tünel."),
            ("kubectl cp local.txt &lt;ad&gt;:/tmp/",
                "Dosya kopyalama (debug için)."),
            ("kubectl delete pod &lt;ad&gt; [--grace-period=0 --force]",
                "Pod'u sonlandırır; force ise grace period beklemez."),
            ("kubectl get pod &lt;ad&gt; -o yaml",
                "Mevcut tanımı YAML olarak görür (status dahil)."),
            ("kubectl debug -it &lt;ad&gt; --image=busybox --target=&lt;c&gt;",
                "Ephemeral debug container ekler (K8s 1.25+)."),
        ],
        flag_intro=[
            "<code>kubectl run</code> için en sık kullanılan flag'ler:"
        ],
        flag_rows=[
            ("--image=&lt;img&gt;",      "Çalıştırılacak konteyner image'ı.",                     "--image=nginx:1.27"),
            ("--port=&lt;n&gt;",         "containerPort tanımlar (Pod IP üzerinden açılır).",     "--port=8080"),
            ("--env=KEY=VAL",            "Ortam değişkeni enjekte eder; birden çok kullanılabilir.", "--env=APP_MODE=dev"),
            ("--labels=k1=v1,k2=v2",     "Pod'a etiket ekler. Service selector'ları için kritik.",  "--labels=app=web,tier=front"),
            ("--restart=Never",
                "Pod'un <code>restartPolicy</code>'sini <b>Never</b>'a set eder. Konteyner exit ettiğinde kubelet "
                "konteyneri yeniden başlatmaz; Pod <i>Failed</i>/<i>Succeeded</i> terminal durumuna düşer. "
                "Tek seferlik komutlar, batch işler, debug için idealdir. "
                "Diğer değerler: <b>Always</b> (default — her exit'te yeniden başlat), "
                "<b>OnFailure</b> (yalnız hatalı exit'te yeniden başlat — Job senaryosu).",
                "--restart=Never"),
            ("--rm",                     "Pod sonlanınca otomatik temizle. --restart=Never ile birlikte kullanılır.",  "--rm"),
            ("--command -- &lt;cmd&gt;", "Image'ın default ENTRYPOINT/CMD'sini ezer; tüm argümanlar konteynere geçer.", "--command -- sleep 3600"),
            ("--dry-run=client -o yaml", "Manifest üretir, uygulamaz. apply etmeden YAML görmek için.",                 "&gt; pod.yaml"),
            ("-n &lt;namespace&gt;",     "Hangi namespace'te oluşturulacak.",                                            "-n dev"),
            ("--image-pull-policy",
                "Konteyner image'ının ne zaman çekileceğini belirler: "
                "<b>Always</b> — her Pod start'ında registry'den yeniden çek (tag :latest için default). "
                "<b>IfNotPresent</b> — image Node'da zaten varsa kullan, yoksa çek (sabit tag için default). "
                "<b>Never</b> — asla çekme; image Node'da yoksa Pod ErrImageNeverPull verir. "
                "Minikube'de <code>minikube image load</code> ile yüklenen lokal image'ları kullanmak için "
                "<b>Never</b> veya <b>IfNotPresent</b> şarttır, yoksa K8s registry'ye uzanır ve hata alır.",
                "--image-pull-policy=IfNotPresent"),
        ],
        yaml_intro=[
            "Yaml manifest hem versiyon kontrolüne girer hem de tekrarlanabilir. "
            "<b>spec.containers</b> bir liste olduğu için her Pod birden fazla "
            "konteyner barındırabilir."
        ],
        yaml_code=(
            "apiVersion: v1\n"
            "kind: Pod\n"
            "metadata:\n"
            "  name: web\n"
            "  labels:\n"
            "    app: web\n"
            "    tier: front\n"
            "spec:\n"
            "  restartPolicy: Always       # Always | OnFailure | Never\n"
            "  terminationGracePeriodSeconds: 30\n"
            "  containers:\n"
            "  - name: nginx\n"
            "    image: nginx:1.27\n"
            "    imagePullPolicy: IfNotPresent\n"
            "    ports:\n"
            "    - name: http\n"
            "      containerPort: 80\n"
            "      protocol: TCP\n"
            "    env:\n"
            "    - name: APP_MODE\n"
            "      value: \"prod\"\n"
            "    - name: POD_NAME           # Downward API\n"
            "      valueFrom:\n"
            "        fieldRef:\n"
            "          fieldPath: metadata.name\n"
            "    resources:\n"
            "      requests:\n"
            "        cpu: \"50m\"\n"
            "        memory: \"64Mi\"\n"
            "      limits:\n"
            "        cpu: \"500m\"\n"
            "        memory: \"256Mi\"\n"
            "    volumeMounts:\n"
            "    - name: cache\n"
            "      mountPath: /var/cache/nginx\n"
            "  volumes:\n"
            "  - name: cache\n"
            "    emptyDir: {}\n"
        ),
        advanced_items=[
            "<b>restartPolicy</b> Pod seviyesindedir; Deployment her zaman <code>Always</code> ister. "
                "OnFailure/Never yalnızca Job/CronJob senaryolarında anlamlıdır.",
            "<b>containerPort</b> sadece <i>bilgi amaçlıdır</i> — Pod'un IP'sine gerçek port erişimini engellemez. "
                "Asıl önemi Service'in <code>targetPort: http</code> gibi <b>isimle</b> referans verebilmesidir.",
            "<b>imagePullPolicy</b>: tag <code>:latest</code> ise default <code>Always</code>, "
                "sabit tag ise <code>IfNotPresent</code>'tır. Sabit tag kullanın, <code>:latest</code>'tan kaçının.",
            "<b>Pod yaşam döngüsü:</b> Pending → ContainerCreating → Running → "
                "Succeeded/Failed/Terminating. Terminal durumlar yeniden başlatılmaz.",
            "<b>Init containers</b> sıralı çalışır; tümü tamamlanmadan ana konteynerler başlamaz. "
                "Bağımlılık beklemek, şema migrasyonu, dosya hazırlamak için idealdir.",
            "<b>Ephemeral containers</b> (1.25+) ile çalışan Pod'a debug konteyneri eklenebilir; "
                "<code>kubectl debug</code>. Hiçbir Pod yeniden başlatılmaz.",
            "<b>Pod IP geçicidir:</b> Pod silinince yeni Pod yeni IP alır. Bu yüzden başka uygulamalar "
                "Pod IP'sine değil, <i>Service</i>'in DNS adına bağlanmalıdır.",
            "<b>terminationGracePeriodSeconds</b> (default 30): Pod'a SIGTERM atılır, bu süre kadar beklenir, "
                "süre dolarsa SIGKILL. preStop hook ile düzgün kapanış senaryosu kurgulanabilir.",
            "<b>SecurityContext:</b> <code>runAsNonRoot: true</code>, "
                "<code>allowPrivilegeEscalation: false</code>, <code>readOnlyRootFilesystem: true</code> — "
                "üretim için minimum şart.",
            "<b>Sık hata:</b> Pod'u doğrudan ölçeklemeye çalışmak. Pod ölçeklenemez — onun yerine ReplicaSet veya Deployment.",
            "<b>Sık hata:</b> Konteyner ölünce \"Pod öldü\" sanmak. Aynı Pod içindeki konteyner restart edilebilir; "
                "Pod hâlâ aynı IP'dedir. <code>kubectl get pod</code> RESTARTS sütununu izleyin.",
            "<b>Image olmadan başarısız Pod:</b> Status <code>ErrImagePull</code> veya <code>ImagePullBackOff</code>. "
                "Çözüm: image tag'i, registry erişimi ve imagePullSecrets'i kontrol edin.",
        ],
    )

    s.append(Paragraph("Lab — Pod ile yapılacaklar", h3))
    s.append(code(
        "# 1) Tek konteynerli Pod\n"
        "kubectl run web --image=nginx:1.27 --port=80 --labels=app=web\n"
        "kubectl get pods -o wide\n"
        "kubectl describe pod web | head -40\n"
        "kubectl port-forward pod/web 8080:80 &\n"
        "curl http://localhost:8080\n\n"
        "# 2) İki konteynerli Pod (sidecar)\n"
        "kubectl apply -f sidecar-pod.yaml\n"
        "kubectl logs sidecar -c app\n"
        "kubectl logs sidecar -c log-shipper\n\n"
        "# 3) Ephemeral debug\n"
        "kubectl debug -it web --image=busybox --target=web -- sh\n\n"
        "# 4) Pod yaşam döngüsünü gör\n"
        "kubectl delete pod web --grace-period=0 --force\n"
    ))
    s.append(diagram(dg.pod_lifecycle_diagram()))
    s.append(PageBreak())


# ===========================================================================
# MODÜL 3 — ReplicaSet ve Deployment
# ===========================================================================
def module_deployment(s):
    topic_section(
        s,
        title="M3. ReplicaSet ve Deployment (120 dk)",
        purpose_paras=[
            "<b>ReplicaSet</b> belirli sayıda Pod'un her zaman çalışır kalmasını "
            "sağlar. Selector'a göre eşleşen Pod sayısını sayar; eksikse "
            "yeni Pod yaratır, fazla ise siler. Self-healing budur.",
            "<b>Deployment</b>, ReplicaSet'in üzerine <b>rollout</b>, "
            "<b>rollback</b> ve <b>history</b> ekler. Bir Deployment her image "
            "değişikliğinde yeni bir ReplicaSet yaratır; trafiği kademeli olarak "
            "eski RS'den yeni RS'e kaydırır.",
            "Üretim ortamında doğrudan ReplicaSet yazılmaz — her zaman "
            "Deployment ile yönetilir.",
        ],
        place_paras=[
            "Deployment → yeni bir ReplicaSet → bu RS, label selector ile "
            "kendi Pod'larını sahiplenir. Bu zincir kurslarda en çok kafa "
            "karıştıran konudur ve dikkatle anlatılmalıdır."
        ],
        place_diagram=dg.replicaset_self_healing(),
        commands_intro=[
            "Aşağıdaki komutlar gündelik kullanımın %90'ını kapsar:"
        ],
        command_rows=[
            ("kubectl create deployment web --image=nginx:1.27 --replicas=3",
                "Hızlı oluşturma (imperative). Manifest üretmek için <code>--dry-run=client -o yaml</code>."),
            ("kubectl get deploy,rs,pods -l app=web",
                "Deployment → RS → Pod zincirini birlikte görür."),
            ("kubectl scale deploy/web --replicas=5",
                "Replika sayısını anlık değiştirir."),
            ("kubectl set image deploy/web nginx=nginx:1.28",
                "Konteynerin image'ını günceller; yeni rollout tetikler."),
            ("kubectl rollout status deploy/web",
                "Rollout'un ilerleyişini gerçek zamanlı izler."),
            ("kubectl rollout history deploy/web",
                "Tüm revizyonları listeler."),
            ("kubectl rollout undo deploy/web [--to-revision=N]",
                "Önceki sürüme döner; isteğe bağlı belirli revizyona."),
            ("kubectl rollout pause/resume deploy/web",
                "Devam eden rollout'u duraklatır/devam ettirir."),
            ("kubectl rollout restart deploy/web",
                "Aynı image'la yeni rollout — env/ConfigMap değişimi sonrası kullanılır."),
            ("kubectl edit deploy/web",
                "Tanımı editörle aç; kaydedince diff uygulanır."),
        ],
        flag_intro=[
            "Deployment'a özgü kritik alanlar (YAML'da kullanılan ama komutta "
            "<code>--set</code>/<code>-p</code> ile de düzeltilebilen):"
        ],
        flag_rows=[
            ("strategy.type",
                "RollingUpdate (default) veya Recreate (önce tamamı durur).",
                "Recreate"),
            ("rollingUpdate.maxSurge",
                "Hedef replikanın üzerine ekstra kaç Pod açılabilir.",
                "25% veya 1"),
            ("rollingUpdate.maxUnavailable",
                "Aynı anda kaç Pod hazır olmayabilir.",
                "25% veya 0"),
            ("revisionHistoryLimit",
                "Saklanan eski RS sayısı (rollback için).",
                "10 (default)"),
            ("progressDeadlineSeconds",
                "Rollout bu süre içinde ilerlemezse fail sayılır.",
                "600 (default)"),
            ("minReadySeconds",
                "Bir Pod hazır sayıldıktan sonra bekleme süresi.",
                "10"),
            ("--record",
                "(eski) kubectl komutunu annotation'a yazar.",
                "kubectl set image ... --record"),
        ],
        yaml_intro=[
            "Aşağıdaki manifest 'altın standart' bir Deployment örneğidir:"
        ],
        yaml_code=(
            "apiVersion: apps/v1\n"
            "kind: Deployment\n"
            "metadata:\n"
            "  name: web\n"
            "  labels: { app: web }\n"
            "spec:\n"
            "  replicas: 3\n"
            "  revisionHistoryLimit: 5\n"
            "  strategy:\n"
            "    type: RollingUpdate\n"
            "    rollingUpdate:\n"
            "      maxSurge: 1\n"
            "      maxUnavailable: 0     # her zaman tüm replikalar hazır\n"
            "  selector:\n"
            "    matchLabels: { app: web }\n"
            "  template:                # bu kısım Pod template'i\n"
            "    metadata:\n"
            "      labels: { app: web } # selector ile birebir uyumlu OLMALI\n"
            "    spec:\n"
            "      containers:\n"
            "      - name: web\n"
            "        image: nginx:1.27\n"
            "        ports: [{ name: http, containerPort: 80 }]\n"
            "        readinessProbe:\n"
            "          httpGet: { path: /, port: http }\n"
            "          periodSeconds: 5\n"
            "        resources:\n"
            "          requests: { cpu: 50m, memory: 64Mi }\n"
            "          limits:   { cpu: 500m, memory: 256Mi }\n"
        ),
        advanced_items=[
            "<b>selector immutable'dır</b>: bir kere ayarlanan <code>spec.selector</code> "
                "sonradan değiştirilemez (yeni Deployment oluşturmak gerekir).",
            "<b>Template label'ları selector'la birebir uyumlu olmak zorunda.</b> "
                "Olmazsa <code>kubectl apply</code> hata verir.",
            "<b>maxUnavailable: 0</b> + <b>readinessProbe</b> = sıfır downtime rollout. "
                "Readiness probe yoksa Pod \"hazır değil\" sinyalini veremez ve trafik kesilebilir.",
            "<b>Pause/Resume</b>: birden fazla değişikliği tek seferde uygulamak için rollout'u "
                "<code>pause</code> ile durdurun, değişiklikleri yapın, <code>resume</code> ile başlatın.",
            "<b>Rollback hızlıdır</b>: önceki RS hâlâ duruyor olabilir (revisionHistoryLimit). "
                "Bu yüzden bu değeri çok düşük tutmayın.",
            "<b>Pod template hash etiketi</b>: K8s her RS'e <code>pod-template-hash</code> ekler. "
                "Bu sayede selector'lar çakışmaz; bu etikete manuel müdahale etmeyin.",
            "<b>Recreate stratejisi</b> StatefulSet/DB benzeri uygulamalar için bazen tercih edilir; "
                "downtime yaşar ama veri tutarlılığı korur.",
            "<b>Sık hata:</b> <code>kubectl apply</code> sonrası rollout başlamıyorsa, "
                "muhtemelen sadece etiket veya annotation değişmiştir; image değişmediğinde RS yeniden oluşmaz.",
            "<b>Sık hata:</b> Yanlış selector. Eski Pod'lar Deployment tarafından sahiplenilirse "
                "(çakışan label) beklenmedik replikalar oluşur.",
            "<b>HPA ile etkileşim:</b> Deployment'a HPA bağlıysa <code>spec.replicas</code> alanını "
                "manifest'ten <b>kaldırın</b> (yoksa apply her seferinde geri çeker).",
        ],
    )

    s.append(Paragraph("Rolling Update Akışı — görsel", h3))
    s.append(diagram(dg.rolling_update_diagram()))

    s.append(Paragraph("Lab — Rolling update + rollback senaryosu", h3))
    s.append(code(
        "# 1) Deployment kur\n"
        "kubectl create deployment web --image=nginx:1.27 --replicas=3\n"
        "kubectl rollout status deploy/web\n\n"
        "# 2) Yeni image yayınla, kaydı izle\n"
        "kubectl set image deploy/web nginx=nginx:1.28\n"
        "watch 'kubectl get pods -l app=web'\n\n"
        "# 3) Bilerek hatalı image yayınla\n"
        "kubectl set image deploy/web nginx=nginx:hatali\n"
        "kubectl rollout status deploy/web --timeout=30s\n"
        "kubectl rollout undo deploy/web\n\n"
        "# 4) Replika sayısını HPA gibi değiştir\n"
        "kubectl scale deploy/web --replicas=6\n"
    ))
    s.append(PageBreak())


# ===========================================================================
# MODÜL 4 — SERVICE VE AĞ MODELİ
# ===========================================================================
def module_service(s):
    topic_section(
        s,
        title="M4. Service ve Ağ Modeli (120 dk)",
        purpose_paras=[
            "Pod IP'leri geçicidir; Pod silinince yeni Pod yeni IP alır. "
            "Bu yüzden başka uygulamalar Pod IP'sine değil <b>Service</b> adıyla "
            "bağlanır. Service, label selector ile eşleşen Pod'lara <b>kararlı</b> "
            "bir sanal IP (ClusterIP) ve DNS adı sağlar.",
            "Service, gelen trafiği selector ile bulduğu Pod'lara dağıtır. "
            "Dağıtım, kube-proxy'nin Node'lara yazdığı iptables/IPVS kuralları "
            "üzerinden L4 seviyesinde yapılır (TCP/UDP, default round-robin).",
            "Service türleri farklı erişim ihtiyaçları için vardır: cluster içi "
            "(ClusterIP), Node üstünden (NodePort), bulut LB ile (LoadBalancer) "
            "ya da harici DNS yönlendirmesi (ExternalName).",
        ],
        place_paras=[
            "Service tanımı API server'da saklanır; Endpoints / EndpointSlice "
            "controller, selector'a uyan Pod'ları izleyip endpoint listesini "
            "günceller. Her Node'daki kube-proxy bu listeyi okuyup iptables/"
            "IPVS kurallarını yazar.",
        ],
        place_diagram=dg.service_selector_diagram(),
        commands_intro=[
            "Service'in en yaygın komutları:"
        ],
        command_rows=[
            ("kubectl expose deploy/web --port=80 --target-port=80",
                "Hızlıca ClusterIP Service yaratır."),
            ("kubectl expose deploy/web --port=80 --type=NodePort",
                "NodePort olarak açar; port otomatik atanır."),
            ("kubectl get svc",
                "Service'leri listeler; CLUSTER-IP, EXTERNAL-IP, PORT(S) sütunlarına bakın."),
            ("kubectl get endpoints &lt;ad&gt; -o wide",
                "Service'in mevcut endpoint listesini (Pod IP:port) gösterir."),
            ("kubectl get endpointslices",
                "Modern EndpointSlice nesneleri (1.21+ default)."),
            ("kubectl describe svc &lt;ad&gt;",
                "Selector, ports, endpoints, sessionAffinity ayrıntıları."),
            ("kubectl port-forward svc/&lt;ad&gt; 8080:80",
                "Lokal makineden Service'e tünel."),
            ("kubectl run probe --rm -it --image=busybox -- wget -qO- web.default.svc.cluster.local",
                "Cluster içi DNS ile Service çağırma testi."),
            ("kubectl patch svc &lt;ad&gt; -p '{\"spec\":{\"type\":\"NodePort\"}}'",
                "Mevcut Service'in tipini değiştirir."),
        ],
        flag_intro=[
            "<code>kubectl expose</code> ve Service tanımında öne çıkan flag'ler:"
        ],
        flag_rows=[
            ("--port",            "Service'in açtığı port (cluster içinden).",          "--port=80"),
            ("--target-port",     "Pod üzerindeki containerPort veya ismi.",            "--target-port=http"),
            ("--type",            "ClusterIP | NodePort | LoadBalancer | ExternalName.","--type=NodePort"),
            ("--protocol",        "TCP (default) | UDP | SCTP.",                        "--protocol=UDP"),
            ("--selector",        "Eşleşecek Pod label'larını override eder.",          "--selector=app=web"),
            ("--cluster-ip=None", "Headless Service (DNS A kayıtları her Pod için).",  "(StatefulSet için yaygın)"),
            ("nodePort",          "NodePort manuel set; 30000-32767 aralığı.",          "30080"),
            ("sessionAffinity",   "ClientIP olursa aynı IP aynı Pod'a yapışır.",        "ClientIP"),
            ("externalTrafficPolicy", "Local: trafiği aynı Node'daki Pod'a tut, kaynak IP korunur.", "Local"),
        ],
        yaml_intro=[
            "ClusterIP + NodePort + Service ports için isimli targetPort kullanımı:"
        ],
        yaml_code=(
            "apiVersion: v1\n"
            "kind: Service\n"
            "metadata:\n"
            "  name: web\n"
            "  labels: { app: web }\n"
            "spec:\n"
            "  type: ClusterIP        # default; NodePort/LoadBalancer da olabilir\n"
            "  selector: { app: web } # Deployment.spec.template.labels ile uyumlu\n"
            "  ports:\n"
            "  - name: http\n"
            "    port: 80             # cluster içinden bu port\n"
            "    targetPort: http     # Pod'daki containerPort adı veya numarası\n"
            "    protocol: TCP\n"
            "  sessionAffinity: None  # ClientIP da yapılabilir\n"
            "---\n"
            "# Aynı Pod'lara ikinci bir NodePort Service\n"
            "apiVersion: v1\n"
            "kind: Service\n"
            "metadata:\n"
            "  name: web-np\n"
            "spec:\n"
            "  type: NodePort\n"
            "  selector: { app: web }\n"
            "  ports:\n"
            "  - { port: 80, targetPort: http, nodePort: 30080 }\n"
        ),
        advanced_items=[
            "<b>DNS adı kalıbı:</b> <code>&lt;service&gt;.&lt;namespace&gt;.svc.cluster.local</code>. "
                "Aynı namespace içinden sadece <code>web</code> de yeterlidir.",
            "<b>Headless Service</b> (<code>clusterIP: None</code>) StatefulSet ile birlikte kullanılır; "
                "her Pod için ayrı DNS kaydı döner (pod-0.app, pod-1.app gibi).",
            "<b>EndpointSlice vs Endpoints:</b> Endpoint nesnesi büyük cluster'larda performans sorunu "
                "yaşıyordu; 1.21+ EndpointSlice default oldu (büyük listeyi parçalara böler).",
            "<b>ExternalName</b> Service: selector yok, DNS CNAME yönlendirmesi (örn. <code>db.prod.example.com</code>).",
            "<b>sessionAffinity: ClientIP</b> sticky session sağlar; cookie tabanlı sticky değildir.",
            "<b>externalTrafficPolicy: Local</b> NodePort/LB için kaynak IP'yi korur, ama o Node'da Pod yoksa istek <i>düşer</i>.",
            "<b>Sık hata:</b> Service yaratıldı ama endpoint listesi boş. Sebep: selector yanlış, Pod label'ları "
                "uyuşmuyor ya da Pod henüz Ready değil (readiness probe fail).",
            "<b>Sık hata:</b> <code>targetPort</code>'u image'ın gerçekten dinlediği port ile karıştırmak. "
                "Container 8080 dinlerken targetPort 80 ise istek zaman aşımı yer.",
            "<b>kube-proxy mod:</b> iptables (default) vs IPVS. Büyük cluster'larda IPVS daha performanslı.",
            "<b>NetworkPolicy</b> (ileri): Service'ler default olarak her Pod'dan erişilebilir. "
                "Cluster'da Calico/Cilium gibi NetworkPolicy destekli CNI varsa, traffik filtrelenebilir.",
            "<b>İpucu — debug:</b> <code>kubectl run probe --rm -it --image=nicolaka/netshoot</code> ile "
                "dig, curl, tcpdump, nslookup gibi araçlara erişin.",
        ],
    )

    s.append(Paragraph("Service Türleri — Karşılaştırma", h3))
    s.append(diagram(dg.service_types_diagram()))

    s.append(Paragraph("Lab — Service ile ulaşılabilirlik", h3))
    s.append(code(
        "kubectl create deployment web --image=nginx:1.27 --replicas=3\n"
        "kubectl expose deploy/web --port=80 --type=ClusterIP\n"
        "kubectl get endpoints web -o wide\n\n"
        "# Cluster içi DNS testi\n"
        "kubectl run probe --rm -it --image=busybox -- sh\n"
        "  > wget -qO- web.default.svc.cluster.local\n"
        "  > nslookup web\n\n"
        "# NodePort'a yükselt ve dışarıdan eriş\n"
        "kubectl patch svc web -p '{\"spec\":{\"type\":\"NodePort\"}}'\n"
        "minikube service web --url\n"
    ))
    s.append(PageBreak())


# ===========================================================================
# MODÜL 5 — ConfigMap ve Secret
# ===========================================================================
def module_configmap_secret(s):
    topic_section(
        s,
        title="M5. ConfigMap ve Secret (90 dk)",
        purpose_paras=[
            "12-factor uygulama prensibi gereği <b>yapılandırma image'tan ayrı</b> "
            "olmalıdır. <b>ConfigMap</b> düz metin yapılandırmayı, <b>Secret</b> "
            "ise hassas verileri (parola, token, sertifika) Pod'lara taşımak "
            "için kullanılır.",
            "Her ikisi de key/value yapısındadır. Tek fark: Secret değerleri "
            "base64 ile kodlanmıştır ve etcd'de (varsayılan olarak) "
            "şifrelenmemiş tutulur. Bu yüzden Secret ≠ \"şifreli\"; "
            "<i>encryption at rest</i> ayrıca açılmalıdır.",
            "ConfigMap/Secret üç şekilde Pod'a aktarılır: tek tek env değişkeni "
            "(<code>env.valueFrom</code>), toplu env (<code>envFrom</code>), "
            "dosya olarak volume mount.",
        ],
        place_paras=[
            "Her iki nesne de namespace seviyesindedir. Volume olarak mount "
            "edildiklerinde ConfigMap güncellendiğinde Pod yeniden başlatılmadan "
            "yaklaşık 30-60 sn içinde dosya içeriği tazelenir. <b>Env olarak</b> "
            "enjekte edilen değerler tazelenmez — Pod restart gerekir."
        ],
        place_diagram=dg.configmap_secret_flow(),
        commands_intro=[
            "Hızlı oluşturma yolları:"
        ],
        command_rows=[
            ("kubectl create configmap app --from-literal=KEY=val1 --from-literal=K2=val2",
                "Literal değerlerden ConfigMap."),
            ("kubectl create configmap app --from-file=./config.json",
                "Tek dosyadan ConfigMap; key = dosya adı, value = içerik."),
            ("kubectl create configmap app --from-file=cfg/",
                "Dizindeki tüm dosyalar ayrı key olur."),
            ("kubectl create configmap app --from-env-file=.env",
                ".env formatında çoklu key/value."),
            ("kubectl create secret generic db --from-literal=PASSWORD='S3cret!'",
                "Opaque tipinde generic Secret."),
            ("kubectl create secret docker-registry regcred --docker-server=... --docker-username=... --docker-password=...",
                "Private registry için imagePullSecrets."),
            ("kubectl create secret tls web-tls --cert=cert.pem --key=key.pem",
                "TLS sertifikası Secret'ı (Ingress için)."),
            ("kubectl get cm,secret",
                "Listele."),
            ("kubectl get secret db -o jsonpath='{.data.PASSWORD}' | base64 -d",
                "Secret değerini decode ederek görür."),
            ("kubectl edit cm app",
                "Canlı olarak düzenle; volume mount edilmişse içerik tazelenir."),
        ],
        flag_intro=[
            "<code>kubectl create configmap/secret</code> için en sık kullanılan flag'ler:"
        ],
        flag_rows=[
            ("--from-literal",       "key=value şeklinde tek bir giriş.",         "--from-literal=APP_MODE=prod"),
            ("--from-file",          "Dosya veya dizinden.",                       "--from-file=app.conf"),
            ("--from-file=name=path","Custom key adı ile dosyadan.",               "--from-file=conf=./prod.json"),
            ("--from-env-file",      ".env dosyası formatından.",                  "--from-env-file=.env"),
            ("--type",               "Secret için: generic | docker-registry | tls.", "--type=tls"),
            ("--dry-run=client -o yaml", "Manifest üretir, uygulamaz.",           "&gt; cm.yaml"),
            ("-n &lt;namespace&gt;", "Namespace.",                                 "-n dev"),
        ],
        yaml_intro=[
            "ConfigMap + Secret + Pod entegrasyonu örneği:"
        ],
        yaml_code=(
            "apiVersion: v1\n"
            "kind: ConfigMap\n"
            "metadata: { name: app-config }\n"
            "data:\n"
            "  APP_MODE: prod\n"
            "  LOG_LEVEL: info\n"
            "  appsettings.json: |\n"
            "    { \"feature\": true }\n"
            "---\n"
            "apiVersion: v1\n"
            "kind: Secret\n"
            "metadata: { name: app-secret }\n"
            "type: Opaque\n"
            "stringData:               # base64'e otomatik dönüştürülür\n"
            "  DB_PASSWORD: 'S3cret!'\n"
            "---\n"
            "apiVersion: v1\n"
            "kind: Pod\n"
            "metadata: { name: app }\n"
            "spec:\n"
            "  containers:\n"
            "  - name: app\n"
            "    image: myapp:1.0\n"
            "    envFrom:                # tüm ConfigMap key'leri env olur\n"
            "    - configMapRef: { name: app-config }\n"
            "    - secretRef:    { name: app-secret }\n"
            "    env:                    # tek bir Secret değerini özel adla\n"
            "    - name: DB_PWD\n"
            "      valueFrom:\n"
            "        secretKeyRef:\n"
            "          name: app-secret\n"
            "          key: DB_PASSWORD\n"
            "    volumeMounts:\n"
            "    - { name: cfg, mountPath: /etc/app, readOnly: true }\n"
            "  volumes:\n"
            "  - name: cfg\n"
            "    configMap:\n"
            "      name: app-config\n"
            "      items:\n"
            "      - { key: appsettings.json, path: appsettings.json }\n"
        ),
        advanced_items=[
            "<b>Volume mount canlıdır</b>: ConfigMap güncellenince Pod yeniden başlamadan dosya tazelenir. "
                "Ama yalnızca <i>subPath kullanılmadığında</i>. <code>subPath</code> ile mount ettiyseniz tazelenmez.",
            "<b>Env değişkenleri statik</b>: ConfigMap güncellense bile env değişmez. "
                "Genelde <code>kubectl rollout restart deploy/...</code> gerekir.",
            "<b>Immutable ConfigMap/Secret</b>: <code>immutable: true</code> ile değişmez yapılır; "
                "API server'ın watch yükünü azaltır; üretim için önerilir.",
            "<b>Secret base64 ≠ şifrelidir.</b> Etcd encryption at rest mutlaka açılmalı; KMS entegrasyonu önerilir.",
            "<b>İçerik boyutu:</b> Her ConfigMap/Secret max 1 MB. Büyük dosyalar için PVC veya init container ile indirme yapılır.",
            "<b>imagePullSecrets</b>: Private registry için Pod.spec.imagePullSecrets[].name kullanılır.",
            "<b>External Secrets</b>: Vault, AWS Secrets Manager, GCP Secret Manager gibi kaynaklarla entegrasyon için "
                "External Secrets Operator (üçüncü taraf) yaygındır.",
            "<b>Sık hata:</b> Secret'ı git'e commit etmek. Hatta <code>kubectl create secret ... --dry-run -o yaml</code> "
                "çıktısı bile base64'lü olduğu için git'e koymaktan kaçının. SealedSecrets/SOPS kullanın.",
            "<b>Sık hata:</b> ConfigMap'i sadece dosya olarak mount edip ama env'le karıştırmak. "
                "Mount edilen dosyada değişiklik var ama env'de yok — uygulama hangi kaynağı okuyor netleştirin.",
        ],
    )
    s.append(PageBreak())


# ===========================================================================
# MODÜL 6 — Volume / PV / PVC
# ===========================================================================
def module_volume(s):
    topic_section(
        s,
        title="M6. Volume, PersistentVolume ve PersistentVolumeClaim (90 dk)",
        purpose_paras=[
            "Konteyner dosya sistemi <b>geçicidir</b>; konteyner restart olunca kaybolur. "
            "Veri saklamak için Kubernetes'te <b>Volume</b> kavramı vardır. Volume Pod "
            "yaşam süresine bağlıdır (Pod silinince çoğu volume kaybolur).",
            "Pod ömrünü aşan kalıcılık için <b>PersistentVolume (PV)</b> ve "
            "<b>PersistentVolumeClaim (PVC)</b> kullanılır. PV admin tarafından "
            "ya da StorageClass üzerinden dinamik provision edilen gerçek depolama "
            "kaynağıdır; PVC kullanıcının bu kaynaktan talebidir.",
            "Pod, doğrudan PV'ye değil <i>PVC üzerinden</i> bağlanır. Bu sayede "
            "uygulama kodu altyapıdan bağımsız kalır.",
        ],
        place_paras=[
            "Volume tipleri: <code>emptyDir</code> (Pod ömrüyle), <code>hostPath</code> "
            "(Node disk; üretimde tehlikeli), <code>configMap</code> ve <code>secret</code> "
            "(daha önce işlendi), <code>persistentVolumeClaim</code> (PVC referansı), "
            "ve cloud-specific (<code>awsElasticBlockStore</code>, <code>gcePersistentDisk</code>) — "
            "günümüzde tamamı CSI sürücüleri üzerinden çalışır."
        ],
        place_diagram=dg.pv_pvc_binding(),
        commands_intro=[
            "PV/PVC ile gündelik kullanım:"
        ],
        command_rows=[
            ("kubectl get sc,pv,pvc",
                "StorageClass, PV ve PVC'leri birlikte gör."),
            ("kubectl describe pvc &lt;ad&gt;",
                "Events bölümünde provisioning hataları görünür."),
            ("kubectl get sc",
                "Mevcut StorageClass'lar; (default) işaretli olan otomatik kullanılır."),
            ("kubectl apply -f pvc.yaml",
                "PVC oluştur; storageClassName uygun ise dinamik PV açılır."),
            ("kubectl delete pvc &lt;ad&gt;",
                "PVC sil. PV'nin reclaim politikasına göre PV ya silinir ya kalır."),
            ("kubectl patch pv &lt;ad&gt; -p '{\"spec\":{\"persistentVolumeReclaimPolicy\":\"Retain\"}}'",
                "Reclaim politikasını manuel değiştir."),
            ("kubectl get pv -o wide",
                "Capacity, accessModes, claim sahibi, status."),
            ("minikube ssh -- ls /var/lib/...",
                "Minikube'de PV'nin fiziksel konumunu kontrol et."),
        ],
        flag_intro=[
            "PVC manifest'inde dikkat edilecek alanlar:"
        ],
        flag_rows=[
            ("storageClassName",   "Hangi SC ile provision edilsin; boş bırakırsa default SC kullanılır.", "standard"),
            ("accessModes",        "ReadWriteOnce | ReadOnlyMany | ReadWriteMany | ReadWriteOncePod.",     "[\"ReadWriteOnce\"]"),
            ("resources.requests.storage", "İstenen kapasite.",                                              "5Gi"),
            ("volumeMode",         "Filesystem (default) veya Block.",                                       "Filesystem"),
            ("dataSource",         "Snapshot/clone'dan başlat.",                                             "VolumeSnapshot"),
            ("reclaimPolicy",      "PV silindiğinde: Retain | Delete | Recycle (deprecated).",              "Retain"),
            ("volumeBindingMode",  "Immediate vs WaitForFirstConsumer (Pod scheduling sonrası).",           "WaitForFirstConsumer"),
        ],
        yaml_intro=[
            "Tipik PVC + Deployment mount:"
        ],
        yaml_code=(
            "apiVersion: v1\n"
            "kind: PersistentVolumeClaim\n"
            "metadata: { name: data }\n"
            "spec:\n"
            "  accessModes: [\"ReadWriteOnce\"]\n"
            "  resources:\n"
            "    requests:\n"
            "      storage: 5Gi\n"
            "  storageClassName: standard\n"
            "---\n"
            "apiVersion: apps/v1\n"
            "kind: Deployment\n"
            "metadata: { name: app }\n"
            "spec:\n"
            "  replicas: 1                  # RWX değilse 1 olmalı\n"
            "  selector: { matchLabels: { app: app } }\n"
            "  template:\n"
            "    metadata: { labels: { app: app } }\n"
            "    spec:\n"
            "      containers:\n"
            "      - name: app\n"
            "        image: myapp:1.0\n"
            "        volumeMounts:\n"
            "        - { name: data, mountPath: /data }\n"
            "      volumes:\n"
            "      - name: data\n"
            "        persistentVolumeClaim:\n"
            "          claimName: data\n"
        ),
        advanced_items=[
            "<b>accessModes</b>'lar PVC seviyesindedir ama gerçek davranış <i>storage</i>'a bağlıdır. "
                "EBS ve GCE PD RWO destekler; NFS, Azure Files RWX destekler. Yanlış seçim provisioning'i engeller.",
            "<b>ReadWriteOnce</b> bir <i>Node'a</i> bağlanır (ReadWriteOncePod 1.22+ ile bir Pod'a). "
                "Bu yüzden RWO ile replicas&gt;1 Deployment çakışır.",
            "<b>StatefulSet</b> her replika için ayrı PVC yaratır (<code>volumeClaimTemplates</code>). "
                "Veritabanları için tipik yapıdır.",
            "<b>VolumeBindingMode: WaitForFirstConsumer</b>: PVC, ilgili Pod scheduler'a düşene kadar PV bağlanmaz. "
                "Topology-aware storage için kritiktir.",
            "<b>reclaimPolicy: Retain</b> üretim verisi için güvenli default. Delete politikası, PVC silindiğinde "
                "veri kaybetmeye neden olabilir.",
            "<b>Snapshot ve clone:</b> CSI sürücüleri VolumeSnapshot ile snapshot, dataSource ile clone destekler.",
            "<b>hostPath kullanmayın</b> (debug hariç): Pod'un yeniden schedule olduğu Node değişirse veri kaybolur.",
            "<b>Sık hata:</b> PVC \"Pending\" — sebep çoğunlukla: SC yok, accessMode storage tarafından desteklenmiyor, "
                "kapasite kalmadı. <code>kubectl describe pvc</code> ile Events okuyun.",
            "<b>Sık hata:</b> <code>subPath</code> kullanıldığında ConfigMap canlı tazeleme çalışmaz.",
            "<b>İpucu — Minikube:</b> default <code>standard</code> SC vardır (hostPath provisioner). "
                "Bu yüzden çoklu Node simülasyonunda PVC'ler sınırlı davranır.",
        ],
    )
    s.append(PageBreak())


# ===========================================================================
# MODÜL 7 — Namespace, Label, Annotation
# ===========================================================================
def module_namespace(s):
    topic_section(
        s,
        title="M7. Namespace, Label, Annotation (45 dk)",
        purpose_paras=[
            "<b>Namespace</b>, aynı cluster içinde mantıksal izolasyon sağlar. "
            "Aynı isimli iki Pod aynı namespace'te olamaz, ama farklı namespace'lerde "
            "olabilir. RBAC, ResourceQuota, NetworkPolicy gibi politikalar namespace "
            "scope'una kapsanır.",
            "<b>Label</b>, key=value şeklinde nesnelere yapışan ve <i>selector</i>'lar "
            "tarafından kullanılan etiketlerdir. Service, ReplicaSet, NetworkPolicy, "
            "NodeSelector hep label seçer.",
            "<b>Annotation</b>, label gibi key=value taşır ama <b>selector ile "
            "kullanılmaz</b>. Daha çok araç/sistem meta verisi içindir: build info, "
            "deployment timestamp, ingress controller'a hint.",
        ],
        place_paras=[
            "Namespace cluster içinde bir <i>scope</i>'tur — Node'lar paylaşılır, "
            "kaynaklar paylaşılır; izolasyon mantıksaldır. <code>kube-system</code> "
            "control plane bileşenleri için; <code>default</code>, <code>kube-public</code>, "
            "<code>kube-node-lease</code> built-in'lerdir."
        ],
        place_diagram=dg.namespace_diagram(),
        commands_intro=[
            "Namespace ve label yönetiminin temel komutları:"
        ],
        command_rows=[
            ("kubectl create namespace dev",
                "Yeni namespace yaratır."),
            ("kubectl get all -n dev",
                "Belirli namespace'teki tüm temel kaynaklar."),
            ("kubectl get all -A | head",
                "Tüm namespace'lerden listeler."),
            ("kubectl config set-context --current --namespace=dev",
                "Geçerli context'in default namespace'ini değiştirir."),
            ("kubectl label pod web env=prod tier=front",
                "Bir Pod'a iki label ekler."),
            ("kubectl label pod web env-",
                "<code>env</code> label'ını siler (eksi işareti)."),
            ("kubectl get pods -l app=web,env=prod",
                "Çoklu label selector."),
            ("kubectl get pods -l 'env in (prod, staging)'",
                "Set-based selector."),
            ("kubectl annotate deploy/web owner=team-x build=abc123",
                "Annotation ekler."),
            ("kubectl get pods --show-labels",
                "Pod'ların tüm label'larını gösterir."),
        ],
        flag_intro=[
            "Label/annotation komutlarında öne çıkan flag'ler:"
        ],
        flag_rows=[
            ("--overwrite",      "Mevcut label/annotation'ı değiştirmek için zorunlu.",     "--overwrite"),
            ("-l, --selector",   "Equality (=, !=) ve set-based (in, notin, exists).",      "-l 'env in (prod)'"),
            ("--all-namespaces, -A",  "Tüm namespace'lerden.",                              "kubectl get pods -A"),
            ("-o jsonpath=...",  "Tek değer çekmek için.",                                  "{.items[0].metadata.labels.app}"),
            ("--field-selector", "metadata.name, status.phase gibi alanlara göre.",         "status.phase=Running"),
        ],
        yaml_intro=[
            "Namespace + ResourceQuota + LimitRange üçlüsü tipik bir kurulumdur:"
        ],
        yaml_code=(
            "apiVersion: v1\n"
            "kind: Namespace\n"
            "metadata:\n"
            "  name: dev\n"
            "  labels: { env: dev, team: backend }\n"
            "---\n"
            "apiVersion: v1\n"
            "kind: ResourceQuota\n"
            "metadata: { name: dev-quota, namespace: dev }\n"
            "spec:\n"
            "  hard:\n"
            "    pods: \"20\"\n"
            "    requests.cpu: \"4\"\n"
            "    requests.memory: 8Gi\n"
            "    limits.cpu: \"8\"\n"
            "    limits.memory: 16Gi\n"
            "---\n"
            "apiVersion: v1\n"
            "kind: LimitRange\n"
            "metadata: { name: dev-limits, namespace: dev }\n"
            "spec:\n"
            "  limits:\n"
            "  - type: Container\n"
            "    default:        { cpu: 200m, memory: 256Mi }\n"
            "    defaultRequest: { cpu: 50m,  memory: 64Mi  }\n"
        ),
        advanced_items=[
            "<b>Namespace silmek</b> içindeki tüm kaynakları siler — geri alınamaz. Önce <code>kubectl get all -n &lt;ns&gt;</code> ile kontrol edin.",
            "<b>Cross-namespace çağrı:</b> <code>http://web.dev.svc.cluster.local</code>. NetworkPolicy ile sınırlanabilir.",
            "<b>Label kuralları:</b> key max 63 karakter, prefix isteğe bağlı (örn. <code>app.kubernetes.io/name</code>); "
                "değer max 63 karakter, alfa-sayısal/–/_ vb.",
            "<b>Önerilen standart label'lar</b>: <code>app.kubernetes.io/name</code>, <code>/instance</code>, <code>/version</code>, <code>/component</code>, <code>/part-of</code>, <code>/managed-by</code>.",
            "<b>Annotation kullanım örnekleri:</b> "
                "<code>kubernetes.io/change-cause</code> (rollout history mesajı), "
                "<code>nginx.ingress.kubernetes.io/rewrite-target</code>.",
            "<b>ResourceQuota</b> namespace toplam kaynak limitidir; ihlal edilirse yeni Pod yaratılamaz.",
            "<b>LimitRange</b> namespace içinde default request/limit verir; resources tanımı eksik Pod'lar yine de güvenli çalışır.",
            "<b>Sık hata:</b> Default namespace'i unutmak. <code>kubens</code> (kubectx aracı) ile namespace değiştirmek pratiktir.",
            "<b>Sık hata:</b> Selector'da değişiklik yapmaya çalışmak. <code>spec.selector</code> birçok nesnede immutable'dır.",
        ],
    )
    s.append(PageBreak())


# ===========================================================================
# MODÜL 8 — Resource Yönetimi ve Probe'lar
# ===========================================================================
def module_resources_probes(s):
    topic_section(
        s,
        title="M8. Resource Yönetimi ve Probe'lar (75 dk)",
        purpose_paras=[
            "<b>resources.requests</b>: Pod'un çalışmaya başlaması için Node üzerinde "
            "ayrılması istenen CPU/RAM. Scheduler bu değere bakarak Pod'u Node'a "
            "yerleştirir. Garanti edilen alt sınırdır.",
            "<b>resources.limits</b>: Pod'un en fazla kullanabileceği değerler. CPU'da "
            "throttle, bellekte <i>OOMKilled</i>'a sebep olur. Limit yoksa bir Pod "
            "Node'un tamamını tüketebilir.",
            "<b>Probe'lar</b> uygulamanın gerçekten çalışıp çalışmadığını anlamak için "
            "vardır: <b>livenessProbe</b> (canlı mı), <b>readinessProbe</b> (trafik almaya hazır mı), "
            "<b>startupProbe</b> (uzun başlangıçlı uygulamalar için).",
        ],
        place_paras=[
            "Scheduler requests'e bakar, Pod'u uygun Node'a yerleştirir. kubelet "
            "limit'i Linux cgroup'lar üzerinden uygular. Probe'ları kubelet "
            "periyodik olarak çalıştırır; sonuçları endpoints controller'a yansır."
        ],
        place_diagram=dg.probe_lifecycle(),
        commands_intro=[
            "Resource ve probe konularıyla en sık kullanılan komutlar:"
        ],
        command_rows=[
            ("kubectl top pods [-n &lt;ns&gt;]",
                "Anlık CPU/RAM kullanımı (metrics-server gerekir)."),
            ("kubectl top nodes",
                "Node bazında kullanım."),
            ("kubectl describe pod &lt;ad&gt;",
                "Probe sonuçları, OOMKilled olayı, restart sayısı."),
            ("kubectl get events -A --sort-by=.lastTimestamp | tail",
                "Son K8s olayları (Pod restart, OOM, Pull error...)."),
            ("kubectl set resources deploy/web --requests=cpu=100m --limits=memory=256Mi",
                "Resources hızlıca ayarla."),
            ("kubectl autoscale deploy/web --min=2 --max=10 --cpu-percent=60",
                "HPA yaratır (metrics-server gerekir)."),
            ("kubectl get hpa",
                "HPA listesi ve hedef metrikler."),
        ],
        flag_intro=[
            "Probe alanlarında en sık kullanılan parametreler:"
        ],
        flag_rows=[
            ("initialDelaySeconds", "İlk probe denemesinden önce bekleme.",       "5"),
            ("periodSeconds",       "Probe'lar arası süre.",                       "10"),
            ("timeoutSeconds",      "Tek probe için zaman aşımı.",                 "1"),
            ("successThreshold",    "Ardışık kaç başarı 'healthy' sayılır (1).",   "1"),
            ("failureThreshold",    "Ardışık kaç başarısızlık restart/unready.",   "3"),
            ("httpGet.path/port",   "HTTP probe için yol ve port.",                "/healthz, 8080"),
            ("tcpSocket.port",      "TCP probe.",                                  "5432"),
            ("exec.command",        "Komut çalıştırarak probe.",                   "[\"cat\", \"/tmp/healthy\"]"),
        ],
        yaml_intro=[
            "Resources + 3 probe entegrasyonlu bir konteyner:"
        ],
        yaml_code=(
            "containers:\n"
            "- name: web\n"
            "  image: web:1.0\n"
            "  ports: [{ name: http, containerPort: 8080 }]\n"
            "  resources:\n"
            "    requests: { cpu: 100m, memory: 128Mi }\n"
            "    limits:   { cpu: 500m, memory: 256Mi }\n"
            "  startupProbe:\n"
            "    httpGet: { path: /healthz/startup, port: http }\n"
            "    failureThreshold: 30   # ≈60 sn (30 * 2 sn)\n"
            "    periodSeconds: 2\n"
            "  livenessProbe:\n"
            "    httpGet: { path: /healthz/live, port: http }\n"
            "    periodSeconds: 10\n"
            "    failureThreshold: 3\n"
            "  readinessProbe:\n"
            "    httpGet: { path: /healthz/ready, port: http }\n"
            "    periodSeconds: 5\n"
            "    failureThreshold: 2\n"
            "  lifecycle:\n"
            "    preStop:\n"
            "      exec: { command: [\"sh\", \"-c\", \"sleep 5\"] }\n"
        ),
        advanced_items=[
            "<b>QoS sınıfları:</b> Guaranteed (requests==limits), Burstable (limits&gt;requests), "
                "BestEffort (hiçbiri). Node baskıda BestEffort önce öldürülür.",
            "<b>CPU birimi:</b> 1 = 1 çekirdek; 500m = 0.5 çekirdek. Bellek: Mi/Gi gibi binary.",
            "<b>CPU limit throttle yapar, restart yapmaz.</b> Bellek limit ise OOMKilled → restart.",
            "<b>Liveness probe agresif olursa</b> sürekli restart döngüsü oluşur. Önce readiness ile sınırlandırın; "
                "liveness yalnızca \"deadlock\" gibi gerçek hata durumları için.",
            "<b>readinessProbe yoksa</b> Service Pod'u hemen endpoint listesine ekler — uygulama henüz hazır değilken trafik alır.",
            "<b>startupProbe</b> yavaş başlayan uygulamalar (Java, .NET) için zorunludur; "
                "liveness/readiness'in agresif failureThreshold'una takılmasını engeller.",
            "<b>HPA için metrics-server şart</b>: <code>kubectl top</code> çalışmıyorsa HPA da çalışmaz.",
            "<b>HPA + sabit replicas çakışır</b>: HPA bağlı Deployment'tan <code>spec.replicas</code> alanını kaldırın.",
            "<b>VPA (Vertical Pod Autoscaler)</b>: requests'i öğrenip otomatik ayarlar; üçüncü taraf, bilinmesi iyi.",
            "<b>Sık hata:</b> <code>resources</code> tanımı eksik Pod scheduler için en alt önceliklidir, "
                "Node baskıda ilk öldürülen olur. Her zaman requests koyun.",
            "<b>Sık hata:</b> HTTP probe Pod hazır değilken bile 200 dönen <code>/</code> path'i kullanmak. "
                "Ayrı bir <code>/healthz/ready</code> uç noktası şart.",
        ],
    )
    s.append(PageBreak())


# ===========================================================================
# MODÜL 9 — Ingress
# ===========================================================================
def module_ingress(s):
    topic_section(
        s,
        title="M9. Ingress (60 dk)",
        purpose_paras=[
            "<b>Ingress</b>, cluster dışından HTTP/HTTPS trafiğini içerideki Service'lere "
            "yönlendiren <b>L7 (uygulama katmanı)</b> kuralıdır. Path-based ve host-based "
            "routing, TLS terminasyonu, rewrite gibi özellikleri tek bir public IP üzerinden "
            "sağlar.",
            "Ingress kuralları <b>Ingress Controller</b> tarafından gerçek bir proxy "
            "(NGINX, Traefik, HAProxy, AWS ALB) üzerinde uygulanır. Cluster'da bir "
            "Ingress Controller yoksa Ingress nesnesi yaratmak hiçbir şey yapmaz.",
            "Minikube'de <code>minikube addons enable ingress</code> komutu NGINX Ingress "
            "Controller'ı devreye alır.",
        ],
        place_paras=[
            "İstek akışı: Public DNS → Cloud LB → Ingress Controller Pod'u → Ingress kuralları "
            "ile eşleşen Service → Endpoints → Pod. Ingress Controller'ın kendisi de bir Pod'dur."
        ],
        place_diagram=dg.ingress_topology(),
        commands_intro=[
            "Ingress için temel komutlar:"
        ],
        command_rows=[
            ("kubectl get ingress -A",
                "Tüm Ingress kurallarını gör."),
            ("kubectl describe ing &lt;ad&gt;",
                "Backend Service'leri, ilişkili IP'yi, annotation'ları gösterir."),
            ("kubectl get ingressclass",
                "Cluster'da kayıtlı Ingress Controller'lar."),
            ("kubectl create ingress web --rule=\"playground.local/*=playground:80\"",
                "Tek satırla Ingress (1.19+; çoğunlukla YAML tercih edilir)."),
            ("kubectl annotate ingress web nginx.ingress.kubernetes.io/rewrite-target=/",
                "Annotation ekle (controller-spesifik davranış)."),
        ],
        flag_intro=[
            "Ingress spec'inde sık kullanılan alanlar:"
        ],
        flag_rows=[
            ("ingressClassName",   "Hangi controller işleyecek.",                    "nginx"),
            ("rules.host",         "DNS adı; Host header eşleşmesi.",                "api.example.com"),
            ("paths.path / pathType", "Path ve eşleşme tipi: Exact | Prefix | ImplementationSpecific.", "/api, Prefix"),
            ("backend.service",    "Trafik hangi Service'e gidecek.",                "name: api, port: number 80"),
            ("tls.hosts / secretName", "TLS sertifikası için.",                      "[api.example.com], api-tls"),
            ("annotations",        "Controller'a özel ayarlar; standart değildir.",   "nginx.ingress.kubernetes.io/..."),
        ],
        yaml_intro=[
            "Path-based + TLS örneği:"
        ],
        yaml_code=(
            "apiVersion: networking.k8s.io/v1\n"
            "kind: Ingress\n"
            "metadata:\n"
            "  name: web\n"
            "  annotations:\n"
            "    nginx.ingress.kubernetes.io/rewrite-target: /\n"
            "spec:\n"
            "  ingressClassName: nginx\n"
            "  tls:\n"
            "  - hosts: [\"web.example.com\"]\n"
            "    secretName: web-tls\n"
            "  rules:\n"
            "  - host: web.example.com\n"
            "    http:\n"
            "      paths:\n"
            "      - path: /api\n"
            "        pathType: Prefix\n"
            "        backend:\n"
            "          service: { name: api, port: { number: 80 } }\n"
            "      - path: /\n"
            "        pathType: Prefix\n"
            "        backend:\n"
            "          service: { name: web, port: { number: 80 } }\n"
        ),
        advanced_items=[
            "<b>pathType</b>: <code>Exact</code> birebir eşleşme; <code>Prefix</code> dizin sınırına göre prefix; "
                "<code>ImplementationSpecific</code> controller'a bırakır.",
            "<b>TLS</b>: <code>kubernetes.io/tls</code> türünde Secret gerekir (cert + key). "
                "Cert-manager + Let's Encrypt üretimde standarttır.",
            "<b>Annotation'lar controller-spesifik</b>: NGINX'in <code>nginx.ingress.kubernetes.io/...</code> "
                "annotation'ları Traefik'te çalışmaz.",
            "<b>Ingress vs Gateway API</b>: Gateway API (1.27+ GA) Ingress'in yerini almaya hazırlanan yeni modeldir; "
                "daha esnek ve role-based.",
            "<b>defaultBackend</b>: eşleşmeyen istekler için fallback Service.",
            "<b>External-DNS</b>: Ingress'lerin host'larını otomatik olarak Route53/Cloud DNS'e yazan operator.",
            "<b>Sık hata:</b> Ingress Controller yok ama Ingress nesnesi yaratıldı — \"hiçbir şey çalışmıyor\".",
            "<b>Sık hata:</b> Local'de <code>/etc/hosts</code>'a host eklemeyi unutmak.",
            "<b>İpucu — debug:</b> <code>kubectl -n ingress-nginx logs deploy/ingress-nginx-controller</code>; "
                "404 ve backend hataları orada görünür.",
        ],
    )
    s.append(PageBreak())


# ===========================================================================
# MODÜL 10 — Kapanış Projesi
# ===========================================================================
def module_capstone(s):
    s.append(Paragraph("M10. Kapanış Projesi ve Sorun Giderme (90 dk)", h1))
    s.append(P(
        "Kursta öğrenilen tüm yapılar bu projede bir araya getirilir. Eğitmen, "
        "manifest'lere kasıtlı hatalar enjekte eder; kursiyerler "
        "<code>logs</code>, <code>describe</code>, <code>events</code> ile sorunu bulur."))

    s.append(Paragraph("Senaryo", h2))
    s.append(bullets([
        "Bir web uygulaması (örn. nginx veya bir .NET MVC uygulaması) Deployment ile çalışır, replikası 3'tür.",
        "Yapılandırma ConfigMap'ten, parola Secret'tan gelir.",
        "Veri kalıcılığı PVC ile sağlanır.",
        "Service (ClusterIP) Pod'ları açığa çıkarır; Ingress public erişim sağlar.",
        "HPA, CPU kullanımı %60'ı geçince replikayı en fazla 6'ya kadar arttırır.",
        "Probe'lar (startup + liveness + readiness) doğru yapılandırılmıştır.",
    ]))

    s.append(Paragraph("Eğitmen Enjekte Edebileceği Hatalar (Troubleshooting)", h2))
    s.append(cmd_table([
        ("Yanlış image tag",
            "Pod ImagePullBackOff'a düşer. Tanı: <code>kubectl describe pod</code> Events bölümü."),
        ("Selector mismatch",
            "Service endpoint listesi boş kalır. Tanı: <code>kubectl get endpoints &lt;svc&gt;</code>."),
        ("readinessProbe yanlış path",
            "Pod sürekli not ready. Tanı: <code>kubectl describe pod</code>, probe sonuçları."),
        ("Bellek limit'i çok düşük",
            "OOMKilled. Tanı: <code>kubectl describe pod</code> Last State: Terminated, Reason: OOMKilled."),
        ("ConfigMap'in adı yanlış",
            "Pod CreateContainerConfigError. Tanı: describe pod."),
        ("Secret eksik",
            "Pod CreateContainerConfigError. <code>kubectl get secret</code>."),
        ("PVC accessMode uyumsuz",
            "PVC Pending. Tanı: <code>kubectl describe pvc</code>."),
        ("Yanlış ingressClassName",
            "Ingress controller işlemez; 404. Tanı: <code>kubectl describe ing</code>."),
    ]))

    s.append(Paragraph("Lab Akışı", h2))
    s.append(bullets([
        "<b>0–15 dk:</b> Manifest'leri grup halinde gözden geçir; her nesnenin görevini söyle.",
        "<b>15–60 dk:</b> Eğitmen 3 hata enjekte eder; gruplar hatayı bulup düzeltir.",
        "<b>60–80 dk:</b> Rolling update + rollback + HPA tetikleme demosu.",
        "<b>80–90 dk:</b> Sınıfta kısa Q&A; cluster temizliği (<code>kubectl delete ns playground</code>).",
    ]))
    s.append(PageBreak())


# ===========================================================================
# APPENDIX — Cheatsheet + Troubleshooting Decision Tree
# ===========================================================================
def appendix(s):
    s.append(Paragraph("Ek A — Komut Hızlı Referans (Cheatsheet)", h1))
    s.append(cmd_table([
        ("kubectl explain &lt;kind&gt;.spec --recursive",
            "Tüm alanların açıklamasını öğren."),
        ("kubectl get &lt;kind&gt; -o yaml",
            "Mevcut nesneyi YAML olarak gör (sürüm/anotasyon dahil)."),
        ("kubectl apply -f file.yaml --dry-run=server",
            "Sunucuda doğrula, uygulama."),
        ("kubectl diff -f file.yaml",
            "Mevcut state ile manifest farkı."),
        ("kubectl auth can-i &lt;verb&gt; &lt;kind&gt;",
            "RBAC izin kontrolü."),
        ("kubectl get all -n &lt;ns&gt; -o name",
            "Sadece isimleri al; script için."),
        ("kubectl logs -l app=web --all-containers --since=1h",
            "Bir Service arkasındaki tüm Pod'ların loglarını birlikte oku."),
        ("kubectl logs &lt;pod&gt; --previous -c &lt;container&gt;",
            "Crash olan bir önceki konteyner instance'ının son loglarını oku — CrashLoopBackOff teşhisinde ilk komut."),
        ("kubectl wait --for=condition=Ready pod -l app=web --timeout=2m",
            "Hazır olana dek bekle (CI/CD için)."),
        ("kubectl run debug --rm -it --image=nicolaka/netshoot -- sh",
            "Tüm network tool'larıyla geçici debug Pod'u."),
        ("kubectl get events --sort-by=.lastTimestamp | tail -20",
            "Son olayları kronolojik gör."),
    ]))

    s.append(Paragraph("Ek B — Sorun Giderme Karar Ağacı", h1))
    s.append(P("<b>Pod hâlâ Pending ise:</b>"))
    s.append(bullets([
        "<code>kubectl describe pod</code> → Events: <b>FailedScheduling</b>? Sebep: yetersiz CPU/RAM, taints, PVC bekliyor.",
        "<code>kubectl get nodes -o wide</code> → kapasite ve durum.",
        "PVC pending mi? <code>kubectl describe pvc</code> → StorageClass yok ya da hatalı.",
    ]))
    s.append(P("<b>Pod CrashLoopBackOff ise:</b>"))
    s.append(bullets([
        "<code>kubectl logs &lt;pod&gt; --previous</code> → bir önceki konteynerin son log'u.",
        "<code>kubectl describe pod</code> → Last State: Terminated; ExitCode kritik (137=OOM, 1=app hatası).",
        "<code>command</code>/<code>args</code> yanlış mı? imagePullPolicy?",
    ]))
    s.append(P("<b>Service çalışmıyor ise:</b>"))
    s.append(bullets([
        "<code>kubectl get endpoints &lt;svc&gt;</code> → boşsa selector/label uyumsuz.",
        "Pod ready mi? <code>kubectl get pods -l ...</code> READY sütunu.",
        "<code>kubectl run probe --rm -it --image=busybox -- wget -qO- svc-name</code> → DNS çözülüyor mu?",
    ]))
    s.append(P("<b>Image çekilemiyor:</b>"))
    s.append(bullets([
        "<code>kubectl describe pod</code> → ErrImagePull / ImagePullBackOff.",
        "Tag doğru mu? Registry public mi? imagePullSecrets gerekli mi?",
        "Minikube'de <code>minikube image load</code> ile lokal image'ı yükleyin.",
    ]))

    s.append(Paragraph("Ek C — Kurs Sonrası Yol Haritası", h1))
    s.append(bullets([
        "<b>Helm</b> ile paket yönetimi; <b>Kustomize</b> ile manifest katmanlama.",
        "<b>HPA + VPA + Cluster Autoscaler</b> üçlüsü.",
        "<b>NetworkPolicy</b> ve service mesh (Istio/Linkerd).",
        "<b>StatefulSet</b>, <b>Job</b>, <b>CronJob</b>, <b>DaemonSet</b>.",
        "<b>RBAC, ServiceAccount, OIDC</b> ile yetkilendirme.",
        "<b>Operator pattern</b> ve Custom Resource Definition (CRD).",
        "<b>GitOps</b>: ArgoCD / Flux ile manifest senkronizasyonu.",
        "<b>Sertifikasyon</b>: CKAD (geliştiriciler), CKA (operatörler), CKS (güvenlik).",
    ]))


# ---------------------------------------------------------------------------
def main():
    out = os.path.join(OUT, "kubernetes-giris-kursu-detayli-mufredat.pdf")
    doc = SimpleDocTemplate(
        out, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
        title="Kubernetes Giriş Kursu — Detaylı Eğitmen Dokümantasyonu",
        author="Eğitim Birimi",
    )

    s = []
    cover(s)
    timeline_section(s)
    module_architecture(s)
    module_pod(s)
    module_deployment(s)
    module_service(s)
    module_configmap_secret(s)
    module_volume(s)
    module_namespace(s)
    module_resources_probes(s)
    module_ingress(s)
    module_capstone(s)
    appendix(s)

    doc.build(s)
    print("OK", out)
    return out


if __name__ == "__main__":
    main()
