# tools

Hilfsskripte rund ums Repo (nicht Teil der Firmware).

---

## `onepager_generator.py`

Erzeugt die Messe-Datenblätter (A4, eine Seite) im Repo-Root — je Projekt ein PDF mit identischem Design:

| Projekt | Datenblatt |
| :--- | :--- |
| `omnilink` | [`OmniLink-OnePager.pdf`](../OmniLink-OnePager.pdf) |
| `minisensor` | [`MiniSensor-OnePager.pdf`](../MiniSensor-OnePager.pdf) |
| `filahygro` | [`FilaHygro-OnePager.pdf`](../FilaHygro-OnePager.pdf) |

Der QR-Code (verweist auf das GitHub-Repo) wird bei jedem Lauf frisch generiert und — falls `opencv` installiert ist — per Decode gegen die Soll-URL verifiziert.

### Verwendung

In einer virtuellen Umgebung ausführen (nicht ins System-Python installieren):

```bash
python -m venv .venv
.venv/Scripts/pip install reportlab "qrcode[pil]" opencv-python-headless
.venv/Scripts/python tools/onepager_generator.py            # alle Projekte
.venv/Scripts/python tools/onepager_generator.py filahygro  # nur ein Projekt
```

Ohne Argument werden alle Projekte erzeugt; sonst nur die angegebenen (Schlüssel wie in der Tabelle). `opencv-python-headless` ist optional (nur für die QR-Verifikation) — ohne läuft die PDF-Erzeugung trotzdem, dann mit Warnhinweis.

### Anpassen

Layout, Typografie und Farben sind fixiert (einheitliches Design über alle Projekte). Für inhaltliche Änderungen nur den mit `ANPASSEN:` markierten `PROJECTS`-Block oben im Skript bearbeiten (je Projekt: Titel, Karten, Bullets, Kennzahlen, Ausgabe-Pfad). Footer-Namen und `REPO_URL` gelten für alle Projekte gemeinsam und werden nicht ohne Rückfrage geändert.
