# ESPHome Apps

[![ESPHome](https://img.shields.io/badge/ESPHome-Ready-03a9f4?logo=esphome&logoColor=white)](https://esphome.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Willkommen in meinem zentralen Repository für alle ESPHome-basierten Smart-Home-Projekte. Hier verwalte und sichere ich die Konfigurationen für meine selbstgebauten Mikrocontroller-Steuerungen auf ESP32-/ESP8266-Basis.

---

## ⚠️ Haftungsausschluss (Disclaimer)

Alle in diesem Repository bereitgestellten Inhalte, Codes und Pläne sind rein private Bastelprojekte. Die Verwendung erfolgt ausdrücklich **auf eigene Gefahr**. Es wird keinerlei Haftung für Schäden an Geräten, Haustechnik oder für Unfälle übernommen. Arbeiten an Netzelektrik (230V) dürfen nur von ausgebildetem Fachpersonal durchgeführt werden.

---

## Repository-Struktur

Um die Wartung so einfach wie möglich zu halten, ist dieses Repository als Monorepo strukturiert. Jedes eigenständige Projekt besitzt seinen eigenen Unterordner inklusive lokaler Dokumentation.

| Ordner / Projekt | Kurzbeschreibung | Status / Version |
| :--- | :--- | :--- |
| [**`omnilink-poolboy`**](./omnilink-poolboy) | Auslesung eines PoolBoy-Elektrolysegeräts via Modbus RTU (RS485) auf der eigenentwickelten Platine OmniLink-C6 (Seeed XIAO ESP32-C6). Liefert Ionisation, Hydrolyse, pH und Redox samt Statusbits (pH-Minus-Pumpe, Ionisierungs- und Redox-Status) an Home Assistant. | v0.3.0 (in Entwicklung) |
| [**`common`**](./common) | Wiederverwendbare Code-Bausteine (Packages), aktuell das Diagnose-Paket `diagnostics.yaml` mit WLAN-, Netzwerk- und System-Sensoren für alle Projekte. | v1.2.1 |

---

## Allgemeine Hinweise zur Verwendung

**Geheimnisse schützen:** Passwörter, WLAN-SSIDs und API-Keys sind in den Projekt-YAMLs über `!secret` ausgelagert. Es gibt eine **zentrale `secrets.yaml` im Repo-Root** für alle Apps. Diese Datei ist über `.gitignore` vom Repository ausgeschlossen – als Vorlage dient [`secrets.yaml.example`](./secrets.yaml.example).

```bash
cp secrets.yaml.example secrets.yaml   # danach echte Werte eintragen
```

**Kompilieren / Flashen:** ESPHome wird **vom Repo-Root aus** aufgerufen, damit sowohl `!include common/...` als auch die zentrale `secrets.yaml` aufgelöst werden (beide Pfade sind relativ zum Aufruf-Verzeichnis):

```bash
esphome run omnilink-poolboy/omnilink-poolboy.yaml
```

---

## 📄 Lizenz

Alle Projekte in diesem Repository stehen unter der [MIT-Lizenz](LICENSE), sofern im jeweiligen Unterordner nicht anders angegeben.
