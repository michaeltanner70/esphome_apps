# tools

Hilfsskripte rund ums Repo (nicht Teil der Firmware).

---

## `onepager_generator.py`

Erzeugt das Messe-Datenblatt [`OmniLink-OnePager.pdf`](../OmniLink-OnePager.pdf) (A4, eine Seite) im Repo-Root. Der QR-Code (verweist auf das GitHub-Repo) wird bei jedem Lauf frisch generiert und — falls `opencv` installiert ist — per Decode gegen die Soll-URL verifiziert.

### Verwendung

In einer virtuellen Umgebung ausführen (nicht ins System-Python installieren):

```bash
python -m venv .venv
.venv/Scripts/pip install reportlab "qrcode[pil]" opencv-python-headless
.venv/Scripts/python tools/onepager_generator.py
```

`opencv-python-headless` ist optional (nur für die QR-Verifikation) — ohne läuft die PDF-Erzeugung trotzdem, dann mit Warnhinweis.

### Anpassen

Layout, Typografie und Farben sind fixiert (einheitliches Design über mehrere Projekte). Für inhaltliche Änderungen nur den mit `ANPASSEN:` markierten Config-Block oben im Skript bearbeiten (Titel, Karten, Bullets, Kennzahlen, Footer-Namen, `REPO_URL`, Akzentfarbe).
