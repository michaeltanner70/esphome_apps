# MiniSensor (universelle I²C-/1-Wire-Sensor-Platine)

![Version](https://img.shields.io/badge/version-0.1.0-blue)
[![ESPHome](https://img.shields.io/badge/ESPHome-Ready-03a9f4?logo=esphome&logoColor=white)](https://esphome.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**MiniSensor** ist eine eigenentwickelte, universelle Trägerplatine (TW microsystems, ESP-12F/ESP8266) für kleine Mess-/Sensoraufgaben. Sie stellt sowohl einen **1-Wire-** als auch einen **I²C-Anschluss** bereit — welcher Sensor tatsächlich verbaut wird, entscheidet die jeweilige Anwendung. Dieser Ordner enthält die Hardware-Unterlagen der Platine sowie **ein Beispiel-YAML** ([`mini-sensor.yaml`](./mini-sensor.yaml)), das die Platine mit einem **1-Wire-Temperatursensor (DS18B20)** für die Pool-Wassertemperatur nutzt.

> **Universell, nicht projektspezifisch:** Die Platine selbst ist nicht an einen Anwendungsfall gebunden. Für ein neues Projekt mit MiniSensor-Hardware wird i. d. R. eine Kopie/Variante von `mini-sensor.yaml` erstellt, die statt (oder zusätzlich zu) `one_wire`/`dallas_temp` den passenden I²C- oder 1-Wire-Sensor konfiguriert. Details zum Vorgehen siehe [Design-Dokument](./Design_mini-sensor.md).

---

## Haftungsausschluss (Disclaimer)

⚠️ **WICHTIGER HINWEIS: VERWENDUNG AUF EIGENE GEFAHR!** ⚠️

Dieses Projekt beschreibt ein privates Bastelprojekt. Die Nutzung, der Nachbau sowie das Einspielen des bereitgestellten Codes erfolgen ausdrücklich auf **eigene Gefahr und eigenes Risiko**. Es wird keinerlei Haftung für Schäden an Geräten oder für Folgeschäden übernommen. Arbeiten an der Elektrik dürfen nur von qualifiziertem Fachpersonal durchgeführt werden.

---

## 1. Hardware & Pinout (MiniSensor, ESP-12F)

| Komponente | Detail |
| :--- | :--- |
| Platine | MiniSensor (TW microsystems, Rev 1.0) |
| MCU | ESP-12F (ESP8266) |
| Versorgung | DC 12 V (J4) → Verpolschutz (D1) + TVS (D2) + Feinsicherung (F1) → NCP718ASN-3.3V (U2, Buck) → 3,3 V |
| 1-Wire-Anschluss | J2 (JST-XH 3-pol.) + J5 (Breakout), Pull-up R9 4k7 |
| I²C-Anschluss | J3 (JST-XH 4-pol.), Pull-ups R10/R11 4k7 |
| Erstflash | J1 FTDI-Header (6-pol.), kein Onboard-USB |

| Funktion | GPIO | Beschreibung |
| :--- | :---: | :--- |
| **1-Wire** | `GPIO2` | Datenleitung J2/J5, Pull-up R9 4k7 — für DS18B20 & andere 1-Wire-Sensoren |
| **I²C SDA** | `GPIO4` | J3, Pull-up R10 4k7 |
| **I²C SCL** | `GPIO5` | J3, Pull-up R11 4k7 |
| **BOOT-Taste (KEY2)** | `GPIO0` | Pull-up R8 10K, nur für Erstflash/Bootmode relevant |
| **STATUS-LED (rot, LED1)** | `GPIO13` | Vorwiderstand R7 2K2, GPIO-gesteuert — zeigt den ESPHome-/API-Verbindungsstatus per Blinkfrequenz (siehe unten) |
| **RESET-Taste (KEY1)** | – | Hardware-Reset, nicht per ESPHome ansteuerbar |

Beide Busse (1-Wire und I²C) liegen auf eigenen, unabhängigen Pins und können **gleichzeitig** genutzt werden — z. B. ein DS18B20 an 1-Wire plus ein I²C-Luftdrucksensor auf derselben Platine, in derselben YAML.

### STATUS-LED (rot, `GPIO13`)

Zeigt den ESPHome-/API-Verbindungsstatus per Blinkfrequenz (jeweils 100 ms an), analog zur STATUS-LED bei omnilink-poolboy:

| Zustand | Takt |
| :--- | :--- |
| ESP läuft, API-/WLAN-Verbindung steht noch nicht | langsam: 100 ms an / 1200 ms aus |
| API verbunden | schnell: 100 ms an / 600 ms aus |

---

## 2. Beispielanwendung: Pool-Wassertemperatur (1-Wire)

Datei: [`mini-sensor.yaml`](./mini-sensor.yaml). Nutzt ausschliesslich den 1-Wire-Anschluss mit einem DS18B20; der I²C-Bus ist im YAML als Beispiel für weitere Anwendungen zwar aktiv (`i2c: scan: true`), aber ohne angeschlossenen Sensor.

| Parameter | Wert |
| :--- | :--- |
| Bus | `one_wire: platform: gpio`, `GPIO2` |
| Sensor | DS18B20, keine feste Adresse im YAML (einziger Sensor am Bus, wird automatisch erkannt) |
| update_interval | 30 s |
| Auflösung | 12 Bit |
| Glättung | `sliding_window_moving_average` (Fenster 10, alle 10 Messungen gesendet) |

* **Diagnose:** über das gemeinsame [`common/diagnostics.yaml`](../common) Package (WLAN, Speicher, Uptime, Version, Restart-Buttons) sowie der API-Verbindungsstatus
* **Konnektivität:** OTA-Updates, lokaler Webserver (Port 80), AP-Fallback

Für ein neues Projekt mit anderem Sensor (z. B. I²C) dient dieses YAML als Vorlage: Konnektivität/Diagnose-Block übernehmen, `one_wire`/`sensor: dallas_temp` durch die passende I²C-Sensor-Konfiguration ersetzen bzw. ergänzen.

---

## 3. Inbetriebnahme

1. Zentrale `secrets.yaml` im **Repo-Root** anlegen (siehe [`secrets.yaml.example`](../secrets.yaml.example)) und mindestens `wifi_ssid`, `wifi_password` sowie die `mini_sensor_*`-Keys eintragen.
2. Erstflash per **FTDI-Adapter** an J1 – kompiliert wird **vom Repo-Root aus** (wegen `!include common/...`):
   ```bash
   esphome run mini_sensor/mini-sensor.yaml
   ```
3. Danach laufen Updates per **OTA** über das Netzwerk.

Ein lokaler **Webserver** auf Port 80 zeigt den Messwert auch unabhängig von Home Assistant an.

---

## 4. Weitere Details

Die vollständige Hardware-Analyse, das Pin-Mapping für beide Busse und alle getroffenen Entscheidungen sind im [Design-Dokument](./Design_mini-sensor.md) dokumentiert.
