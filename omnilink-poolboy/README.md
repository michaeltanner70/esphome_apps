# omnilink-poolboy – PoolBoy Modbus-Auslesung

![Version](https://img.shields.io/badge/version-0.3.0-blue)
[![ESPHome](https://img.shields.io/badge/ESPHome-Ready-03a9f4?logo=esphome&logoColor=white)](https://esphome.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Dieses ESPHome-Projekt läuft auf der eigenentwickelten Platine **OmniLink-C6** (Seeed Studio XIAO **ESP32-C6**) und liest ein **PoolBoy-Elektrolysegerät** per **Modbus RTU (RS485)** aus. Die Wasser- und Statuswerte werden über die native Home-Assistant-API bereitgestellt.

> **Umfang dieser Version:** Modbus sowie die STATUS-/MSG-Status-LEDs. I²C, 1-Wire und die HAT-Eingänge sind auf der Platine vorhanden, aber noch nicht implementiert (siehe [Design-Dokument](./Design_omnilink-poolboy.md)).

---

## Haftungsausschluss (Disclaimer)

⚠️ **WICHTIGER HINWEIS: VERWENDUNG AUF EIGENE GEFAHR!** ⚠️

Dieses Projekt beschreibt ein privates Bastelprojekt. Die Nutzung, der Nachbau sowie das Einspielen des bereitgestellten Codes erfolgen ausdrücklich auf **eigene Gefahr und eigenes Risiko**. Es wird keinerlei Haftung für Schäden an Geräten, an der Pooltechnik oder für Folgeschäden übernommen. Arbeiten an der Elektrik dürfen nur von qualifiziertem Fachpersonal durchgeführt werden.

---

## 1. Funktion

Der OmniLink-PoolBoy liest die Mess- und Statusregister des PoolBoy-Elektrolysegeräts zyklisch (alle 30 s) über Modbus RTU aus und stellt sie als Entitäten in Home Assistant bereit. Es findet (in dieser Version) **keine** aktive Steuerung statt – das Gerät ist rein lesend.

* **Messwerte:** Ionisation (mA), Hydrolyse (%), pH, Redox (mV)
* **Statusbits:** pH-Minus-Pumpe, Ionisierung (On-Target / Low / Zeit erreicht), Redox (On-Target / Low / Flow)
* **Diagnose:** über das gemeinsame [`common/diagnostics.yaml`](../common) Package (WLAN, Speicher, Uptime, Version, Restart-Buttons) sowie der API-Verbindungsstatus
* **Konnektivität:** OTA-Updates, lokaler Webserver (Port 80), AP-Fallback
* **Status-LEDs:** blaue STATUS-LED zeigt den ESPHome-/API-Verbindungsstatus per Blinkfrequenz, MSG-LED (WS2812) zeigt die Wasserwerte (pH/Redox) als Farbe und flackert bei jedem Modbus-Poll (siehe [Abschnitt 6](#6-status-anzeige-leds))

---

## 2. Hardware & Pinout (XIAO ESP32-C6)

| Komponente | Detail |
| :--- | :--- |
| Platine | [OmniLink-C6](../omnilink-c6) (TW microsystems, Rev 2.0) |
| MCU | Seeed Studio XIAO ESP32-C6 |
| RS485-Transceiver | SN65HVD75DR (Half-Duplex, DE+RE# = „DIR") |
| Bus-Anschluss | Schraubklemme J7 (A/B), 120 Ω Terminierung, Fail-Safe-Bias |

| Funktion | XIAO-Pin | Interner GPIO | Beschreibung |
| :--- | :---: | :---: | :--- |
| **RS485 TX (DI)** | D6 | `GPIO16` | Modbus TX zum SN65HVD75 |
| **RS485 RX (RO)** | D7 | `GPIO17` | Modbus RX vom SN65HVD75 |
| **RS485 DIR (DE+RE#)** | D2 | `GPIO2` | Richtungsumschaltung (`flow_control_pin`, high = senden) |
| **STATUS-LED (blau)** | D0 | `GPIO0` | diskrete LED, zeigt ESPHome-/API-Verbindungsstatus (siehe [Abschnitt 6](#6-status-anzeige-leds)) |
| **MSG-LED (WS2812B)** | D3 | `GPIO21` | adressierbare LED, zeigt Wasserwerte-Farbe + Kommunikations-Flackern (teilt sich die Leitung mit einer diskreten grünen LED, siehe [Abschnitt 6](#6-status-anzeige-leds)) |

> **Hinweis:** I²C (J6), 1-Wire (J5) und die HAT-Eingänge (J1) sind hardwareseitig vorhanden, aber in dieser Version noch nicht in der Firmware aktiviert.

---

## 3. Modbus-Parameter

| Parameter | Wert |
| :--- | :--- |
| Protokoll | Modbus RTU, 19200 8N1 |
| Slave-Adresse | `0x01` |
| Registertyp | Input-Register (FC04) |
| update_interval | 30 s |
| command_throttle / send_wait / turnaround | 500 ms / 500 ms / 100 ms |

### Registersatz

| Entität | Register | Typ / Dekodierung | Einheit / Class |
| :--- | :---: | :--- | :--- |
| 1.0 Ionisation | `0x0100` | U_WORD | mA, current |
| 1.1 Hydrolyse | `0x0101` | U_WORD × 0,1 | %, acc 0 |
| 1.2 pH | `0x0102` | U_WORD × 0,01 | ph, acc 2 |
| 1.3 Redox | `0x0103` | U_WORD | mV, voltage |
| 1.4 pH Status | `0x0107` | bitmask `0x000F` | numerisch |
| 1.5 pH Minus Pumpe | `0x0107` | bit `0x0800` | binary |
| 1.6 Ionisierung On Target / Low / Zeit erreicht | `0x010C` | bits `0x0001` / `0x0002` / `0x0008` | binary |
| 1.7 Redox On Target / Low / Flow | `0x010D` | bits `0x0001` / `0x0002` / `0x0008` | binary |

---

## 4. Inbetriebnahme

1. Zentrale `secrets.yaml` im **Repo-Root** anlegen (siehe [`secrets.yaml.example`](../secrets.yaml.example)) und mindestens `wifi_ssid`, `wifi_password` sowie die `poolboy_*`-Keys eintragen.
2. Erstflash per USB-C – kompiliert wird **vom Repo-Root aus** (wegen `!include common/...`):
   ```bash
   esphome run omnilink-poolboy/omnilink-poolboy.yaml
   ```
3. Danach laufen Updates per **OTA** über das Netzwerk.

Ein lokaler **Webserver** auf Port 80 zeigt alle Werte auch unabhängig von Home Assistant an.

---

## 5. Weitere Details

Die vollständige Hardware-Analyse, der Registersatz und alle getroffenen Entscheidungen sind im [Design-Dokument](./Design_omnilink-poolboy.md) dokumentiert.

---

## 6. Status-Anzeige (LEDs)

Beide LEDs sind reine Hardware-Statusanzeigen ohne eigene Home-Assistant-Entität.

### STATUS-LED (blau, diskret, `GPIO0`)

Zeigt den ESPHome-/API-Verbindungsstatus per Blinkfrequenz (jeweils 100 ms an):

| Zustand | Takt |
| :--- | :--- |
| ESP läuft, API-/WLAN-Verbindung steht noch nicht | langsam: 100 ms an / 1200 ms aus |
| API verbunden | schnell: 100 ms an / 600 ms aus |

Die Off-Zeiten sind bewusst länger als das MSG-Rot-Blinken (500 ms an/aus), damit sich die blaue LED optisch klar davon abhebt.

### MSG-LED (WS2812B, `GPIO21`)

Zeigt die Wasserwerte als gedimmte Farbe (`msg_led_brightness = 0.5`) und flackert kurz bei jeder Modbus-Kommunikation. Teilt sich die Datenleitung mit einer diskreten grünen LED — ein Leitungstest hat bestätigt, dass ein langer Digital-High-Pegel die WS2812 nicht stört.

| Zustand | Anzeige |
| :--- | :--- |
| Seit mehr als `msg_led_stale_timeout_ms` (45 s) kein gültiger pH-/Redox-Wert (Start **oder** Kommunikations-Unterbruch) | blinkt **rot**, 500 ms an / 500 ms aus |
| pH > 7.1 und < 7.3 **und** Redox > 650 mV | konstant **grün** |
| pH < 6.9 **oder** > 7.4 **oder** Redox < 600 mV | konstant **rot** |
| alle übrigen Werte (Übergangs-/Warnbereich) | konstant **gelb** |
| bei jedem Modbus-Poll-Zyklus (ausgelöst über „1.0 Ionisation") | flackert 3× kurz aus (je 50 ms aus / 50 ms Farbe wiederhergestellt), danach steht wieder die aktuelle Wasserwerte-Farbe |

Die Grenzwerte lassen bewusst kleine Lücken (z. B. pH exakt 7.4): diese fallen auf **gelb** als sicherer Zwischenzustand. Die Daten-Aktualität wird bei jedem Blink-Zyklus (alle 500 ms) neu geprüft (`msg_led_monitor`, Zeitstempel der letzten Aktualisierung) — ein späterer Kommunikationsausfall wird also genauso erkannt wie die Startphase, mit demselben Mechanismus.
