# OmniLink-PoolBoy — Projektzusammenfassung

Auslesen des PoolBoy-Elektrolysegeräts über Modbus RTU (RS485) und Übergabe der
Werte an Home Assistant, mit ESPHome auf der Platine **OmniLink-C6**.

---

## 1. Aufgabe

Auf der speziell entwickelten Hardware (Schaltplan `OmniLink-C6`) soll ESPHome
laufen, das über **Modbus** Wasser- und Statuswerte ausliest und an Home
Assistant sendet. Der Modbus-Teil (Register und deren Dekodierung) wird aus einem
bestehenden YAML einer **anderen** Hardware (`poolcontrol`, ESP32-S3) übernommen;
der Rest jenes YAMLs ist nicht relevant.

Vorgehen: zuerst Analyse, dann nach Klärung der offenen Punkte das vollständige
YAML. Umfang der ersten Version: **nur Modbus**.

---

## 2. Hardware-Analyse (OmniLink-C6, TW microsystems)

Quelle: Schaltplan (EasyEDA, gezeichnet von michael.tanner, 2026-05-10, Rev 1.0).
Vollständige PCB-Dateien (Schaltplan, Layout, Gerbers, BOM, Änderungshistorie
inkl. Rev 2.0) liegen in [`omnilink-c6/`](../omnilink-c6).

Wichtigster Punkt: Der Controller ist ein **Seeed Studio XIAO ESP32-C6** (U3) —
**nicht** der ESP32-S3 aus dem alten YAML. Die GPIO-Belegung ist daher komplett
anders und stammt aus dem Schaltplan, nicht aus dem alten File.

### RS485-Strecke

- Transceiver **U4 = SN65HVD75DR** (3,3 V, Half-Duplex)
- RE# (Pin 2) und DE (Pin 3) sind **zusammengelegt** auf eine einzige
  Richtungsleitung „DIR" → in ESPHome der `flow_control_pin`
- RO (Pin 1) → RX, DI (Pin 4) → TX
- 120 Ω-Terminierung (R15), Fail-Safe-Bias (R14/R16, 10 k), SM712-TVS-Schutz (D4)
- Bus-Anschluss über Schraubklemme **J7 (A/B)**

### Pin-Mapping (aus Schaltplan gelesen, vom Nutzer bestätigt)

| Funktion | XIAO-Pin | GPIO | Bemerkung |
|---|---|---|---|
| RS485 TX (DI) | D6 | GPIO16 | Modbus TX |
| RS485 RX (RO) | D7 | GPIO17 | Modbus RX |
| RS485 DIR (DE+RE#) | D2 | GPIO2 | flow_control_pin |
| I²C SDA | D4 | GPIO22 | J6, 4k7 Pull-up, VCC per Jumper SJ2 (3,3/5 V) |
| I²C SCL | D5 | GPIO23 | J6 |
| 1-Wire | D1 | GPIO1 | J5, 4k7 Pull-up (R17) |
| Status-LED WS2812B (MSG) | D3 | GPIO21 | U1 (5050WS2812B), Wasserwerte-Farbe + Poll-Flackern (v0.3.0); teilt sich die Leitung mit einer diskreten grünen LED |
| HAT1 / HAT2 / HAT3 | D8 / D9 / D10 | GPIO19 / GPIO20 / GPIO18 | J1, Pull-up/down per SJ1 |
| Diskrete LED STATUS | D0 | GPIO0 | blaue LED, ESPHome-/API-Blinkstatus (v0.2.0) |
| Batterie | BAT+ / BAT- | — | J2 (LiPo 3,7 V) |

### Weitere Stecker / Versorgung

- **J3** DC 12 V Eingang → Verpolschutz/Schutzdiode → **U2 = LM2675M-5.0** Buck → 5 V;
  XIAO erzeugt daraus 3,3 V. `ON/OFF#` von U2 ist ab Rev 2.0 nicht mehr extern
  beschaltet (NC) — der Regler hat einen internen Pull-Up und ist damit ohne
  externe Beschaltung dauerhaft aktiv. Firmwareseitig ohne Auswirkung (Pin
  war nie mit dem XIAO verbunden).
- **J4 FTDI**: greift RX/TX/DIR ab (Debug; teilt sich die Modbus-UART)
- **J2 BAT 3,7 V**: LiPo an die BAT-Pins des XIAO

> Hinweis: I²C, 1-Wire, HAT-Eingänge usw. sind **bewusst nicht** Teil
> der ersten Version (Umfang = nur Modbus), aber hardwareseitig vorhanden und
> später nachrüstbar. Die WS2812-LED (D3) wurde in v0.2.0 als MSG-Statusanzeige
> aktiviert, siehe Abschnitt 7.

---

## 3. Aus dem alten YAML extrahierter Modbus-Teil

### Bus-Parameter

| Parameter | Wert |
|---|---|
| Protokoll | Modbus RTU |
| Baudrate / Framing | 19200, 8N1 (Parität none, 1 Stopbit) |
| Slave-Adresse | 0x01 |
| Registertyp | `read` = Input-Register (FC 04) |
| update_interval | 30 s |
| command_throttle | 500 ms |
| send_wait_time | 500 ms |
| turnaround_time | 100 ms |
| Range-Bildung | mehrere Register mit `force_new_range: true` (je eigener Request) |

### Registersatz (PoolBoy)

| Entität | Register | Typ | Dekodierung | Einheit / Class |
|---|---|---|---|---|
| Ionisation | 0x0100 | U_WORD | — | mA, current |
| Hydrolyse | 0x0101 | U_WORD | × 0,1 | %, acc 0 |
| pH | 0x0102 | U_WORD | × 0,01 | ph, acc 2 |
| Redox | 0x0103 | U_WORD | — | mV, voltage |
| pH-Status (Sensor) | 0x0107 | U_WORD | bitmask 0x000F | numerisch |
| pH-Minus-Pumpe | 0x0107 | bit | bitmask 0x0800 | binary |
| Ionisierung On-Target | 0x010C | bit | bitmask 0x0001 | binary |
| Ionisierung Low | 0x010C | bit | bitmask 0x0002 | binary |
| Ionisierung Zeit erreicht | 0x010C | bit | bitmask 0x0008 | binary |
| Redox On-Target | 0x010D | bit | bitmask 0x0001 | binary |
| Redox Low | 0x010D | bit | bitmask 0x0002 | binary |
| Redox Flow | 0x010D | bit | bitmask 0x0008 | binary |

---

## 4. Getroffene Entscheidungen

| # | Frage | Antwort |
|---|---|---|
| 1 | Umfang | nur Modbus |
| 2 | ESPHome-Version | 2026.5.3 (bald 6.x), Framework ESP-IDF |
| 3 | Pin-Mapping | bestätigt (TX=GPIO16, RX=GPIO17, DIR=GPIO2) |
| 4 | Modbus-Slave | identisches PoolBoy-Gerät, Adresse 0x01, gleiche Register/Baudrate |
| 5 | Node-Name / Secrets | `OmniLink-PoolBoy`; `secrets.yaml` vorhanden |
| 6 | Timing | 30 s / 500 ms übernommen |

---

## 5. Ergebnis: ESPHome-Konfiguration

Datei: **`omnilink-poolboy.yaml`** (separat als Download).

Enthält:

- **esp32**: `board: esp32-c6-devkitc-1`, `variant: esp32c6`, Framework ESP-IDF
- **Konnektivität**: WiFi (aus `secrets.yaml`), AP-Fallback, captive_portal,
  Home-Assistant-API (Verschlüsselung), OTA, web_server (Auth aus `secrets.yaml`)
- **uart**: GPIO16/GPIO17, 19200 8N1
- **modbus**: `flow_control_pin: GPIO2`, send_wait 500 ms, turnaround 100 ms
- **modbus_controller**: Adresse 0x01, update_interval 30 s, throttle 500 ms
- **sensor / binary_sensor**: vollständiger PoolBoy-Registersatz (siehe Tabelle 3)
- **Diagnose**: WiFi Signal, Uptime, API Status

### Secrets

Aus `secrets.yaml` erwartet (wie bisher):
`wifi_ssid`, `wifi_password`, `web_server_username`, `web_server_password`.

Frisch generiert und inline im YAML (bei Bedarf nach `secrets.yaml` auslagern):
API-Encryption-Key, OTA-Passwort, AP-Passwort.

---

## 6. Offene Hinweise / nächste Schritte

- **Board-Bezeichner**: `esp32-c6-devkitc-1` + `variant: esp32c6` ist der robuste
  Weg. Falls ESPHome 2026.5.3 zickt, Alternative: `board: seeed_xiao_esp32c6`
  (dann **ohne** `variant`). Offline nicht gegen die installierte Version
  verifizierbar.
- **Erstflash** per USB-C, danach OTA.
- **Diagnose-Entities** (WiFi/Uptime/API-Status) sind Konnektivitäts-Lebenszeichen,
  kein zusätzlicher Funktionsumfang — bei Wunsch entfernbar.
- **Spätere Erweiterungen** (nicht Teil dieser Version): 1-Wire-Temperatur (J5),
  I²C (J6), HAT-Eingänge (J1).

---

## 7. Status-Visualisierung (v0.2.0 / v0.3.0)

| # | Frage | Antwort |
|---|---|---|
| 1 | STATUS-LED (blau, D0/GPIO0) | Diskrete LED, kein WS2812. Blinkt langsam (100 ms an / 1200 ms aus) solange keine API-Verbindung steht, schnell (100 ms an / 600 ms aus) sobald verbunden. Off-Zeiten bewusst länger als das MSG-Rot-Blinken (500/500ms) gewählt, damit sich die blaue LED optisch klar davon abhebt und nicht untergeht. |
| 2 | Umsetzung STATUS | Endlos-`script` (`status_led_run`, per `on_boot` einmalig gestartet) mit `while: true`-Loop, das bei jedem Durchlauf die `api.connected`-Bedingung prüft und die passende An/Aus-Sequenz auf einen `output: platform: gpio` (GPIO0) fährt. |
| 3 | MSG-LED (D3/GPIO21) | Physisch die vorhandene WS2812B (U1) — **teilt sich die Datenleitung mit einer diskreten grünen LED** (auf dem Schaltplan ursprünglich vage als "STAT/MSG" gruppiert, siehe Abschnitt 2). Ein Leitungstest hat bestätigt: ein reiner Digital-High-Pegel für 200 ms (statt WS2812-Protokoll-Timing) stört die WS2812 nicht, und die grüne LED reagiert sichtbar darauf. |
| 4 | MSG-LED — Zustände | (a) seit mehr als `msg_led_stale_timeout_ms` (45s) kein gültiger pH-/Redox-Wert (Start **oder** späterer Kommunikations-Unterbruch): blinkt **rot**, 500 ms an / 500 ms aus (`msg_led_monitor`). (b) solange aktuelle Daten da sind: konstante Farbe nach Wasserwerte-Regeln (siehe unten). (c) bei jedem Modbus-Poll: 3× kurzes Flackern (je 50 ms aus / 50 ms Farbe wiederhergestellt, `msg_led_comm_blip`), danach bleibt die Farbe stehen. |
| 5 | Wasserwerte-Farbregeln | grün: 7.1 < pH < 7.3 **und** Redox > 650mV. rot: pH < 6.9 **oder** > 7.4 **oder** Redox < 600mV. gelb: alles dazwischen (bewusster Sicherheits-Zwischenzustand für die Grenzwert-Lücken, z. B. pH exakt 7.4). |
| 6 | Umsetzung MSG | `light: platform: esp32_rmt_led_strip` auf GPIO21 (1 LED, WS2812), `internal: true`. Dimmung **zwingend** über den `brightness`-Parameter (Substitution `msg_led_brightness`, aktuell `0.5`) — ESPHomes `light.turn_on` normalisiert `red/green/blue` bei jedem Aufruf automatisch so, dass der grösste Kanal auf 1.0 gesetzt wird (`LightColorValues::normalize_color()`), kleine RGB-Werte allein dimmen also nicht. Farbe wird als Hue (0.0/1.0 je Kanal) in Globals (`msg_led_r/g/b`) gemerkt, damit der Kommunikations-Blitz sie nach dem Flackern wiederherstellen kann. `msg_led_last_update_ms` (Global, `uint32_t`, `millis()`-Zeitstempel) wird bei jedem `msg_led_update_water_color`-Lauf aktualisiert (ausgelöst über `on_value` von pH und Redox); `msg_led_monitor` prüft bei jedem 500ms-Zyklus per `while: true`-Loop, ob dieser Zeitstempel älter als `msg_led_stale_timeout_ms` ist (oder noch `0`, d. h. nie gesetzt) — ein einziger Mechanismus für Startphase **und** spätere Ausfälle. Der Kommunikations-Indikator hängt an `on_value` des zuerst abgefragten Registers „1.0 Ionisation" (0x0100) als Näherung für „ein Modbus-Poll-Zyklus lief". |
| 7 | Non-blocking bestätigt | `delay:` in ESPHome-Scripts/Automationen läuft über den kooperativen Scheduler (`App.scheduler.set_timer_common_`, siehe `core/base_automation.h`), kein Busy-Wait. Die LED-Scripts blockieren daher weder die Hauptschleife noch die Modbus-UART-Kommunikation. |
| 8 | HA-Sichtbarkeit | Beide LEDs sind reine Hardware-Statusanzeigen ohne eigene Home-Assistant-Entität. |

---

*Hardware: OmniLink-C6 Rev 1.0 · MCU: Seeed XIAO ESP32-C6 · RS485: SN65HVD75DR ·
Ziel-ESPHome: 2026.5.x (ESP-IDF)*
