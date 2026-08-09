# FilaHygro (Filament-Lagerbehälter-Sensor)

![Version](https://img.shields.io/badge/version-0.1.0-blue)
[![ESPHome](https://img.shields.io/badge/ESPHome-Ready-03a9f4?logo=esphome&logoColor=white)](https://esphome.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**FilaHygro** ist eine eigenentwickelte, akkubetriebene Sensorplatine
(TW microsystems) für Filament-Lagerbehälter. Sie misst Temperatur und
Luftfeuchtigkeit im Behälter und meldet beides per **MQTT**. Das ist vor
allem für **hygroskopische Filamente** (ABS, Nylon/PA, PVA, PC, …) relevant —
sie nehmen bei zu hoher Luftfeuchtigkeit Wasser auf, was zu Blasenbildung,
Knistern und schlechterer Druckqualität führt.

Das Gerät läuft auf einem **18650-Akku** (per Micro-USB/TP4056 nachladbar).
Die Firmware ist konsequent stromsparend ausgeführt: aufwachen, messen,
per MQTT senden, wieder in **Deep-Sleep** — kein Dauerbetrieb, keine
Home-Assistant-API, kein Webserver.

> ⚠️ **Bekanntes Problem:** Die gemeldete Akku-Spannung/SoC ist aktuell nicht
> verlässlich (zeigt dauerhaft ~4V/100%), Ursache noch offen. Siehe
> [BACKLOG.md](./BACKLOG.md).

---

## Haftungsausschluss (Disclaimer)

⚠️ **WICHTIGER HINWEIS: VERWENDUNG AUF EIGENE GEFAHR!** ⚠️

Dieses Projekt beschreibt ein privates Bastelprojekt. Die Nutzung, der Nachbau
sowie das Einspielen des bereitgestellten Codes erfolgen ausdrücklich auf
**eigene Gefahr und eigenes Risiko**. Es wird keinerlei Haftung für Schäden an
Geräten (inkl. Lithium-Akku) oder für Folgeschäden übernommen. Arbeiten an der
Elektrik sowie der Umgang mit Lithium-Akkus (Laden, Lagerung) erfolgen in
eigener Verantwortung.

---

## 1. Funktion

FilaHygro misst zyklisch Temperatur und relative Luftfeuchtigkeit im
Filament-Lagerbehälter sowie die eigene Akkuspannung, sendet die Werte als
JSON per MQTT und legt sich danach schlafen, um den 18650-Akku zu schonen.

* **Messwerte:** Temperatur (°C), Luftfeuchtigkeit (% rF), Akkuspannung (V),
  Akku-Ladezustand/SoC (%, aktuell fehlerhaft — siehe BACKLOG)
* **Konnektivität:** WiFi + MQTT (JSON-Payload, kein Discovery, kein HA-API,
  kein Webserver); OTA-Updates sind als per MQTT getriggerter
  Dauerbetrieb-Modus geplant, aktuell noch nicht umgesetzt (siehe
  [BACKLOG.md](./BACKLOG.md)) — bis dahin Firmware-Updates nur per FTDI
* **Stromsparen:** Deep-Sleep zwischen den Messzyklen; der
  Akku-Spannungsteiler wird nur während der Messung eingeschaltet

---

## 2. Hardware & Pinout (FilaHygro, ESP-12F)

| Komponente | Detail |
| :--- | :--- |
| Platine | FilaHygro (TW microsystems, Rev 2) |
| MCU | ESP-12F (ESP8266) |
| Akku | 18650 (Halter B1), Laderegler TP4056 (U4) per Micro-USB |
| Spannungsregler | NCP718ASN-3.3V (U3, LDO) aus `Vbat` |
| I²C-Sensor (U2) | SHT31-D (0x44, bestückt) **oder** HDC1080 (0x40), Auswahl per Lötbrücke SB1 |
| Erstflash | J1 FTDI-Header (6-pol.), kein Onboard-USB für Programmierung |

| Funktion | GPIO | Beschreibung |
| :--- | :---: | :--- |
| **I²C SDA** | `GPIO4` | zum Sensor U2 |
| **I²C SCL** | `GPIO5` | zum Sensor U2 |
| **Vbat-ADC** | `A0` | über Spannungsteiler R12(330K)/R13(100K), Faktor `4.0218` |
| **Vbat-Teiler-Schalter** | `GPIO15` | schaltet Q1 (SI2302DS), aktiviert den Spannungsteiler (R12/R13, Pull-down R7 10K) nur während der Messung — Verdrahtung bestätigt korrekt |

> ⚠️ **Akku-SoC-Bug:** Die Spannungsmessung liefert unabhängig vom
> Ladezustand immer ~4V/100%. `GPIO15` für `vbat_switch` ist bestätigt
> korrekt verdrahtet — die eigentliche Ursache ist noch offen. Details im
> [Design-Dokument, Abschnitt 2](./Design_filahygro.md#2-hardware-analyse-filahygro-tw-microsystems)
> sowie [BACKLOG.md](./BACKLOG.md).

---

## 3. MQTT

| Parameter | Wert |
| :--- | :--- |
| Broker/User/Passwort | aus `secrets.yaml` (`filahygro_mqtt_*`) |
| Client-ID | `FilaBox` |
| Topic | `FilaBox/data` |
| Discovery | aus — reines JSON-Payload, keine automatischen HA-Entities |
| Payload | `{"t": Temp °C, "h": rF %, "v": Vbat V, "soc": SoC %}` |
| Ablauf | Boot → Vbat-Teiler an → auf MQTT warten (max. 15s) → 1s Sensor-Settle → JSON senden → 500ms → Vbat-Teiler aus → Deep-Sleep |
| Sleep-Dauer | 300s (Testwert, siehe [BACKLOG.md](./BACKLOG.md)) |

---

## 4. Inbetriebnahme

1. Zentrale `secrets.yaml` im **Repo-Root** anlegen (siehe
   [`secrets.yaml.example`](../secrets.yaml.example)) und mindestens
   `wifi_ssid`, `wifi_password` sowie die `filahygro_mqtt_*`-Keys eintragen.
2. Erstflash per **FTDI-Adapter** an J1 — kompiliert wird **vom Repo-Root
   aus**:
   ```bash
   esphome run filahygro/filabox1.yaml
   ```
3. OTA-Updates sind als per MQTT getriggerter Dauerbetrieb-Modus geplant
   (siehe [BACKLOG.md](./BACKLOG.md)), aktuell aber noch nicht umgesetzt —
   bis dahin läuft jedes weitere Update ebenfalls per FTDI-Adapter.

Es gibt **keinen** lokalen Webserver und **keine** Home-Assistant-API — die
Werte kommen ausschliesslich per MQTT (z. B. über eine
MQTT-Sensor-Konfiguration in Home Assistant, passend zum Topic `FilaBox/data`).

---

## 5. Weitere Details

Die vollständige Hardware-Analyse, der bekannte Akku-SoC-Bug und alle
getroffenen Entscheidungen sind im
[Design-Dokument](./Design_filahygro.md) dokumentiert.
