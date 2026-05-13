"""
Kubernetes detaylı dokümanı için reportlab.graphics ile çizilen diyagramlar.
"animasyon" hissi için çoklu-kare diyagramlar kullanılır.
"""

from reportlab.graphics.shapes import (
    Drawing, Rect, Circle, Line, String, Polygon, Group, PolyLine
)
from reportlab.lib import colors

# ---- Renkler ----
PRIMARY  = colors.HexColor("#0b3d91")
ACCENT   = colors.HexColor("#f59e0b")
SUCCESS  = colors.HexColor("#16a34a")
DANGER   = colors.HexColor("#dc2626")
NEUTRAL  = colors.HexColor("#475569")
LIGHT    = colors.HexColor("#e0e7ff")
BG       = colors.HexColor("#f8fafc")
INK      = colors.HexColor("#0f172a")
MUTED    = colors.HexColor("#94a3b8")

FONT      = "DejaVu"
FONT_BOLD = "DejaVu-Bold"
FONT_MONO = "DejaVuMono"


def _box(x, y, w, h, label, fill=LIGHT, stroke=PRIMARY, sub=None, fontsize=9, bold=True):
    """Etiketli yuvarlatılmış kutu. label = ana metin; sub = alt etiket."""
    g = Group()
    g.add(Rect(x, y, w, h, rx=4, ry=4,
               fillColor=fill, strokeColor=stroke, strokeWidth=0.8))
    g.add(String(x + w / 2, y + h / 2 + (3 if sub else -3),
                 label, fontName=FONT_BOLD if bold else FONT,
                 fontSize=fontsize, textAnchor="middle", fillColor=INK))
    if sub:
        g.add(String(x + w / 2, y + h / 2 - 7,
                     sub, fontName=FONT, fontSize=fontsize - 2,
                     textAnchor="middle", fillColor=NEUTRAL))
    return g


def _arrow(x1, y1, x2, y2, color=NEUTRAL, label=None, dashed=False):
    """x1,y1 -> x2,y2 ok. İsteğe bağlı etiket."""
    g = Group()
    line = Line(x1, y1, x2, y2, strokeColor=color, strokeWidth=1.2)
    if dashed:
        line.strokeDashArray = (3, 2)
    g.add(line)
    # Ok başı
    import math
    ang = math.atan2(y2 - y1, x2 - x1)
    head = 5
    g.add(Polygon([
        x2, y2,
        x2 - head * math.cos(ang - math.pi / 7),
        y2 - head * math.sin(ang - math.pi / 7),
        x2 - head * math.cos(ang + math.pi / 7),
        y2 - head * math.sin(ang + math.pi / 7),
    ], fillColor=color, strokeColor=color))
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        g.add(String(mx, my + 4, label, fontName=FONT, fontSize=7,
                     textAnchor="middle", fillColor=color))
    return g


def _title(d, text, y=None):
    if y is None:
        y = d.height - 14
    d.add(String(d.width / 2, y, text, fontName=FONT_BOLD,
                 fontSize=11, textAnchor="middle", fillColor=PRIMARY))


def _caption(d, text, y=4):
    d.add(String(d.width / 2, y, text, fontName=FONT, fontSize=7.5,
                 textAnchor="middle", fillColor=NEUTRAL))


# ===========================================================================
# 1) KUBERNETES MİMARİSİ — Control Plane + Worker Node'lar
# ===========================================================================
def architecture_diagram():
    d = Drawing(500, 340)
    _title(d, "Kubernetes Mimarisi — Genel Görünüm")

    # Control plane çerçevesi
    d.add(Rect(10, 60, 200, 250, rx=8, ry=8,
               fillColor=colors.HexColor("#eef2ff"),
               strokeColor=PRIMARY, strokeWidth=1.2))
    d.add(String(110, 295, "Control Plane (Master)",
                 fontName=FONT_BOLD, fontSize=10,
                 textAnchor="middle", fillColor=PRIMARY))

    # Bileşenler
    d.add(_box(25, 250, 170, 28, "kube-apiserver",
               sub="RESTful API; tüm trafiğin kalbi", fill=colors.white))
    d.add(_box(25, 210, 170, 28, "etcd",
               sub="key-value store, cluster state", fill=colors.white))
    d.add(_box(25, 170, 170, 28, "kube-scheduler",
               sub="Pod'u uygun Node'a yerleştirir", fill=colors.white))
    d.add(_box(25, 130, 170, 28, "kube-controller-manager",
               sub="ReplicaSet, Node, Endpoints controller'ları", fill=colors.white))
    d.add(_box(25, 90, 170, 28, "cloud-controller-manager",
               sub="(bulutta) LoadBalancer, Route, Node", fill=colors.white))

    # Worker node çerçevesi
    for i, x in enumerate([240, 360]):
        d.add(Rect(x, 60, 110, 250, rx=8, ry=8,
                   fillColor=colors.HexColor("#fff7ed"),
                   strokeColor=ACCENT, strokeWidth=1.0))
        d.add(String(x + 55, 295, f"Worker Node {i + 1}",
                     fontName=FONT_BOLD, fontSize=10,
                     textAnchor="middle", fillColor=ACCENT))

        d.add(_box(x + 5, 255, 100, 26, "kubelet",
                   sub="Pod yaşamcısı", fill=colors.white, fontsize=8))
        d.add(_box(x + 5, 220, 100, 26, "kube-proxy",
                   sub="iptables/IPVS", fill=colors.white, fontsize=8))
        d.add(_box(x + 5, 185, 100, 26, "containerd",
                   sub="container runtime", fill=colors.white, fontsize=8))
        # Pod'lar
        d.add(_box(x + 10, 130, 40, 35, "Pod",
                   sub="app A", fill=LIGHT, fontsize=8))
        d.add(_box(x + 60, 130, 40, 35, "Pod",
                   sub="app B", fill=LIGHT, fontsize=8))
        d.add(_box(x + 10, 80, 40, 35, "Pod",
                   sub="app C", fill=LIGHT, fontsize=8))

    # Oklar: API <-> kubelet
    d.add(_arrow(210, 264, 240, 268, label="watch", color=PRIMARY))
    d.add(_arrow(210, 264, 360, 268, color=PRIMARY))
    # Scheduler -> API
    d.add(_arrow(195, 184, 195, 200, dashed=True, color=NEUTRAL))
    # Controller -> API
    d.add(_arrow(195, 144, 195, 160, dashed=True, color=NEUTRAL))
    # etcd <-> API
    d.add(_arrow(110, 240, 110, 250, color=SUCCESS))
    d.add(_arrow(110, 250, 110, 240, color=SUCCESS))

    _caption(d, "Tüm bileşenler etcd'ye yalnızca kube-apiserver üzerinden erişir.")
    return d


# ===========================================================================
# 2) POD YAŞAM DÖNGÜSÜ — Pending → Running → Terminating
# ===========================================================================
def pod_lifecycle_diagram():
    d = Drawing(500, 200)
    _title(d, "Pod Yaşam Döngüsü (4 evre)")

    phases = [
        ("Pending", "scheduled olmamış",        MUTED),
        ("ContainerCreating", "image pull, mount", ACCENT),
        ("Running", "konteynerler çalışıyor",   SUCCESS),
        ("Terminating", "SIGTERM + grace period", DANGER),
    ]
    x = 15
    for name, sub, color in phases:
        d.add(_box(x, 90, 105, 60, name, sub=sub,
                   fill=colors.white, stroke=color, fontsize=10))
        x += 120
    # Oklar
    for i in range(3):
        sx = 15 + 105 + i * 120
        d.add(_arrow(sx, 120, sx + 15, 120, color=NEUTRAL))

    _caption(d, "kubectl get pod STATUS sütunu burada görünür. Failed/Succeeded terminal durumlardır.")
    return d


# ===========================================================================
# 3) POD ANATOMİSİ — Shared net ns, volumes, sidecar
# ===========================================================================
def pod_anatomy_diagram():
    d = Drawing(500, 290)
    _title(d, "Pod Anatomisi — Paylaşılan Ağ ve Volume")

    # Pod dış çerçevesi — sayfa ortasında, açıklama yazıları altta
    d.add(Rect(60, 100, 380, 155, rx=10, ry=10,
               fillColor=colors.HexColor("#ecfdf5"),
               strokeColor=SUCCESS, strokeWidth=1.4))
    d.add(String(250, 238, "Pod (10.244.1.5)",
                 fontName=FONT_BOLD, fontSize=10,
                 textAnchor="middle", fillColor=SUCCESS))

    # Konteynerler
    d.add(_box(80, 160, 150, 60, "main",
               sub="image: app:1.0", fill=colors.white, fontsize=9))
    d.add(_box(270, 160, 150, 60, "sidecar (log-shipper)",
               sub="image: fluent-bit", fill=colors.white, fontsize=9))

    # Volume (paylaşılan)
    d.add(_box(165, 115, 170, 28, "shared-volume (emptyDir)",
               fill=LIGHT, stroke=PRIMARY, fontsize=8))

    # localhost paylaşımı
    d.add(Line(230, 190, 270, 190, strokeColor=NEUTRAL, strokeWidth=1,
               strokeDashArray=(2, 2)))
    d.add(String(250, 195, "localhost", fontName=FONT, fontSize=7,
                 textAnchor="middle", fillColor=NEUTRAL))

    # Açıklamalar — Pod kutusunun ALTINA, iki kolon
    d.add(String(60, 80, "Aynı Pod'daki konteynerler:",
                 fontName=FONT_BOLD, fontSize=9, fillColor=INK))
    d.add(String(75, 64, "• Aynı IP'yi paylaşır",
                 fontName=FONT, fontSize=8.5, fillColor=INK))
    d.add(String(75, 50, "• localhost ile birbirini görür",
                 fontName=FONT, fontSize=8.5, fillColor=INK))
    d.add(String(265, 64, "• Volume'leri paylaşır",
                 fontName=FONT, fontSize=8.5, fillColor=INK))
    d.add(String(265, 50, "• Birlikte yaratılır, birlikte ölür",
                 fontName=FONT, fontSize=8.5, fillColor=INK))

    _caption(d, "Bu sebeple Pod, dağıtımın en küçük birimi sayılır — konteyner değil.",
             y=20)
    return d


# ===========================================================================
# 4) REPLICASET SELF-HEALING (3 kare)
# ===========================================================================
def replicaset_self_healing():
    d = Drawing(500, 220)
    _title(d, "ReplicaSet — Self-Healing (3 kare)")

    frames = [
        ("1. desired=3, mevcut=3", [(SUCCESS, "Pod A"), (SUCCESS, "Pod B"), (SUCCESS, "Pod C")], None),
        ("2. Pod B düşer",        [(SUCCESS, "Pod A"), (DANGER, "Pod B"),  (SUCCESS, "Pod C")], "✗"),
        ("3. RS yeni Pod yaratır", [(SUCCESS, "Pod A"), (ACCENT, "Pod D (yeni)"), (SUCCESS, "Pod C")], None),
    ]
    for i, (title, pods, mark) in enumerate(frames):
        fx = 15 + i * 165
        d.add(Rect(fx, 40, 155, 140, rx=6, ry=6,
                   fillColor=BG, strokeColor=MUTED, strokeWidth=0.8))
        d.add(String(fx + 77, 165, title, fontName=FONT_BOLD,
                     fontSize=9, textAnchor="middle", fillColor=PRIMARY))
        for j, (color, name) in enumerate(pods):
            py = 130 - j * 32
            d.add(_box(fx + 20, py, 115, 24, name, fill=colors.white,
                       stroke=color, fontsize=8))
            if mark and j == 1:
                d.add(String(fx + 135, py + 12, mark, fontName=FONT_BOLD,
                             fontSize=14, fillColor=DANGER))
        if i < 2:
            d.add(_arrow(fx + 156, 110, fx + 165, 110, color=NEUTRAL))

    _caption(d, "ReplicaSet sürekli olarak istenen replika sayısını kontrol eder ve farkı kapatır.")
    return d


# ===========================================================================
# 5) DEPLOYMENT — ROLLING UPDATE (4 kare)
# ===========================================================================
def rolling_update_diagram():
    d = Drawing(500, 260)
    _title(d, "Deployment — Rolling Update Akışı (maxSurge=1, maxUnavailable=0)")

    frames = [
        ("Başlangıç", ["v1", "v1", "v1"], None),
        ("1) Yeni RS, +1 v2", ["v1", "v1", "v1", "v2"], 3),
        ("2) Hazır → eski -1", ["v1", "v1", "v2", "v2"], None),
        ("3) Tamamlandı", ["v2", "v2", "v2"], None),
    ]
    for i, (title, ver, hl) in enumerate(frames):
        fx = 12 + i * 125
        d.add(Rect(fx, 50, 115, 175, rx=6, ry=6,
                   fillColor=BG, strokeColor=MUTED, strokeWidth=0.8))
        d.add(String(fx + 57, 210, title, fontName=FONT_BOLD,
                     fontSize=8.5, textAnchor="middle", fillColor=PRIMARY))
        for j, v in enumerate(ver):
            py = 180 - j * 36
            color = ACCENT if v == "v2" else NEUTRAL
            fill = colors.HexColor("#fef3c7") if v == "v2" else colors.white
            d.add(_box(fx + 15, py, 85, 28, f"Pod {v}", fill=fill,
                       stroke=color, fontsize=8))
            if hl is not None and j == hl:
                d.add(String(fx + 105, py + 14, "★", fontName=FONT_BOLD,
                             fontSize=10, fillColor=ACCENT))
        if i < 3:
            d.add(_arrow(fx + 116, 130, fx + 125, 130, color=NEUTRAL))

    _caption(d, "★ = bu adımda eklenen Pod. Trafik kesintisiz kalır çünkü maxUnavailable=0.")
    return d


# ===========================================================================
# 6) SERVICE — Selector → Endpoints → Pod'lar
# ===========================================================================
def service_selector_diagram():
    d = Drawing(500, 250)
    _title(d, "Service — Selector → Endpoints → Pod'lar")

    # Service
    d.add(_box(190, 175, 120, 40, "Service: web",
               sub="selector: app=web", fill=LIGHT, fontsize=10))
    d.add(String(250, 165, "ClusterIP 10.96.0.42", fontName=FONT_MONO,
                 fontSize=7, textAnchor="middle", fillColor=NEUTRAL))

    # EndpointSlice
    d.add(_box(160, 110, 180, 32, "EndpointSlice",
               sub="kubelet ↔ controller tarafından doldurulur",
               fill=colors.white, stroke=ACCENT, fontsize=9))

    # Pod'lar
    pods = [
        (50,  35, "Pod-1", "app=web",  SUCCESS),
        (150, 35, "Pod-2", "app=web",  SUCCESS),
        (250, 35, "Pod-3", "app=web",  SUCCESS),
        (370, 35, "Pod-X", "app=cache", DANGER),
    ]
    for x, y, name, lbl, c in pods:
        d.add(_box(x, y, 90, 50, name, sub=lbl,
                   fill=colors.white, stroke=c, fontsize=9))

    # Oklar
    d.add(_arrow(250, 175, 250, 145, color=PRIMARY))
    for x in [95, 195, 295]:
        d.add(_arrow(250, 110, x, 88, color=SUCCESS))
    d.add(Line(250, 110, 415, 88, strokeColor=DANGER,
               strokeWidth=1, strokeDashArray=(3, 2)))
    d.add(String(380, 105, "X eşleşme yok",
                 fontName=FONT, fontSize=7, fillColor=DANGER))

    _caption(d, "Service, Pod IP'lerini değil; selector'la eşleşen Pod'ları endpoints listesinde takip eder.")
    return d


# ===========================================================================
# 7) SERVICE TÜRLERİ — ClusterIP / NodePort / LoadBalancer
# ===========================================================================
def service_types_diagram():
    d = Drawing(500, 240)
    _title(d, "Service Türleri — Erişim Yolu Karşılaştırması")

    cols = [
        ("ClusterIP",     "yalnız cluster içi",      PRIMARY,  colors.HexColor("#eef2ff")),
        ("NodePort",      "her Node üstünde port",   ACCENT,   colors.HexColor("#fff7ed")),
        ("LoadBalancer",  "harici cloud LB",         SUCCESS,  colors.HexColor("#ecfdf5")),
    ]
    for i, (name, sub, color, fill) in enumerate(cols):
        x = 15 + i * 160
        d.add(Rect(x, 30, 150, 185, rx=8, ry=8,
                   fillColor=fill, strokeColor=color, strokeWidth=1))
        d.add(String(x + 75, 195, name, fontName=FONT_BOLD,
                     fontSize=10, textAnchor="middle", fillColor=color))
        d.add(String(x + 75, 183, sub, fontName=FONT,
                     fontSize=7.5, textAnchor="middle", fillColor=NEUTRAL))
        # Erişim katmanları
        layers = [
            ("Client", 150),
            ("Cluster İçi" if name == "ClusterIP" else
                ("Node:30080" if name == "NodePort" else "Cloud LB"), 120),
            ("Service", 85),
            ("Pod", 50),
        ]
        prev_y = None
        for label, y in layers:
            d.add(_box(x + 25, y, 100, 22, label, fill=colors.white,
                       stroke=color, fontsize=8))
            if prev_y is not None:
                d.add(_arrow(x + 75, prev_y, x + 75, y + 22, color=color))
            prev_y = y

    _caption(d, "LoadBalancer içerir NodePort'u; NodePort içerir ClusterIP'yi.")
    return d


# ===========================================================================
# 8) CONFIGMAP & SECRET — Pod'a aktarım yolları
# ===========================================================================
def configmap_secret_flow():
    d = Drawing(500, 240)
    _title(d, "ConfigMap & Secret → Pod'a Aktarım Yolları")

    # Kaynaklar
    d.add(_box(20, 150, 130, 50, "ConfigMap",
               sub="key/value, plain text",
               fill=colors.HexColor("#ecfdf5"), stroke=SUCCESS, fontsize=10))
    d.add(_box(20, 60, 130, 50, "Secret",
               sub="key/value, base64",
               fill=colors.HexColor("#fef3c7"), stroke=ACCENT, fontsize=10))

    # Pod
    d.add(Rect(310, 40, 170, 180, rx=10, ry=10,
               fillColor=colors.HexColor("#eef2ff"),
               strokeColor=PRIMARY, strokeWidth=1.2))
    d.add(String(395, 205, "Pod (container)", fontName=FONT_BOLD,
                 fontSize=10, textAnchor="middle", fillColor=PRIMARY))
    d.add(_box(325, 155, 140, 30, "env: VAR=VALUE",
               fill=colors.white, fontsize=9))
    d.add(_box(325, 110, 140, 30, "envFrom: configMapRef",
               fill=colors.white, fontsize=9))
    d.add(_box(325, 65, 140, 30, "volumeMount: /etc/...",
               fill=colors.white, fontsize=9))

    # Oklar (CM ve Secret'tan 3 yola)
    for sy, src in [(175, "CM"), (85, "Secret")]:
        for ty in [170, 125, 80]:
            color = SUCCESS if src == "CM" else ACCENT
            d.add(_arrow(150, sy, 310, ty, color=color))

    _caption(d, "Volume mount kullanıldığında ConfigMap/Secret güncellemeleri Pod yeniden başlatılmadan tazelenir (≈30–60 sn).")
    return d


# ===========================================================================
# 9) PV / PVC / StorageClass binding
# ===========================================================================
def pv_pvc_binding():
    d = Drawing(500, 250)
    _title(d, "PVC → StorageClass → PV → Pod (Dinamik Provisioning)")

    d.add(_box(15, 110, 110, 60, "Kullanıcı / Pod",
               sub="PVC ister", fill=LIGHT, fontsize=9))
    d.add(_box(150, 165, 130, 50, "StorageClass",
               sub="provisioner: ebs-csi",
               fill=colors.HexColor("#fff7ed"), stroke=ACCENT, fontsize=9))
    d.add(_box(150, 55, 130, 50, "PV (dinamik)",
               sub="bağlanır PVC'ye",
               fill=colors.HexColor("#ecfdf5"), stroke=SUCCESS, fontsize=9))
    d.add(_box(310, 110, 170, 60, "Pod (volumeMount)",
               sub="/data", fill=LIGHT, fontsize=9))

    d.add(_arrow(125, 145, 150, 175, label="1) PVC", color=PRIMARY))
    d.add(_arrow(215, 165, 215, 110, label="2) PV yaratır", color=ACCENT, dashed=True))
    d.add(_arrow(280, 80,  310, 130, label="3) bağlanır", color=SUCCESS))
    d.add(_arrow(125, 145, 310, 145, label="4) Pod mount eder", color=PRIMARY))

    _caption(d, "PVC sadece istektir. Manuel PV de yapılabilir ama prodüksiyonda StorageClass ile dinamik daha yaygındır.")
    return d


# ===========================================================================
# 10) PROBE LIFECYCLE
# ===========================================================================
def probe_lifecycle():
    d = Drawing(500, 240)
    _title(d, "Probe Yaşam Döngüsü — Startup, Liveness, Readiness")

    # Zaman ekseni
    d.add(Line(40, 80, 460, 80, strokeColor=NEUTRAL, strokeWidth=1))
    d.add(String(250, 65, "zaman →", fontName=FONT, fontSize=8,
                 textAnchor="middle", fillColor=NEUTRAL))

    # Startup
    d.add(_box(50, 130, 150, 30, "startupProbe",
               sub="ağır başlangıçlar için",
               fill=colors.HexColor("#fff7ed"), stroke=ACCENT, fontsize=9))
    d.add(_arrow(120, 130, 120, 90, color=ACCENT, label="başarılı"))

    # Liveness & Readiness paralel
    d.add(_box(220, 175, 230, 30, "livenessProbe",
               sub="başarısız → kill + restart",
               fill=colors.HexColor("#fee2e2"), stroke=DANGER, fontsize=9))
    d.add(_box(220, 130, 230, 30, "readinessProbe",
               sub="başarısız → endpoint listesinden çıkar",
               fill=colors.HexColor("#dcfce7"), stroke=SUCCESS, fontsize=9))
    d.add(_arrow(335, 175, 335, 90, color=DANGER, dashed=True))
    d.add(_arrow(335, 130, 335, 90, color=SUCCESS, dashed=True))

    # İşaretler
    d.add(String(50, 95, "Pod başlar", fontName=FONT,
                 fontSize=8, fillColor=NEUTRAL))
    d.add(String(125, 30, "startup OK → diğer probe'lar başlar",
                 fontName=FONT, fontSize=8, fillColor=ACCENT))
    d.add(String(335, 30, "sürekli (periodSeconds)",
                 fontName=FONT, fontSize=8, fillColor=NEUTRAL,
                 textAnchor="middle"))

    _caption(d, "startupProbe başarılı olana kadar liveness/readiness çalışmaz. Yavaş başlayan uygulamalar için kritik.")
    return d


# ===========================================================================
# 11) INGRESS TOPOLOJİSİ
# ===========================================================================
def ingress_topology():
    d = Drawing(500, 240)
    _title(d, "Ingress Topolojisi — Dış İstemciden Pod'a")

    d.add(_box(20, 110, 90, 50, "İstemci",
               sub="tarayıcı", fill=LIGHT, fontsize=9))
    d.add(_box(135, 110, 120, 50, "Ingress Controller",
               sub="NGINX / Traefik",
               fill=colors.HexColor("#fff7ed"), stroke=ACCENT, fontsize=9))
    d.add(_box(280, 165, 200, 30, "Ingress kuralı: api.local/api",
               fill=colors.white, stroke=PRIMARY, fontsize=8))
    d.add(_box(280, 120, 200, 30, "Ingress kuralı: api.local/admin",
               fill=colors.white, stroke=PRIMARY, fontsize=8))
    d.add(_box(290, 60, 90, 40, "Service: api",
               fill=LIGHT, fontsize=9))
    d.add(_box(395, 60, 90, 40, "Service: admin",
               fill=LIGHT, fontsize=9))

    d.add(_arrow(110, 135, 135, 135, color=PRIMARY))
    d.add(_arrow(255, 135, 280, 180, color=PRIMARY, label="/api"))
    d.add(_arrow(255, 135, 280, 135, color=PRIMARY, label="/admin"))
    d.add(_arrow(335, 165, 335, 100, color=NEUTRAL))
    d.add(_arrow(440, 120, 440, 100, color=NEUTRAL))

    _caption(d, "Ingress = L7 yönlendirme kuralları. Ingress Controller bunları gerçek bir proxy'ye uygular.")
    return d


# ===========================================================================
# 12) NAMESPACE — sanal cluster bölümlemesi
# ===========================================================================
def namespace_diagram():
    d = Drawing(500, 200)
    _title(d, "Namespace — Sanal Cluster İçinde İzolasyon")

    # Tek cluster, çoklu namespace
    d.add(Rect(20, 30, 460, 140, rx=10, ry=10,
               fillColor=BG, strokeColor=NEUTRAL, strokeWidth=1))
    d.add(String(250, 175, "Cluster (paylaşılan API + Node havuzu)",
                 fontName=FONT_BOLD, fontSize=9,
                 textAnchor="middle", fillColor=NEUTRAL))

    namespaces = [
        ("dev",     colors.HexColor("#ecfdf5"), SUCCESS),
        ("staging", colors.HexColor("#fff7ed"), ACCENT),
        ("prod",    colors.HexColor("#fee2e2"), DANGER),
        ("kube-system", LIGHT, PRIMARY),
    ]
    for i, (name, fill, color) in enumerate(namespaces):
        x = 35 + i * 113
        d.add(Rect(x, 50, 100, 100, rx=6, ry=6,
                   fillColor=fill, strokeColor=color, strokeWidth=1))
        d.add(String(x + 50, 138, name, fontName=FONT_BOLD,
                     fontSize=9, textAnchor="middle", fillColor=color))
        for j, p in enumerate(["Pod", "Svc", "CM"]):
            d.add(_box(x + 10, 90 - j * 18, 80, 14, p,
                       fill=colors.white, fontsize=7, bold=False))

    _caption(d, "Namespace'ler kaynak isimleri için scope sağlar; Node'lar paylaşılır, izolasyon mantıksaldır.")
    return d
