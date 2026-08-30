# Backlog - omnilink-poolboy

Offene Punkte, Ideen und geplante Erweiterungen, die (noch) nicht Teil einer Version sind. Umgesetzte Punkte wandern beim Release in die [CHANGELOG.md](./CHANGELOG.md) und werden hier entfernt.

---

## Hardware-Erweiterungen (auf der Platine vorhanden, noch nicht implementiert)

- **1-Wire-Temperatur** (J5, `GPIO1`)
- **I²C** (J6, `GPIO22`/`GPIO23`)
- **HAT-Eingänge** (J1, `GPIO19`/`GPIO20`/`GPIO18`)

Details zum Pin-Mapping: [Design-Dokument](./Design_omnilink-poolboy.md).

---

## Software

- **Präzisere Kommunikations-/Ausfallerkennung:** ESPHome 2026.7.0 hat den Modbus-Client um zwei neue Callbacks erweitert — `on_modbus_no_response()` und `on_modbus_not_sent()`. Damit liesse sich `msg_led_monitor`/`msg_led_comm_blip` künftig direkt an echte Modbus-Antwort-/Sendefehler koppeln, statt sich nur auf `on_value` der Sensoren und den reinen `msg_led_stale_timeout_ms`-Timeout zu verlassen. Nicht dringend, da das aktuelle Timeout-basierte Verfahren bereits funktioniert.

---

## pH-Gültigkeit & erweiterte NeoPool-Register (nur lesen)

Ausgearbeitete Erweiterung des Registersatzes hinter der NeoPool-Steuerung (Slave 1, 19200 8N1). **Strikt nur lesen** — keine Schreibzugriffe auf USER-/INSTALLER-/FACTORY-Register (Schreiben verlangt EEPROM-Save `0x02F0`, nur ~100'000 Zyklen).

**Auslöser:** `sensor.omnilink_poolboy_1_2_ph` steht auffällig oft exakt auf `7.00` (49 h in 14 Tagen, Faktor 3 gegenüber jedem anderen Wert; im Fenster 6.90–7.10 kommen nur 6.9/7.0/7.1 vor, ausserhalb saubere 0.01er-Schritte). Laut Doku ist `MBF_MEASURE_PH` (`0x0102`) nur gültig, wenn Bit 14 von `MBF_PH_STATUS` (`0x0107`) gesetzt ist — dieses Bit wird heute nicht gelesen.

### Randbedingungen (gelten für alle Prioritäten)
- Bestehende Entity-IDs **nicht** umbenennen — Automationen und Recorder-Historie hängen daran.
- Bit 12 von `PH_STATUS` (Laugenpumpe) entfällt bewusst — die Anlage regelt nur mit Säure.
- pH/Redox nur publizieren, wenn das jeweilige Gültigkeits-Bit gesetzt ist; sonst **gar nichts senden** statt eines Ersatzwerts.

### Priorität 1 — Gültigkeit
- `0x0107 MBF_PH_STATUS` vollständig lesen und als binary_sensors auswerten: **Bit 14** = „pH Messmodul aktiv", **Bit 10** = „pH Durchfluss", **Bit 13** = „pH Regelung aktiv". Bits 0–3 bleiben als bestehender Sensor „1.4 pH Status" erhalten (Historie nicht brechen).
- `0x0108 MBF_RX_STATUS` **Bit 14** = „Redox Messmodul aktiv".
- **pH** (`0x0102`) nur publizieren, wenn `PH_STATUS` Bit 14 gesetzt ist; **Redox** (`0x0103`) nur, wenn `RX_STATUS` Bit 14 gesetzt ist.
- **Offen / zu klären:** Herkunft des heutigen binary_sensor „1.7 Redox Flow". `RX_STATUS` hat laut Doku **kein** Bit 10. Kandidaten: `PH_STATUS` Bit 10 oder `HIDRO_STATUS` Bit 3/9. Beim Umsetzen die tatsächliche Zuordnung ermitteln und dokumentieren.

### Priorität 2 — echter Anlagenstatus
- `0x010E MBF_RELAY_STATE`: Bit 1 = Filtration, Bit 0 = pH-Dosierrelais, Bit 2 = Beleuchtung.
- `0x010D MBF_HIDRO_STATUS`: Bit 3 = Durchfluss Hydrolysezelle FL1, Bit 4 = Abdeckung, Bit 1 = Low, Bit 8 = Chlorschock aktiv.

### Priorität 3 — Sollwerte als Sensoren (nur lesen)
- `0x0504 MBF_PAR_PH1` (×100, aktuell 730), `0x0505 MBF_PAR_PH2` (×100), `0x0508 MBF_PAR_RX1`, `0x0502 MBF_PAR_HIDRO`, `0x0106 MBF_MEASURE_TEMPERATURE` (Zehntel °C).

### Zusätzlich
- Den drei Poolsensoren `state_class: measurement` geben, damit Langzeitstatistiken entstehen (heute nur ~10 Tage Recorder-Historie).

### Abnahmekriterien
- Nach dem Filterstopp um 19:00 zeigt der pH-Sensor **keinen** Wert mehr, statt auf `7.00` zu springen.
- „pH Messmodul aktiv" fällt in den bisherigen 7.00-Phasen auf `off`.
- „Filtration" (`RELAY_STATE` Bit 1) deckt sich mit `binary_sensor.poolcontrol_filter`.
