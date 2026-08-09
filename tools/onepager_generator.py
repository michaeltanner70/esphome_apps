#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""One-Pager-Generator (A4, eine Seite) — Messe-Datenblaetter fuer die Projekte.

Einheitliches Design ueber mehrere Projekte (siehe tools/README.md): Layout,
Typografie und Farben sind fixiert, pro Projekt wird nur der Inhalt aus dem
PROJECTS-Block unten gefuellt. Der QR-Code wird beim Lauf frisch aus REPO_URL
erzeugt und — falls opencv verfuegbar ist — per Decode verifiziert. Die fertigen
PDFs landen im Repo-Root.

Benoetigt (in einer venv, NICHT ins System-Python):
    python -m venv .venv
    .venv/Scripts/pip install reportlab "qrcode[pil]" opencv-python-headless
    .venv/Scripts/python tools/onepager_generator.py            # alle Projekte
    .venv/Scripts/python tools/onepager_generator.py filahygro  # nur eines
"""

import sys
import tempfile
from pathlib import Path

import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfgen import canvas as canvas_mod

# =====================================================================
# ANPASSEN: Projektspezifischer Inhalt (aus dem Repo recherchiert bzw.
# erfragt — Kontakt/Footer und QR-URL NICHT ohne Rueckfrage aendern).
# Ein Eintrag je Projekt; das Design (unten) gilt fuer alle gleich.
# =====================================================================

REPO_ROOT = Path(__file__).resolve().parent.parent
REPO_URL = "https://github.com/michaeltanner70/esphome_apps"
FOOTER_NAMES = ["Michael Tanner"]
QR_CAPTION = "PROJEKT AUF GITHUB"

PROJECTS = {
    # -----------------------------------------------------------------
    "omnilink": {
        "out": "OmniLink-OnePager.pdf",
        "title": "OmniLink-PoolBoy",
        "subtitle": "Pool-Monitoring: eigene ESP32-C6-Platine + ESPHome-Firmware",
        "tagline": "Open-Source-Bastelprojekt · ESPHome · Modbus RTU · Home Assistant · MIT-Lizenz",
        "intro": (
            "Der OmniLink-PoolBoy liest ein PoolBoy-Elektrolysegerät per Modbus RTU (RS485) "
            "aus und stellt Ionisation, Hydrolyse, pH und Redox in Home Assistant bereit. "
            "Herzstück ist die eigenentwickelte Platine OmniLink-C6 rund um ein Seeed XIAO "
            "ESP32-C6, auf der ESPHome läuft. Zwei Status-LEDs machen Verbindungszustand und "
            "Wasserwerte direkt am Gerät sichtbar."
        ),
        "arch_title": "System — Platine & Firmware",
        "arch_cards": [
            ("OmniLink-C6 · Trägerplatine (Rev 2.0)",
             "Eigenentwicklung (TW microsystems) um das Seeed XIAO ESP32-C6. RS485-Transceiver "
             "SN65HVD75, 12 V→5 V-Schaltregler sowie Anschlüsse für I²C, 1-Wire, HAT-Erweiterungen "
             "und eine WS2812-Status-LED."),
            ("omnilink-poolboy · ESPHome-Firmware (v0.3.0)",
             "Zyklische Modbus-Abfrage des PoolBoy und Übergabe an die verschlüsselte "
             "Home-Assistant-API. OTA-Updates, lokaler Webserver mit Digest-Auth und "
             "WLAN-AP-Fallback inklusive."),
        ],
        "col1_title": "Messwerte & Anbindung",
        "col1_bullets": [
            ("Wasserwerte", "Ionisation (mA), Hydrolyse (%), pH und Redox (mV) im 30-Sekunden-Takt."),
            ("Statusbits", "pH-Minus-Pumpe sowie Ionisierungs- und Redox-Status als Binärsensoren."),
            ("Home Assistant", "Native, verschlüsselte API; alle Werte als thematisch sortierte Entitäten."),
            ("Diagnose", "WLAN, freier Speicher, Uptime und Neustart-Grund über gemeinsames Package."),
        ],
        "col2_title": "Technik & Bedienung",
        "col2_bullets": [
            ("RS485 / Modbus", "SN65HVD75-Transceiver, 19200 8N1, 120 Ω-Terminierung und TVS-Schutz."),
            ("Status-LEDs", "Blaue Verbindungs-Ampel; WS2812 zeigt die Wasserwerte farbig (grün/gelb/rot)."),
            ("Konnektivität", "OTA-Updates, lokaler Webserver (Digest-Auth) und WLAN-AP-Fallback."),
            ("Antennenwahl", "Beim Boot fest auf die interne Keramikantenne für reproduzierbaren Funk."),
        ],
        "stats": [
            ("4", "Wasser-\nMesswerte"),
            ("30 s", "Abfrage-\nintervall"),
            ("ESP32-C6", "Controller\n(RISC-V)"),
            ("MIT", "Open-Source\nLizenz"),
        ],
    },
    # -----------------------------------------------------------------
    "minisensor": {
        "out": "MiniSensor-OnePager.pdf",
        "title": "MiniSensor",
        "subtitle": "Universelle 1-Wire-/I²C-Sensorplatine + ESPHome-Firmware",
        "tagline": "Open-Source-Bastelprojekt · ESPHome · 1-Wire · I²C · Home Assistant · MIT-Lizenz",
        "intro": (
            "MiniSensor ist eine universelle Trägerplatine (ESP-12F/ESP8266) für kleine Mess- "
            "und Sensoraufgaben. Sie stellt sowohl einen 1-Wire- als auch einen I²C-Anschluss "
            "bereit — welcher Sensor verbaut wird, entscheidet die jeweilige Anwendung. Das "
            "Beispiel-YAML misst die Pool-Wassertemperatur über einen DS18B20 und übergibt sie "
            "an Home Assistant; die Platine dient zugleich als Vorlage für weitere Sensoren."
        ),
        "arch_title": "System — Platine & Firmware",
        "arch_cards": [
            ("MiniSensor · Trägerplatine (Rev 1.0)",
             "Eigenentwicklung (TW microsystems) um ein ESP-12F (ESP8266). 1-Wire (J2/J5) und "
             "I²C (J3) mit je 4k7-Pull-ups, 12 V→3,3 V per NCP718-Regler, GPIO-gesteuerte "
             "Status-LED und FTDI-Header für den Erstflash."),
            ("mini-sensor · ESPHome-Firmware (v0.1.0)",
             "Beispielanwendung Pool-Wassertemperatur (DS18B20) an die verschlüsselte "
             "Home-Assistant-API. Vorlage für weitere 1-Wire- oder I²C-Sensoren auf derselben "
             "Platine."),
        ],
        "col1_title": "Anschlüsse & Anbindung",
        "col1_bullets": [
            ("1-Wire", "GPIO2 mit 4k7-Pull-up (J2/J5) — DS18B20 und andere 1-Wire-Sensoren."),
            ("I²C", "SDA/SCL auf GPIO4/GPIO5 (J3), 4k7-Pull-ups — bereit für weitere Sensoren."),
            ("Home Assistant", "Native, verschlüsselte API; Messwerte als thematisch sortierte Entitäten."),
            ("Diagnose", "WLAN, freier Speicher, Uptime und Neustart-Grund über gemeinsames Package."),
        ],
        "col2_title": "Technik & Bedienung",
        "col2_bullets": [
            ("Beispiel-Sensor", "DS18B20, 12-Bit-Auflösung, 30-Sekunden-Takt, gleitender Mittelwert."),
            ("Status-LED", "Rote LED zeigt den Verbindungsstatus per Blinkfrequenz (langsam/schnell)."),
            ("Konnektivität", "OTA-Updates, lokaler Webserver (Digest-Auth) und WLAN-AP-Fallback."),
            ("Universell", "1-Wire und I²C gleichzeitig nutzbar — eine Platine für viele Messaufgaben."),
        ],
        "stats": [
            ("2", "Bus-Systeme\n(1-Wire + I²C)"),
            ("30 s", "Abfrage-\nintervall"),
            ("ESP-12F", "Controller\n(ESP8266)"),
            ("MIT", "Open-Source\nLizenz"),
        ],
    },
    # -----------------------------------------------------------------
    "filahygro": {
        "out": "FilaHygro-OnePager.pdf",
        "title": "FilaHygro",
        "subtitle": "Filament-Lagerbehälter im Blick: Temperatur & Feuchte, akkubetrieben",
        "tagline": "Open-Source-Bastelprojekt · ESPHome · MQTT · Deep-Sleep · Akku · MIT-Lizenz",
        "intro": (
            "FilaHygro überwacht Temperatur und Luftfeuchtigkeit in Filament-Lagerbehältern. "
            "Hygroskopische Filamente wie ABS oder Nylon nehmen bei zu hoher Feuchtigkeit Wasser "
            "auf und verlieren an Druckqualität — FilaHygro macht den Zustand messbar. Das Gerät "
            "läuft auf einem 18650-Akku, misst zyklisch, meldet die Werte per MQTT und legt sich "
            "danach in Deep-Sleep, um die Akkulaufzeit zu maximieren."
        ),
        "arch_title": "System — Platine & Firmware",
        "arch_cards": [
            ("FilaHygro · Sensorplatine (Rev 2)",
             "Eigenentwicklung (TW microsystems) um ein ESP-12F (ESP8266). SHT31-D-Sensor über "
             "I²C, 18650-Akku mit TP4056-Laderegler (Micro-USB), NCP718-Spannungsregler und "
             "FTDI-Header für den Erstflash."),
            ("filabox1 · ESPHome-Firmware (v0.1.0)",
             "Misst zyklisch, sendet die Werte als kompaktes JSON per MQTT und schläft danach — "
             "konsequent stromsparend, ohne dauerhafte Netzwerkverbindung."),
        ],
        "col1_title": "Messwerte & Anbindung",
        "col1_bullets": [
            ("Klima", "Temperatur (°C) und relative Luftfeuchtigkeit (%) im Lagerbehälter (SHT31-D)."),
            ("MQTT", "Werte als kompaktes JSON an den lokalen Broker — anbindbar z. B. an Home Assistant."),
            ("Akku", "Betrieb an einer 18650-Zelle, nachladbar per Micro-USB über den TP4056."),
            ("Sensorwahl", "SHT31-D (0x44) oder HDC1080 (0x40) per Lötbrücke bestückbar."),
        ],
        "col2_title": "Stromsparen & Technik",
        "col2_bullets": [
            ("Deep-Sleep", "Aufwachen, messen, senden, schlafen — maximiert die Akkulaufzeit."),
            ("Messfenster", "Spannungsteiler nur während der Messung aktiv, danach abgeschaltet."),
            ("MCU", "ESP-12F (ESP8266); I²C-Sensor auf GPIO4/GPIO5."),
            ("Erstflash", "Per FTDI-Header (J1) — kein Onboard-USB für die Programmierung nötig."),
        ],
        "stats": [
            ("2", "Klimawerte\n(Temp + Feuchte)"),
            ("18650", "Akku-\nbetrieb"),
            ("MQTT", "Übermittlung\n(Deep-Sleep)"),
            ("MIT", "Open-Source\nLizenz"),
        ],
    },
}

# Akzentfarbe: Teal/Cyan — passt zum ESPHome-Blau der Badges. Bewusst
# einheitlich ueber alle Projekte (siehe tools/README.md).
TEAL = HexColor("#0891b2")
TEAL_DARK = HexColor("#075e73")

# =====================================================================
# AB HIER NICHT AENDERN — Layout/Typografie/Design ist fixiert.
# =====================================================================

INK = HexColor("#1b1e22")
DIM = HexColor("#5b636b")
LINE = HexColor("#d7dbe0")
PANEL = HexColor("#f3f5f6")
WHITE = HexColor("#ffffff")

PAGE_W, PAGE_H = A4
MARGIN = 18 * mm
BAND_H = 48 * mm

styles = {
    "intro": ParagraphStyle("intro", fontName="Helvetica", fontSize=10.3, leading=15, textColor=INK),
    "h2": ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=11.5, leading=14, textColor=TEAL_DARK, spaceAfter=5),
    "arch_label": ParagraphStyle("arch_label", fontName="Helvetica-Bold", fontSize=10, leading=12, textColor=INK),
    "arch_body": ParagraphStyle("arch_body", fontName="Helvetica", fontSize=9, leading=12.5, textColor=DIM),
    "bullet": ParagraphStyle("bullet", fontName="Helvetica", fontSize=9.3, leading=13.6, textColor=INK),
    "stat_num": ParagraphStyle("stat_num", fontName="Helvetica-Bold", fontSize=21, leading=24, textColor=TEAL_DARK, alignment=TA_CENTER),
    "stat_label": ParagraphStyle("stat_label", fontName="Helvetica", fontSize=8.3, leading=11, textColor=DIM, alignment=TA_CENTER),
}


def generate_qr(qr_path, repo_url):
    """QR frisch aus repo_url erzeugen und (falls opencv da ist) verifizieren."""
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=12, border=4)
    qr.add_data(repo_url)
    qr.make(fit=True)
    qr.make_image(fill_color="#1b1e22", back_color="white").save(qr_path)
    try:
        import cv2
        decoded, _, _ = cv2.QRCodeDetector().detectAndDecode(cv2.imread(qr_path))
        if decoded != repo_url:
            sys.exit(f"QR-Verifikation fehlgeschlagen: '{decoded}' != '{repo_url}'")
        print("QR verifiziert:", decoded)
    except ImportError:
        print("WARNUNG: opencv nicht installiert — QR nicht verifiziert (URL:", repo_url, ")")


def draw_background(cfg, qr_path):
    """Liefert den onPage-Callback (Kopfband, Footer, QR) fuer ein Projekt."""
    def _draw(c: canvas_mod.Canvas, doc):
        c.saveState()
        c.setFillColor(TEAL)
        c.rect(0, PAGE_H - BAND_H, PAGE_W, BAND_H, stroke=0, fill=1)
        c.setFillColor(TEAL_DARK)
        c.rect(0, PAGE_H - BAND_H - 1.4 * mm, PAGE_W, 1.4 * mm, stroke=0, fill=1)

        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 26)
        c.drawString(MARGIN, PAGE_H - 24 * mm, cfg["title"])
        c.setFont("Helvetica", 12.5)
        c.drawString(MARGIN, PAGE_H - 32 * mm, cfg["subtitle"])
        c.setFont("Helvetica", 8.7)
        c.setFillColor(HexColor("#dff2ee"))
        c.drawString(MARGIN, PAGE_H - 39.5 * mm, cfg["tagline"])

        c.setStrokeColor(LINE)
        c.setLineWidth(0.6)
        footer_y = 34 * mm
        c.line(MARGIN, footer_y, PAGE_W - MARGIN, footer_y)

        c.setFillColor(TEAL_DARK)
        c.setFont("Helvetica-Bold", 7.6)
        c.drawString(MARGIN, footer_y - 7 * mm, "PROJEKTTEAM")
        c.setFillColor(INK)
        c.setFont("Helvetica", 10.5)
        name_y = footer_y - 12.5 * mm
        x = MARGIN
        for i, name in enumerate(FOOTER_NAMES):
            c.drawString(x, name_y, name)
            x += c.stringWidth(name, "Helvetica", 10.5)
            if i < len(FOOTER_NAMES) - 1:
                c.drawString(x + 6, name_y, "&")
                x += 6 + c.stringWidth("&", "Helvetica", 10.5) + 6

        qr_size = 20 * mm
        qr_x = PAGE_W - MARGIN - qr_size
        qr_y = footer_y - 23 * mm
        c.drawImage(qr_path, qr_x, qr_y, width=qr_size, height=qr_size, preserveAspectRatio=True, mask="auto")
        c.setFillColor(TEAL_DARK)
        c.setFont("Helvetica-Bold", 7.6)
        c.drawCentredString(qr_x + qr_size / 2, qr_y - 4.5 * mm, QR_CAPTION)

        c.restoreState()

    return _draw


def section_header(text):
    return Paragraph(text.upper(), styles["h2"])


def bullets(items):
    rows = []
    for head, body in items:
        rows.append(Paragraph(f"<b>{head}</b> — {body}", styles["bullet"]))
        rows.append(Spacer(1, 5.2))
    if rows:
        rows.pop()
    return rows


def build(cfg, out_path, qr_path):
    doc = SimpleDocTemplate(
        out_path, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=BAND_H + 10 * mm, bottomMargin=42 * mm,
    )
    story = [Paragraph(cfg["intro"], styles["intro"]), Spacer(1, 13)]

    story.append(section_header(cfg["arch_title"]))
    story.append(Spacer(1, 2))
    cards = []
    for label, body in cfg["arch_cards"]:
        cards.append([
            Paragraph(label, styles["arch_label"]), Spacer(1, 2),
            Paragraph(body, styles["arch_body"]),
        ])
    arch_table = Table([cards], colWidths=[(PAGE_W - 2 * MARGIN - 6 * mm) / len(cards)] * len(cards))
    arch_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PANEL),
        ("BOX", (0, 0), (0, 0), 0.6, LINE), ("BOX", (1, 0), (1, 0), 0.6, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 9), ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(arch_table)
    story.append(Spacer(1, 16))

    col_w = (PAGE_W - 2 * MARGIN - 8 * mm) / 2
    cols_table = Table(
        [[
            [section_header(cfg["col1_title"]), Spacer(1, 3)] + bullets(cfg["col1_bullets"]),
            [section_header(cfg["col2_title"]), Spacer(1, 3)] + bullets(cfg["col2_bullets"]),
        ]],
        colWidths=[col_w, col_w],
    )
    cols_table.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (0, 0), 8 * mm), ("RIGHTPADDING", (1, 0), (1, 0), 0),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(cols_table)
    story.append(Spacer(1, 26))

    story.append(section_header("Auf einen Blick"))
    story.append(Spacer(1, 8))
    stats = cfg["stats"]
    stat_col_w = (PAGE_W - 2 * MARGIN) / len(stats)
    stat_row = [[
        Paragraph(num, styles["stat_num"]), Spacer(1, 2),
        Paragraph(label.replace("\n", "<br/>"), styles["stat_label"]),
    ] for num, label in stats]
    stat_table = Table([stat_row], colWidths=[stat_col_w] * len(stats))
    stat_style = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 0)]
    for i in range(1, len(stats)):
        stat_style.append(("LINEBEFORE", (i, 0), (i, 0), 0.6, LINE))
    stat_table.setStyle(TableStyle(stat_style))
    story.append(stat_table)

    draw = draw_background(cfg, qr_path)
    doc.build(story, onFirstPage=draw, onLaterPages=draw)


def render(key):
    cfg = PROJECTS[key]
    out_path = str(REPO_ROOT / cfg["out"])
    qr_path = str(Path(tempfile.gettempdir()) / f"{key}_onepager_qr.png")
    generate_qr(qr_path, REPO_URL)
    build(cfg, out_path, qr_path)
    print("PDF geschrieben:", out_path)


if __name__ == "__main__":
    keys = sys.argv[1:] or list(PROJECTS)
    unknown = [k for k in keys if k not in PROJECTS]
    if unknown:
        sys.exit(f"Unbekanntes Projekt: {', '.join(unknown)}. Verfuegbar: {', '.join(PROJECTS)}")
    for k in keys:
        render(k)
