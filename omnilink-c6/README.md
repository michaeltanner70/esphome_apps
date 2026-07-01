# OmniLink-C6 – Trägerplatine (PCB)

![Version](https://img.shields.io/badge/version-rev2-blue)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Eigenentwickelte Trägerplatine (TW microsystems) rund um das Seeed Studio XIAO **ESP32-C6**-Modul. Stellt RS485/Modbus, I²C, 1-Wire, eine WS2812B-Status-LED sowie HAT-Erweiterungsanschlüsse bereit. Wird aktuell vom Projekt [`omnilink-poolboy`](../omnilink-poolboy) genutzt (dort bisher nur der Modbus-Teil sowie die Status-LEDs implementiert).

---

## ⚠️ Haftungsausschluss (Disclaimer)

Alle in diesem Repository bereitgestellten Inhalte, Schaltpläne und Layouts sind rein private Bastelprojekte. Die Verwendung, der Nachbau sowie die Fertigung erfolgen ausdrücklich **auf eigene Gefahr**. Es wird keinerlei Haftung für Schäden an Geräten oder für Unfälle übernommen. Arbeiten an Netzelektrik (230V) dürfen nur von ausgebildetem Fachpersonal durchgeführt werden.

---

## 1. Ordnerinhalt

| Datei | Inhalt |
| :--- | :--- |
| [`OmniLink-C6_Schema.pdf`](./OmniLink-C6_Schema.pdf) | Schaltplan (Rev 2.0) |
| [`PCB_OmniLink-C6-Top_Layer.pdf`](./PCB_OmniLink-C6-Top_Layer.pdf) / [`-Bottom_Layer.pdf`](./PCB_OmniLink-C6-Bottom_Layer.pdf) | PCB-Layout, Top-/Bottom-Layer |
| [`Gerber_OmniLink-C6_PCB_Rev2.zip`](./Gerber_OmniLink-C6_PCB_Rev2.zip) | Gerber-Fertigungsdaten Rev 2.0 |
| [`BOM_OmniLink-C6_EasyEDA_Export.csv`](./BOM_OmniLink-C6_EasyEDA_Export.csv) | Stückliste (Bill of Materials), EasyEDA-Export |
| [`Backup_OmniLink-C6_rev2_20260701.zip`](./Backup_OmniLink-C6_rev2_20260701.zip) | EasyEDA-Projekt-Backup (Rev 2.0, editierbares Quellprojekt) |

---

## 2. Hauptkomponenten (BOM)

| Referenz | Bauteil | Funktion |
| :--- | :--- | :--- |
| U1 | 5050 WS2812B | Adressierbare RGB-LED (MSG-Anzeige, teilt sich die Leitung mit der diskreten LED2) |
| U2 | LM2675M-5.0 | Buck-Konverter, 12V (J3) → 5V |
| U3 | Seeed XIAO ESP32-C6 | Hauptcontroller |
| U4 | SN65HVD75DR | RS485-Transceiver (Modbus) |
| LED1 | — (blau) | diskrete STATUS-LED |
| LED2 | — (grün) | diskrete MSG-LED |

Vollständiges Pin-Mapping und Funktionsbeschreibung: [Design-Dokument omnilink-poolboy](../omnilink-poolboy/Design_omnilink-poolboy.md).

---

## 3. Revisionen

| Revision | Status | Bemerkung |
| :--- | :--- | :--- |
| Rev 1.0 | abgelöst | Pin-Mapping siehe [Design-Dokument omnilink-poolboy](../omnilink-poolboy/Design_omnilink-poolboy.md) |
| Rev 2.0 | aktuell, im Feld (omnilink-poolboy) | Änderungen gegenüber Rev 1.0 siehe [CHANGELOG.md](./CHANGELOG.md) |

---

## 4. Verwendet in

* [`omnilink-poolboy`](../omnilink-poolboy) — PoolBoy-Elektrolysegerät-Auslesung via Modbus RTU
