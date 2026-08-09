# MiniSensor — Projektzusammenfassung

**MiniSensor** ist eine universelle Trägerplatine (ESP-12F/ESP8266) mit
sowohl **1-Wire-** als auch **I²C-Anschluss** — die Hardware ist nicht auf
einen Sensortyp oder Anwendungsfall festgelegt. Dieses Dokument beschreibt
die Hardware-Analyse (gilt für jede Anwendung auf dieser Platine) sowie ein
konkretes **Beispiel**: Messung der Pool-Wassertemperatur über 1-Wire
(DS18B20), umgesetzt in [`mini-sensor.yaml`](./mini-sensor.yaml).

---

## 1. Aufgabe

Auf der eigenentwickelten Hardware (Schaltplan `MiniSensor`) soll ESPHome
laufen, das Sensordaten an Home Assistant sendet. Da die Platine sowohl
1-Wire als auch I²C bereitstellt, ist sie als **universelle Basis** für
verschiedenste Mess-Anwendungen gedacht — welcher Sensor konkret verbaut
wird, entscheidet jeweils das einzelne Projekt/YAML.

Als erstes Beispiel entstand `mini-sensor.yaml`: Auslesen der
Pool-Wassertemperatur über **1-Wire**. Basis für den 1-Wire-Teil ist
konzeptionell das bestehende `poolcontrol-pool-sensor.yaml` (andere
Hardware, ESP32-S3-Board), das GPIO sowie das Pin-Mapping selbst stammen
jedoch aus dem MiniSensor-Schaltplan.

Umfang dieses Beispiels: 1-Wire-Temperaturmessung. Der I²C-Anschluss der
Platine ist als Bus bereits im YAML aktiv (bereit für weitere
Anwendungen/Sensoren), aber ohne angeschlossenen Sensor (siehe
[BACKLOG.md](./BACKLOG.md)).

---

## 2. Hardware-Analyse (MiniSensor, TW microsystems)

Quelle: Schaltplan (EasyEDA, gezeichnet von michael.tanner, 2024-03-03, Rev 1.0),
[`MiniSensor Schema.pdf`](./MiniSensor%20Schema.pdf). Vollständige PCB-Dateien
(Gerbers, PCB-Layer-Plots, BOM, Gehäuse) liegen ebenfalls in diesem Ordner.

Controller ist ein **ESP-12F** (ESP8266), im Gegensatz zu den ESP32-Boards
der übrigen OmniLink-Projekte in diesem Repo.

### Spannungsversorgung

- **J4** DC 12 V Eingang → Verpolschutzdiode (D1, S1ML R2) + TVS-Schutz
  (D2, SMBJ15A) + Feinsicherung (F1, RXEF020) → **U2 = NCP718ASN-3.3V**
  (Buck-Regler) → 3,3 V für ESP-12F und Peripherie
- Eingangs-/Ausgangs-Filterung über L1/L2 (100 µH) und C3–C7

### 1-Wire-Strecke

- Datenleitung an **GPIO2** des ESP-12F, Pull-up **R9 (4k7)** nach 3,3 V
- Anschluss über **J2** (JST-XH 3-polig, direkt auf der Platine) und
  **J5** (3-poliger Breakout-Header für externe Verlängerung/Sensorplatzierung)
- Bewusst dasselbe GPIO wie im alten `poolcontrol-pool-sensor.yaml`
  (ESP8266, `GPIO02`) — dort ebenfalls 1-Wire auf GPIO2, allerdings andere
  Hardware/Boardvariante (`esp01_1m` statt `esp12e`)

### I²C-Strecke (vorhanden, ungenutzt)

- **SDA = GPIO4**, **SCL = GPIO5**, je Pull-up **R10/R11 (4k7)** nach 3,3 V
- Anschluss über **J3** (JST-XH 4-polig)
- Kein Sensor in dieser Version angeschlossen — Bus ist im YAML bereits
  konfiguriert (`i2c: scan: true`), damit sich künftige I²C-Sensoren ohne
  Anpassung des YAML-Grundgerüsts ergänzen lassen

### Boot/Reset

- **KEY1 (RESET)**: klassischer Hardware-Reset (an EN/RST des Moduls),
  ESPHome-seitig ohne Bedeutung
- **KEY2 (BOOT)** an **GPIO0**, Pull-up **R8 (10K)** nach 3,3 V: muss beim
  Erstflash über den seriellen Bootloader gedrückt gehalten werden
  (Standard-ESP8266-Verfahren), im Normalbetrieb ohne Funktion

### Status-LED

- **LED1 „STATUS"** (rot) hängt über **R7 (2K2, Vorwiderstand)** an
  **GPIO13** des ESP-12F — **GPIO-gesteuert**, keine reine Power-LED. Im
  YAML analog zur STATUS-LED bei omnilink-poolboy als Blinkfrequenz-Anzeige
  des ESPHome-/API-Verbindungsstatus umgesetzt (langsam = keine
  Verbindung, schnell = API verbunden), siehe Abschnitt 7.

### Erstflash

- **J1 FTDI-Header** (6-polig): einziger Weg für den Erstflash, da die
  Platine **keinen** Onboard-USB-Anschluss hat. Danach läuft alles per OTA.

---

## 3. Konzeptionell übernommener 1-Wire-Teil (aus altem YAML, Beispiel-Anwendung)

Aus `poolcontrol-pool-sensor.yaml` (andere Hardware) wurde nur das
**Funktionsprinzip** übernommen, nicht 1:1 der Code (andere Plattform:
ESP8266 `esp01_1m` vs. hier `esp12e`, andere DS18B20-Adresse):

| Parameter | Altes YAML | mini-sensor.yaml (Beispiel) |
|---|---|---|
| 1-Wire-GPIO | GPIO2 | GPIO2 (gleiches Pin-Layout, Zufall der Hardware) |
| Sensor-Adresse | fest `0xf4355fd4456b3228` | keine feste Adresse — einziger Sensor am Bus, automatische Erkennung |
| update_interval | 1 s | 30 s (an omnilink-poolboy-Rhythmus angeglichen) |
| Glättung | `sliding_window_moving_average` (Fenster 10, alle 10 gesendet) | unverändert übernommen |
| Auflösung | Standard (12 Bit implizit) | explizit `resolution: 12` |

---

## 4. Getroffene Entscheidungen

| # | Frage | Antwort |
|---|---|---|
| 1 | Hardware-Umfang | Platine ist universell (1-Wire **und** I²C nutzbar); Beispiel-YAML nutzt nur 1-Wire, I²C-Bus ist aktiv, aber ohne Sensor |
| 2 | Ordnername | `mini_sensor` (Bestandsname beibehalten, kein Umbenennen ins OmniLink-Schema) |
| 3 | 1-Wire-GPIO | GPIO2 (vom Nutzer bestätigt) |
| 4 | DS18B20-Adresse | keine feste Adresse im YAML — Platine trägt genau einen 1-Wire-Sensor |
| 5 | Node-Name / Secrets | generisch `mini-sensor` (nicht anwendungsspezifisch benannt); eigene `mini_sensor_*`-Keys in `secrets.yaml` |
| 6 | Board | `esp8266: board: esp12e` (ESP-12F-Modul) |
| 7 | Erstflash | nur per FTDI-Adapter an J1 möglich (kein Onboard-USB) |

---

## 5. Ergebnis: ESPHome-Konfiguration (Beispiel-YAML)

Datei: [`mini-sensor.yaml`](./mini-sensor.yaml). Dient als **Vorlage** für
weitere MiniSensor-Projekte — Konnektivität/Diagnose-Block übernehmen,
`one_wire`/`sensor: dallas_temp` durch den jeweils passenden 1-Wire- oder
I²C-Sensor ersetzen bzw. ergänzen.

Enthält:

- **esp8266**: `board: esp12e`
- **Konnektivität**: WiFi (aus `secrets.yaml`), AP-Fallback, captive_portal,
  Home-Assistant-API (Verschlüsselung), OTA, web_server (Auth `digest`,
  Zugangsdaten aus `secrets.yaml`)
- **one_wire**: `GPIO2`
- **i2c**: `GPIO4`/`GPIO5`, `scan: true`, aktuell ohne Sensor
- **sensor**: `dallas_temp` — Temperatur (Beispiel: Pool-Wasser), 30 s Update, geglättet
- **STATUS-LED** (`GPIO13`): Blinkfrequenz-Anzeige des ESPHome-/API-Verbindungsstatus, siehe Abschnitt 7
- **Diagnose**: über `common/diagnostics.yaml` (WiFi, Heap, Uptime, Version,
  Restart-Buttons) sowie API-Verbindungsstatus

### Secrets

Aus `secrets.yaml` erwartet (wie bisher):
`wifi_ssid`, `wifi_password`, `web_server_username`, `web_server_password`.

Neu für dieses Projekt: `mini_sensor_api_key`, `mini_sensor_ota_key`,
`mini_sensor_fallback_ap_ssid`, `mini_sensor_fallback_ap_password`
(frisch generiert, lokal in `secrets.yaml` hinterlegt).

---

## 6. Offene Hinweise / nächste Schritte

- **DS18B20-Adresse fixieren:** Beim ersten Flash im Boot-Log die erkannte
  1-Wire-Adresse notieren und optional fest im YAML eintragen, falls später
  ein zweiter 1-Wire-Sensor am selben Bus ergänzt werden soll (dann ist eine
  feste Adresse zwingend, da sonst nicht mehr eindeutig).
- **Geplante Erweiterungen** (I²C-Sensor): siehe [BACKLOG.md](./BACKLOG.md).

---

## 7. Status-Visualisierung (STATUS-LED, `GPIO13`)

| # | Frage | Antwort |
|---|---|---|
| 1 | Anschluss | LED1 (rot) über Vorwiderstand R7 (2K2) direkt an `GPIO13` — **GPIO-gesteuert**, keine reine Power-LED (ursprünglich fälschlich so dokumentiert, korrigiert). |
| 2 | Umsetzung | Endlos-`script` (`status_led_run`, per `on_boot` einmalig gestartet) mit `while: true`-Loop, das bei jedem Durchlauf die `api.connected`-Bedingung prüft und die passende An/Aus-Sequenz auf einen `output: platform: gpio` (GPIO13) fährt — identisches Muster wie die STATUS-LED bei omnilink-poolboy. |
| 3 | Zustände | Langsam (100 ms an / 1200 ms aus), solange die API-/WLAN-Verbindung noch nicht steht; schnell (100 ms an / 600 ms aus), sobald die API verbunden ist. |
| 4 | HA-Sichtbarkeit | Reine Hardware-Statusanzeige ohne eigene Home-Assistant-Entität. |

---

*Hardware: MiniSensor Rev 1.0 · MCU: ESP-12F (ESP8266) ·
Ziel-ESPHome: 2026.7.x*
