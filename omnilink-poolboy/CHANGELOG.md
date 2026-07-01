# Changelog - omnilink-poolboy

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert. Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/) und diese Versionierung folgt dem [Semantic Versioning](https://semver.org/lang/de/).

---

## [0.3.0] - 2026-07-01

### Hinzugefügt
- **MSG-LED (WS2812B, `GPIO21`) — Wasserwerte-Farbanzeige:** Zeigt pH/Redox als gedimmte Farbe (`msg_led_brightness = 0.5`) — grün (7.1 < pH < 7.3 und Redox > 650mV), rot (pH < 6.9 oder > 7.4 oder Redox < 600mV), gelb (übriger Übergangs-/Warnbereich).
- **MSG-LED — Daten-Aktualitätsprüfung:** Solange seit mehr als `msg_led_stale_timeout_ms` (45s = 1.5x update_interval) kein gültiger pH-/Redox-Wert kam, blinkt die LED **rot** im Takt 500ms an/aus (`msg_led_monitor`, geprüft per Zeitstempel `msg_led_last_update_ms` bei jedem 500ms-Zyklus). Deckt sowohl die Startphase als auch spätere Kommunikations-Unterbrüche mit demselben Mechanismus ab.
- **MSG-LED — Kommunikations-Indikator:** Flackert bei jedem Modbus-Poll-Zyklus 3× kurz aus (je 50ms aus / 50ms Farbe wiederhergestellt, `msg_led_comm_blip`), ausgelöst über `on_value` des zuerst abgefragten Registers „1.0 Ionisation". Die aktuelle Wasserwerte-Farbe bleibt danach erhalten.
- **Geteilte Leitung getestet:** GPIO21 versorgt sowohl die WS2812 als auch eine diskrete grüne LED. Ein Leitungstest (reiner Digital-High-Pegel für 200ms) hat bestätigt, dass beide Komponenten koexistieren können, ohne dass die WS2812 gestört wird.

### Wichtig (Bugfix während der Entwicklung)
- ESPHomes `light.turn_on` normalisiert `red`/`green`/`blue` bei jedem Aufruf automatisch so, dass der grösste Kanal auf `1.0` gesetzt wird (`LightColorValues::normalize_color()`) — kleine RGB-Werte allein dimmen also **nicht**. Die Dimmung der MSG-LED läuft daher über den separaten `brightness`-Parameter (`msg_led_apply_color`), die Farbwerte selbst speichern nur die Hue-Anteile (0.0/1.0).

---

## [0.2.0] - 2026-07-01

### Hinzugefügt
- **STATUS-LED (blau, `GPIO0`):** Zeigt den ESPHome-/API-Verbindungsstatus per Blinkfrequenz — langsam (100 ms an / 1200 ms aus), solange die API-/WLAN-Verbindung noch nicht steht, schnell (100 ms an / 600 ms aus) sobald die API verbunden ist. Off-Zeiten bewusst länger als das MSG-Rot-Blinken (500/500ms), damit die blaue LED optisch nicht untergeht. Umgesetzt über einen Endlos-Script-Loop (`status_led_run`), der bei jedem Zyklus die `api.connected`-Bedingung prüft.

---

## [0.1.0] - 2026-06-19

### Hinzugefügt
- **Initiale Version:** Auslesen des PoolBoy-Elektrolysegeräts via Modbus RTU (RS485) auf der Platine OmniLink-C6 (Seeed XIAO ESP32-C6).
- **Messwerte:** Ionisation (`0x0100`), Hydrolyse (`0x0101`), pH (`0x0102`), Redox (`0x0103`) sowie pH-Status (`0x0107`, bitmask `0x000F`).
- **Statusbits:** pH-Minus-Pumpe (`0x0107`), Ionisierungs- (`0x010C`) und Redox-Statusbits (`0x010D`) als Binary-Sensoren.
- **Konnektivität:** Home-Assistant-API (verschlüsselt), WiFi mit AP-Fallback, OTA und lokaler Webserver (Port 80).
- **Diagnose:** Einbindung des gemeinsamen `common/diagnostics.yaml`-Packages sowie eines API-Verbindungsstatus-Sensors.
- **Feste Antennenwahl:** Beim Boot (`on_boot`, Priorität 800) wird der Onboard-RF-Switch über `GPIO3` aktiviert und mit `GPIO14` fest die interne Keramikantenne gewählt – der Funkpfad ist damit unabhängig vom Auslieferungszustand des XIAO-Moduls eindeutig definiert.
- **Entity-Benennung:** Nummeriertes Schema (Kategorie `1.x` für projektspezifische Sensoren) passend zum Sortierkonzept des common-Packages.

### Sicherheit
- **Secrets ausgelagert:** API-Key, OTA- und AP-Passwort liegen nicht mehr inline im YAML, sondern in der zentralen, per `.gitignore` ausgeschlossenen `secrets.yaml`.

### Geplant / offen
- 1-Wire-Temperatur (J5), I²C (J6), WS2812-Status-LED (`GPIO21`), HAT-Eingänge (J1).
