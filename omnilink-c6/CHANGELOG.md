# Changelog - OmniLink-C6

Alle wichtigen Änderungen an dieser Platine werden in dieser Datei dokumentiert. Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/).

---

## [Rev 2.0] - 2026-07-01

### Geändert
- **Beschriftung korrigiert:** kleinere Fehler in der Silkscreen-Beschriftung behoben.
- **U2 (LM2675M-5.0, Buck-Konverter) — `ON/OFF#` nicht mehr beschaltet:** Der Regler besitzt einen internen Pull-Up auf `ON/OFF#`, wodurch er ohne externe Beschaltung dauerhaft aktiv ist. Der Pin liegt in Rev 2.0 offen (NC).

---

## [Rev 1.0] - 2026-05-10

### Hinzugefügt
- **Initiale Version:** Trägerplatine für Seeed Studio XIAO ESP32-C6, entworfen von michael.tanner (EasyEDA). RS485-Transceiver (SN65HVD75DR), I²C- und 1-Wire-Anschlüsse, WS2812B-Status-LED, HAT-Erweiterungsanschlüsse (J1), LiPo-Anschluss (J2), 12V-DC-Eingang mit Buck-Konverter (J3), FTDI-Debug-Abgriff (J4).
