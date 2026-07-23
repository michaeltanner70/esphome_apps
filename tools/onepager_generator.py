#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""One-Pager-Generator (A4, eine Seite) — Messe-Datenblatt fuer OmniLink-PoolBoy.

Einheitliches Design ueber mehrere Projekte (siehe tools/README.md). Der QR-Code
wird beim Lauf frisch aus REPO_URL erzeugt und — falls opencv verfuegbar ist —
per Decode verifiziert. Die fertige PDF landet im Repo-Root.

Benoetigt (in einer venv, NICHT ins System-Python):
    python -m venv .venv
    .venv/Scripts/pip install reportlab "qrcode[pil]" opencv-python-headless
    .venv/Scripts/python tools/onepager_generator.py
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
# =====================================================================

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = str(REPO_ROOT / "OmniLink-OnePager.pdf")
QR_PATH = str(Path(tempfile.gettempdir()) / "omnilink_onepager_qr.png")  # frisch generiert, siehe generate_qr()
REPO_URL = "https://github.com/michaeltanner70/esphome_apps"

TITLE = "OmniLink-PoolBoy"
SUBTITLE = "Pool-Monitoring: eigene ESP32-C6-Platine + ESPHome-Firmware"
TAGLINE = "Open-Source-Bastelprojekt · ESPHome · Modbus RTU · Home Assistant · MIT-Lizenz"

INTRO_TEXT = (
    "Der OmniLink-PoolBoy liest ein PoolBoy-Elektrolysegerät per Modbus RTU (RS485) "
    "aus und stellt Ionisation, Hydrolyse, pH und Redox in Home Assistant bereit. "
    "Herzstück ist die eigenentwickelte Platine OmniLink-C6 rund um ein Seeed XIAO "
    "ESP32-C6, auf der ESPHome läuft. Zwei Status-LEDs machen Verbindungszustand und "
    "Wasserwerte direkt am Gerät sichtbar."
)

ARCH_SECTION_TITLE = "System — Platine & Firmware"
ARCH_CARDS = [
    ("OmniLink-C6 · Trägerplatine (Rev 2.0)",
     "Eigenentwicklung (TW microsystems) um das Seeed XIAO ESP32-C6. RS485-Transceiver "
     "SN65HVD75, 12 V→5 V-Schaltregler sowie Anschlüsse für I²C, 1-Wire, HAT-Erweiterungen "
     "und eine WS2812-Status-LED."),
    ("omnilink-poolboy · ESPHome-Firmware (v0.3.0)",
     "Zyklische Modbus-Abfrage des PoolBoy und Übergabe an die verschlüsselte "
     "Home-Assistant-API. OTA-Updates, lokaler Webserver mit Digest-Auth und "
     "WLAN-AP-Fallback inklusive."),
]

COLUMN_1_TITLE = "Messwerte & Anbindung"
COLUMN_1_BULLETS = [
    ("Wasserwerte", "Ionisation (mA), Hydrolyse (%), pH und Redox (mV) im 30-Sekunden-Takt."),
    ("Statusbits", "pH-Minus-Pumpe sowie Ionisierungs- und Redox-Status als Binärsensoren."),
    ("Home Assistant", "Native, verschlüsselte API; alle Werte als thematisch sortierte Entitäten."),
    ("Diagnose", "WLAN, freier Speicher, Uptime und Neustart-Grund über gemeinsames Package."),
]
COLUMN_2_TITLE = "Technik & Bedienung"
COLUMN_2_BULLETS = [
    ("RS485 / Modbus", "SN65HVD75-Transceiver, 19200 8N1, 120 Ω-Terminierung und TVS-Schutz."),
    ("Status-LEDs", "Blaue Verbindungs-Ampel; WS2812 zeigt die Wasserwerte farbig (grün/gelb/rot)."),
    ("Konnektivität", "OTA-Updates, lokaler Webserver (Digest-Auth) und WLAN-AP-Fallback."),
    ("Antennenwahl", "Beim Boot fest auf die interne Keramikantenne für reproduzierbaren Funk."),
]

STATS = [
    ("4", "Wasser-\nMesswerte"),
    ("30 s", "Abfrage-\nintervall"),
    ("ESP32-C6", "Controller\n(RISC-V)"),
    ("MIT", "Open-Source\nLizenz"),
]

FOOTER_NAMES = ["Michael Tanner"]
QR_CAPTION = "PROJEKT AUF GITHUB"

# Akzentfarbe: Teal/Cyan — passt zum ESPHome-Blau der Badges und zum Pool-Thema
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


def generate_qr():
    """QR frisch aus REPO_URL erzeugen und (falls opencv da ist) verifizieren."""
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=12, border=4)
    qr.add_data(REPO_URL)
    qr.make(fit=True)
    qr.make_image(fill_color="#1b1e22", back_color="white").save(QR_PATH)
    try:
        import cv2
        decoded, _, _ = cv2.QRCodeDetector().detectAndDecode(cv2.imread(QR_PATH))
        if decoded != REPO_URL:
            sys.exit(f"QR-Verifikation fehlgeschlagen: '{decoded}' != '{REPO_URL}'")
        print("QR verifiziert:", decoded)
    except ImportError:
        print("WARNUNG: opencv nicht installiert — QR nicht verifiziert (URL:", REPO_URL, ")")


def draw_background(c: canvas_mod.Canvas, doc):
    c.saveState()
    c.setFillColor(TEAL)
    c.rect(0, PAGE_H - BAND_H, PAGE_W, BAND_H, stroke=0, fill=1)
    c.setFillColor(TEAL_DARK)
    c.rect(0, PAGE_H - BAND_H - 1.4 * mm, PAGE_W, 1.4 * mm, stroke=0, fill=1)

    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 26)
    c.drawString(MARGIN, PAGE_H - 24 * mm, TITLE)
    c.setFont("Helvetica", 12.5)
    c.drawString(MARGIN, PAGE_H - 32 * mm, SUBTITLE)
    c.setFont("Helvetica", 8.7)
    c.setFillColor(HexColor("#dff2ee"))
    c.drawString(MARGIN, PAGE_H - 39.5 * mm, TAGLINE)

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
    c.drawImage(QR_PATH, qr_x, qr_y, width=qr_size, height=qr_size, preserveAspectRatio=True, mask="auto")
    c.setFillColor(TEAL_DARK)
    c.setFont("Helvetica-Bold", 7.6)
    c.drawCentredString(qr_x + qr_size / 2, qr_y - 4.5 * mm, QR_CAPTION)

    c.restoreState()


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


def build():
    doc = SimpleDocTemplate(
        OUT_PATH, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=BAND_H + 10 * mm, bottomMargin=42 * mm,
    )
    story = [Paragraph(INTRO_TEXT, styles["intro"]), Spacer(1, 13)]

    story.append(section_header(ARCH_SECTION_TITLE))
    story.append(Spacer(1, 2))
    cards = []
    for label, body in ARCH_CARDS:
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
            [section_header(COLUMN_1_TITLE), Spacer(1, 3)] + bullets(COLUMN_1_BULLETS),
            [section_header(COLUMN_2_TITLE), Spacer(1, 3)] + bullets(COLUMN_2_BULLETS),
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
    stat_col_w = (PAGE_W - 2 * MARGIN) / len(STATS)
    stat_row = [[
        Paragraph(num, styles["stat_num"]), Spacer(1, 2),
        Paragraph(label.replace("\n", "<br/>"), styles["stat_label"]),
    ] for num, label in STATS]
    stat_table = Table([stat_row], colWidths=[stat_col_w] * len(STATS))
    stat_style = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 0)]
    for i in range(1, len(STATS)):
        stat_style.append(("LINEBEFORE", (i, 0), (i, 0), 0.6, LINE))
    stat_table.setStyle(TableStyle(stat_style))
    story.append(stat_table)

    doc.build(story, onFirstPage=draw_background, onLaterPages=draw_background)


if __name__ == "__main__":
    generate_qr()
    build()
    print("PDF geschrieben:", OUT_PATH)
