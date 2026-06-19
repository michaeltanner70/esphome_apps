# Changelog - omnilink-poolboy

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert. Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/) und diese Versionierung folgt dem [Semantic Versioning](https://semver.org/lang/de/).

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
