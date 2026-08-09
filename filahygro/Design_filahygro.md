# FilaHygro — Projektzusammenfassung

**FilaHygro** ist eine eigenentwickelte, akkubetriebene Sensorplatine
(TW microsystems) zur Überwachung von Temperatur und Luftfeuchtigkeit in
Filament-Lagerbehältern. Hygroskopische Filamente (ABS, Nylon/PA, PVA, …)
nehmen bei zu hoher Luftfeuchtigkeit Wasser auf und verlieren an Druckqualität
— FilaHygro macht den Zustand im Behälter messbar. Das Gerät läuft auf einem
18650-Akku, misst zyklisch, sendet die Werte per **MQTT** und legt sich danach
in **Deep-Sleep**, um die Akkulaufzeit zu maximieren.

---

## 1. Aufgabe

Auf der eigenentwickelten Hardware (Schaltplan `FilaHygro`, Rev 2) soll
ESPHome laufen, das Temperatur, Luftfeuchtigkeit und Akkuzustand periodisch
misst und per MQTT an den lokalen Broker sendet. Im Gegensatz zu den übrigen
Projekten in diesem Repo (omnilink-poolboy, mini_sensor) ist FilaHygro
**akkubetrieben ohne Netzteil** — die Firmware ist deshalb bewusst auf
minimalen Stromverbrauch ausgelegt (kein Dauerbetrieb, keine HA-API, kein
Webserver): aufwachen, messen, senden, schlafen.

Funktionsumfang: Temperatur-/Feuchtigkeitsmessung und Akkuüberwachung,
Übermittlung per MQTT im Deep-Sleep-Zyklus. Die stromsparende
MQTT/Deep-Sleep-Architektur ist bewusst beibehalten — eine Umstellung auf das
HA-API/Diagnostics-Muster der netzbetriebenen Geräte (omnilink-poolboy,
mini_sensor) würde die Akkulaufzeit spürbar verkürzen.

---

## 2. Hardware-Analyse (FilaHygro, TW microsystems)

Quelle: Schaltplan (EasyEDA, gezeichnet von roger_5073, 2021-03-06, Rev 2),
[`Schematic_FilaHygro_2026-08-05.pdf`](./Schematic_FilaHygro_2026-08-05.pdf).
PCB-Layout, Gerbers und BOM liegen ebenfalls in diesem Ordner. Das Design
folgt eigenen Konventionen (kein 1.x-Nummerierungsschema, keine STATUS-LED).

Controller ist ein **ESP-12F** (ESP8266), direkt auf der Platine verlötet.

### Spannungsversorgung / Akku

- **B1 = BLOSSM 18650-PC2**: Akkuhalter für eine 18650-Zelle
- **U4 = TP4056** (Laderegler, Micro-USB): lädt den Akku, `J2 "Isens"` ist der
  Programmier-Header für den Ladestrom
- **U3 = NCP718ASN-3.3V** (LDO-Regler): erzeugt aus `Vbat` die 3,3 V für
  ESP-12F und Sensor
- **Akku-Spannungsmessung**: Spannungsteiler **R12 (330K) / R13 (100K)** von
  `Vbat` nach GND, Abgriff über `ADC` → ESP-12F `A0`. Faktor im YAML:
  `multiply: 4.0218` (≈ (330K+100K)/100K, mit Korrektur für den ADC-eigenen
  Spannungsteiler des ESP-12F)
- **Q1 (SI2302DS)**: schaltet den R12/R13-Teiler über das Gate-Netz `M_BAT`
  (Gate-Widerstand R14, 1K) — der Teiler zieht nur während der Messung Strom,
  nicht durchgehend im Deep-Sleep. Ansteuerung über **GPIO15** (`R7`, 10K,
  ist ein Pull-**down** an diesem Netz) — bestätigt korrekt verdrahtet.

### I²C-Sensor (U2)

- **SDA = GPIO4**, **SCL = GPIO5**, direkt am ESP-12F
- Sockel ist für **zwei** pinkompatible Sensoren ausgelegt, Auswahl über
  Lötbrücke **SB1**:
  - **SHT31-D** (Adafruit-Breakout, Adresse `0x44`) — auf den vorhandenen
    Boards bestückt, aktueller Default im YAML
  - **HDC1080** (Adresse `0x40`) — Alternative laut Schema, aktuell auf
    keinem im Feld befindlichen Board bestückt (siehe [BACKLOG.md](./BACKLOG.md))

### Erstflash

- **J1 FTDI-Header** (6-polig): einziger Weg für den Erstflash, kein
  Onboard-USB für die Programmierung (nur der TP4056-Micro-USB zum Laden).
  Danach läuft alles per **MQTT/WiFi**. Für Firmware-Updates ist ein per MQTT
  getriggerter Dauerbetrieb-Modus vorgesehen: Umschalten auf Dauerbetrieb
  (Deep-Sleep-Zyklus aussetzen) → OTA durchführen → zurückschalten. Dieser
  Mechanismus ist im aktuellen `filabox1.yaml` noch **nicht implementiert**
  (kein `ota:`-/`api:`-Block, kein MQTT-Subscribe dafür) — siehe
  [BACKLOG.md](./BACKLOG.md). Bis dahin läuft jedes Update per FTDI.
- **KEY1 (RESET)** / **KEY2 (BOOT)**: Standard-ESP8266-Tasten für
  Reset/Bootloader-Modus, ESPHome-seitig ohne Bedeutung

### Bekanntes Problem: Akku-SoC zeigt dauerhaft ~4V/100%

In der Praxis zeigt die Akku-SoC-Berechnung dauerhaft ~4V/100%, unabhängig
vom tatsächlichen Ladezustand des Akkus.

**GPIO15 für `vbat_switch` (steuert Q1 über das Gate-Netz `M_BAT`) ist
bestätigt korrekt verdrahtet** — R7 (10K) an diesem Netz ist ein Pull-down,
kein Pull-up. Die Verdrahtung ist damit als Fehlerursache ausgeschlossen. Die
eigentliche Ursache ist noch offen und muss weiter untersucht werden. Siehe
[BACKLOG.md](./BACKLOG.md).

---

## 3. Bestehender MQTT-Ablauf (aus `filabox1.yaml`)

| Parameter | Wert |
|---|---|
| Broker | `filahygro_mqtt_broker` (Secret) |
| Client-ID | `FilaBox` |
| Topic | `FilaBox/data` |
| Discovery | aus (`discovery: false`) — keine automatischen HA-Entities, reines JSON-Payload |
| Payload | `{"t": <Temp °C, 1 Dez.>, "h": <rF %, 1 Dez.>, "v": <Vbat V, 2 Dez.>, "soc": <SoC %, int>}` |
| Ablauf | Boot → Vbat-Teiler aktivieren → auf MQTT-Verbindung warten (max. 15s) → 1s warten (Sensor-Settle) → JSON publizieren → 500ms warten (Paket raus) → Vbat-Teiler deaktivieren → Deep-Sleep |
| Sleep-Dauer | 300s (Testwert, siehe [BACKLOG.md](./BACKLOG.md)) |

Die SoC-Berechnung (`soc`-Template-Sensor) rechnet die gemessene Vbat-Spannung
über eine Lookup-Tabelle (4.20V = 100% … <3.06V = 0%) auf einen Prozentwert
um — funktioniert erst korrekt, sobald der SoC-Bug (Abschnitt 2) behoben ist.

---

## 4. Getroffene Entscheidungen

| # | Frage | Antwort |
|---|---|---|
| 1 | Architektur | MQTT + Deep-Sleep (Akkubetrieb); kein HA-API/Webserver/Diagnostics wie bei den netzbetriebenen Geräten |
| 2 | GPIO Vbat-Schalter (`M_BAT`) | GPIO15 bestätigt korrekt (R7 ist Pull-down); SoC-Bug-Ursache separat offen, siehe Abschnitt 2 und BACKLOG |
| 3 | Aktuell bestückter Sensor | SHT31-D (0x44) auf allen vorhandenen Boards; HDC1080-Support bleibt Backlog-Punkt |
| 4 | Board-Typ (ESPHome) | `esp8266: board: esp12e` (entspricht dem tatsächlich verbauten ESP-12F; vorher fälschlich `d1_mini`, ein Wemos-Dev-Board-Profil, das hier physisch nicht vorliegt) |
| 5 | Ordnername / Node-Name | `filahygro` (Ordner) bzw. `filabox1` (Node-Name/`client_id`) unverändert beibehalten |
| 6 | OTA | Per MQTT getriggerter Dauerbetrieb-Modus vorgesehen (Umschalten → OTA → zurück), im Code noch nicht umgesetzt (Backlog-Punkt). Erstflash weiterhin nur per FTDI (J1) |

---

## 5. Ergebnis: ESPHome-Konfiguration

Datei: [`filabox1.yaml`](./filabox1.yaml).

Enthält:

- **esp8266**: `board: esp12e`
- **Konnektivität**: WiFi (aus `secrets.yaml`), **kein** HA-API/Webserver
  — stattdessen MQTT (Broker/User/Passwort aus `secrets.yaml`); OTA per
  MQTT-getriggertem Dauerbetrieb-Modus ist geplant, aber noch nicht
  implementiert (siehe Abschnitt 4/6, [BACKLOG.md](./BACKLOG.md))
- **i2c**: `GPIO4`/`GPIO5`, SHT31-D auf `0x44`
- **output**: `vbat_switch` (GPIO15, siehe Abschnitt 2) schaltet den
  Akku-Spannungsteiler
- **sensor**: Temperatur, Luftfeuchtigkeit (SHT31-D), Akkuspannung (ADC),
  Akku-SoC (Template-Lambda mit Lookup-Tabelle)
- **script `publish_and_sleep`**: MQTT-Publish-and-Sleep-Ablauf (siehe
  Abschnitt 3), ausgelöst über `on_boot`
- **deep_sleep**: 300s (Testwert)

### Secrets

Aus `secrets.yaml` erwartet (wie bisher): `wifi_ssid`, `wifi_password`.

Neu für dieses Projekt (vorher inline im YAML): `filahygro_mqtt_broker`,
`filahygro_mqtt_user`, `filahygro_mqtt_password`.

---

## 6. Offene Hinweise / nächste Schritte

Siehe [BACKLOG.md](./BACKLOG.md) — insbesondere der Akku-SoC-Bug (Ursache
offen), der noch nicht implementierte MQTT-OTA-Modus und die
Deep-Sleep-Produktivdauer sind vor dem nächsten Feld-Rollout zu klären.

---

*Hardware: FilaHygro Rev 2 · MCU: ESP-12F (ESP8266) ·
Ziel-ESPHome: 2026.7.x*
