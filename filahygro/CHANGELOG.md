# Changelog - filahygro (FilaHygro)

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert. Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/) und diese Versionierung folgt dem [Semantic Versioning](https://semver.org/lang/de/). Offene Punkte, Ideen und geplante Erweiterungen stehen nicht hier, sondern in [BACKLOG.md](./BACKLOG.md).

---

## [0.1.0] - 2026-08-09

### Hinzugefügt
- **Initiale Version:** Temperatur-/Feuchtigkeitsmessung (SHT31-D), Akkuspannung/SoC und MQTT-Publish-and-Sleep auf der Platine FilaHygro (ESP-12F/ESP8266, Rev 2).
- **Messwerte:** Temperatur, Luftfeuchtigkeit (SHT31-D, `0x44`, `GPIO4`/`GPIO5`), Akkuspannung (ADC, `A0`), Akku-SoC (Lookup-Tabelle).
- **Konnektivität:** MQTT (JSON-Payload, Topic `FilaBox/data`, kein Discovery); WiFi. Bewusst **keine** Home-Assistant-API, kein Webserver — passend zum Deep-Sleep-Zyklus im Akkubetrieb. OTA ist als per MQTT getriggerter Dauerbetrieb-Modus geplant, aber noch nicht implementiert (siehe [BACKLOG.md](./BACKLOG.md)).

### Geändert
- **`esp8266: board`** von `d1_mini` auf `esp12e` korrigiert — entspricht dem tatsächlich verbauten ESP-12F (kein Wemos-D1-Mini-Board vorhanden); ohne funktionale Auswirkung, da alle Pins bereits als rohe GPIO-Nummern angesprochen werden.

### Sicherheit
- **Secrets ausgelagert:** WLAN- sowie MQTT-Zugangsdaten (`filahygro_mqtt_broker`, `filahygro_mqtt_user`, `filahygro_mqtt_password`) liegen nicht mehr inline im YAML, sondern in der zentralen, per `.gitignore` ausgeschlossenen `secrets.yaml`.

### Bekannt (nicht behoben)
- **Akku-SoC unzuverlässig:** Die gemeldete Akkuspannung/SoC zeigt in der Praxis dauerhaft ~4V/100%, unabhängig vom tatsächlichen Ladezustand. Siehe [BACKLOG.md](./BACKLOG.md).
