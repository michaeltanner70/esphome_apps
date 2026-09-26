# Changelog - omnilink-poolboy

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert. Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/) und diese Versionierung folgt dem [Semantic Versioning](https://semver.org/lang/de/). Offene Punkte, Ideen und geplante Erweiterungen stehen nicht hier, sondern in [BACKLOG.md](./BACKLOG.md).

---

## [0.4.2] - 2026-09-26

### Geändert
- **MSG-LED:** `rgb_order: GRB` → `channel_colors: GRB` (von ESPHome angebotene Migration: seit 2026.8 in `channel_colors` zusammengefasst, alte Schreibweise entfällt in 2027.3.0). Funktional unverändert.

---

## [0.4.1] - 2026-09-26

Behebt die beiden bekannten Mängel von 0.4.0. Konfiguration mit ESPHome 2026.9.0 validiert, Compile/Flash stehen noch aus.

### Behoben
- **pH-/Redox-Sperre prüft jetzt das Statusbit desselben Zyklus:** Rohwerte `0x0102`/`0x0103` werden intern gelesen (`1.2 pH roh`, `1.3 Redox roh`) und erst im `on_value` der internen Statusregister `0x0107`/`0x0108` (U_WORD, Bit 14) an die Template-Sensoren „1.2 pH" / „1.3 Redox" übergeben. Kein zusätzlicher Bus-Verkehr: die Statusregister liegen im bereits bestehenden Kommando ab `0x0107`. Namen, `device_class`, Einheit und `state_class` unverändert → Entity-IDs und Historie bleiben erhalten.
- **MSG-LED:** Die Datenaktualität hängt am Modbus-Zyklus (Zeitstempel beim Lesen von `0x0108`), nicht mehr an pH/Redox. Gesperrte Messung (Messmodul inaktiv, z. B. Umwälzpumpe steht) = konstant **weiss** statt rot blinken. Rot blinken heisst wieder ausschliesslich: kein Modbus-Zyklus seit 45 s.
- **Webserver:** `type: digest` wieder gesetzt (in 0.4.0 verloren gegangen; in 2026.9 weiterhin gültig, ohne die Angabe fällt ESPHome auf `basic` zurück).

### Sicherheit
- **OTA verschlüsselt (Noise):** `ota: encryption:` statt `password: !secret poolboy_ota_key`. Ein leeres `encryption:` übernimmt den API-Schlüssel `poolboy_api_key`; ESPHome 2026.9 hatte das OTA-Passwort als überflüssig (Flash/RAM) angemahnt. `poolboy_ota_key` wird nicht mehr gebraucht.
- **Webserver-OTA bleibt offen (Entscheid 26.09.2026):** Die Noise-Verschlüsselung gilt nur für ESPHome-OTA; der `/update`-Endpunkt des Webservers bleibt unverschlüsselt, geschützt durch das Digest-Login. Flashen über den Webzugang soll möglich bleiben, darum kein `web_server: ota: false`.

### Nach dem Flash prüfen
- „1.2 pH" und „1.3 Redox" behalten ihre Entity-IDs (`sensor.omnilink_poolboy_1_2_ph`, `…_1_3_redox`) — keine Duplikate mit Suffix `_2`.

---

## [0.4.0] - 2026-09-26

Build unter ESPHome 2026.9.0, per OTA auf das Gerät geflasht. Umfang: Migration auf 2026.9 und Priorität 1 („Gültigkeit") aus dem Backlog.

### Geändert
- **Migration ESPHome 2026.9:** `force_new_range: true` (in 2026.9 entfallen) → `reuse_previous_range: false` an den fünf Sensoren `0x0100`–`0x0103` und `0x0107`. 1:1-Entsprechung, weiterhin je ein eigenes Modbus-Kommando, keine Bereichszusammenfassung.
- Header-Kommentar auf Ziel „ESPHome 2026.9.x", Änderungsblock im Header, `fw_version` 0.4.0.

### Hinzugefügt
- **Gültigkeitsbits als Binärsensoren:** `MBF_PH_STATUS` (`0x0107`) Bit 14 „1.4 pH Messmodul aktiv" (`0x4000`), Bit 10 „1.4 pH Durchfluss" (`0x0400`), Bit 13 „1.4 pH Regelung aktiv" (`0x2000`); `MBF_RX_STATUS` (`0x0108`) Bit 14 „1.8 Redox Messmodul aktiv" (`0x4000`). Der bestehende Sensor „1.4 pH Status" (Alarm-Nibble `0x000F`) bleibt unverändert.
- **Fail-Safe-Sperre pH/Redox:** Filter-Lambda verwirft den Wert (kein Publish), sobald das Messmodul-Bit abfällt, nachdem es einmal gesetzt war. Ziel: den Ersatzwert 7.00 der Anlage nicht als Messwert veröffentlichen.
- **Langzeitstatistik:** `state_class: measurement` für 1.0 Ionisation, 1.1 Hydrolyse, 1.2 pH und 1.3 Redox. Bewusst nicht für „1.4 pH Status" (Zustandscode).
- **Registerzuordnung dokumentiert:** Die Sensoren „1.7 Redox On Target / Low / Flow" lesen `0x010D` = `MBF_HIDRO_STATUS` (Bit 0 / 1 / 3), nicht `MBF_RX_STATUS`. Namen bleiben (Entscheid 17.09.2026), weil die Hydrolyse vom Redoxmodul freigegeben und auf den Redox-Sollwert geregelt wird. „1.7 Redox Flow" ist der Durchflusswächter der Hydrolysezelle und **kein** Gültigkeitskriterium für den Redoxwert.

### Entfernt
- `type: digest` bei `web_server: auth` (in 0.3.0 eingeführt) ist in diesem Stand nicht mehr enthalten — in der Übergabe nicht erwähnt, Grund offen.

### Bekannte Mängel (behoben in 0.4.1)
- Die Sperre prüft das Statusbit des **vorherigen** Zyklus (pH/Redox werden vor `0x0107`/`0x0108` gelesen). Beim Filterstopp kann ein 7.00 durchrutschen, das HA dann bis zum nächsten gültigen Wert anzeigt.
- Die MSG-LED blinkt bei gesperrten Werten rot (Kommunikationsausfall), obwohl der Bus läuft — z. B. jede Nacht bei stehender Umwälzpumpe.

### Betrieb (Home Assistant, nicht in der YAML)
- Die vier neuen Binärsensoren bekamen bei der Discovery das Bereichspräfix `schwimmbad_`. Im Entity-Registry umbenannt, bevor etwas darauf verwies: `binary_sensor.schwimmbad_omnilink_poolboy_…` → `binary_sensor.omnilink_poolboy_1_4_ph_messmodul_aktiv`, `…_1_4_ph_durchfluss`, `…_1_4_ph_regelung_aktiv`, `…_1_8_redox_messmodul_aktiv`. Neue Entitäten nach der Discovery auf dieses Präfix kontrollieren.

---

## [0.3.0] - 2026-07-01

### Hinzugefügt
- **MSG-LED (WS2812B, `GPIO21`) — Wasserwerte-Farbanzeige:** Zeigt pH/Redox als gedimmte Farbe (`msg_led_brightness = 0.5`) — grün (7.1 < pH < 7.3 und Redox > 650mV), rot (pH < 6.9 oder > 7.4 oder Redox < 600mV), gelb (übriger Übergangs-/Warnbereich).
- **MSG-LED — Daten-Aktualitätsprüfung:** Solange seit mehr als `msg_led_stale_timeout_ms` (45s = 1.5x update_interval) kein gültiger pH-/Redox-Wert kam, blinkt die LED **rot** im Takt 500ms an/aus (`msg_led_monitor`, geprüft per Zeitstempel `msg_led_last_update_ms` bei jedem 500ms-Zyklus). Deckt sowohl die Startphase als auch spätere Kommunikations-Unterbrüche mit demselben Mechanismus ab.
- **MSG-LED — Kommunikations-Indikator:** Flackert bei jedem Modbus-Poll-Zyklus 3× kurz aus (je 50ms aus / 50ms Farbe wiederhergestellt, `msg_led_comm_blip`), ausgelöst über `on_value` des zuerst abgefragten Registers „1.0 Ionisation". Die aktuelle Wasserwerte-Farbe bleibt danach erhalten.
- **Geteilte Leitung getestet:** GPIO21 versorgt sowohl die WS2812 als auch eine diskrete grüne LED. Ein Leitungstest (reiner Digital-High-Pegel für 200ms) hat bestätigt, dass beide Komponenten koexistieren können, ohne dass die WS2812 gestört wird.

### Sicherheit
- **Webserver-Auth auf `digest` umgestellt:** ESPHome 2026.7.0 warnt beim Kompilieren, dass `web_server: auth:` aktuell noch auf `basic` defaultet (Passwort geht dabei leicht reversibel übers Netz) und der Default erst in ESPHome 2027.1.0 auf `digest` wechselt. Statt nur `type: basic` explizit zu setzen (Warnung stumm schalten), direkt auf `type: digest` umgestellt.

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
