# Changelog - mini_sensor (MiniSensor)

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert. Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/) und diese Versionierung folgt dem [Semantic Versioning](https://semver.org/lang/de/). Offene Punkte, Ideen und geplante Erweiterungen stehen nicht hier, sondern in [BACKLOG.md](./BACKLOG.md).

---

## [0.1.0] - 2026-08-09

### Hinzugefügt
- **Initiale Version (Beispielanwendung):** Temperaturmessung via 1-Wire (DS18B20) auf der universellen Platine MiniSensor (ESP-12F/ESP8266) — Beispiel: Pool-Wassertemperatur.
- **Messwert:** Temperatur (`GPIO2`), 30 s Update-Intervall, geglättet (`sliding_window_moving_average`, Fenster 10).
- **I²C-Bus vorbereitet:** `GPIO4`/`GPIO5` als I²C-Bus aktiviert (`scan: true`), aktuell ohne angeschlossenen Sensor — Platine ist für 1-Wire **und** I²C ausgelegt.
- **STATUS-LED (rot, `GPIO13`):** Zeigt den ESPHome-/API-Verbindungsstatus per Blinkfrequenz — langsam (100 ms an / 1200 ms aus), solange die API-/WLAN-Verbindung noch nicht steht, schnell (100 ms an / 600 ms aus) sobald die API verbunden ist. Umgesetzt über einen Endlos-Script-Loop (`status_led_run`), analog zu omnilink-poolboy.
- **Konnektivität:** Home-Assistant-API (verschlüsselt), WiFi mit AP-Fallback, OTA und lokaler Webserver (Port 80, Auth `digest`).
- **Diagnose:** Einbindung des gemeinsamen `common/diagnostics.yaml`-Packages sowie eines API-Verbindungsstatus-Sensors.
- **Entity-Benennung:** Nummeriertes Schema (Kategorie `1.x` für projektspezifische Sensoren) passend zum Sortierkonzept des common-Packages.

### Sicherheit
- **Secrets ausgelagert:** API-Key, OTA- und AP-Passwort liegen nicht inline im YAML, sondern in der zentralen, per `.gitignore` ausgeschlossenen `secrets.yaml`.
