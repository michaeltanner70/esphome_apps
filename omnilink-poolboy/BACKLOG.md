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
- **LED-Skripte koordinieren:** `msg_led_monitor` schreibt im else-Zweig alle 500 ms die Farbe neu und kann mitten in den Dreifach-Blitz von `msg_led_comm_blip` fallen — der Blitz ist dadurch nicht zuverlässig sichtbar. Funktional harmlos. Abhilfe: Flag, das der Blitz setzt und der Monitor respektiert, oder Farbe nur bei Zustandswechsel schreiben.
- **Kommunikations-Blitz an den Zyklus hängen:** Der Blitz hängt am `on_value` von „1.0 Ionisation" („erstes abgefragtes Register"). Seit 0.4.1 gibt es mit dem internen Statusregister `0x0108` einen Punkt, der sicher einmal pro vollständigem Zyklus feuert — dorthin verschieben, spätestens bei der Bereichszusammenfassung (unten).
- **„1.4 pH Status" ganzzahlig anzeigen:** `accuracy_decimals: 0` ergänzen, heute zeigt HA „0.0" statt „0".
- **Webserver-OTA:** Die Noise-Verschlüsselung (seit 0.4.1) gilt nur für ESPHome-OTA. Der Webserver bietet weiterhin einen unverschlüsselten `/update`-Endpunkt (geschützt nur durch das Digest-Login). Schliessen mit `web_server: ota: false`, falls Updates nur über ESPHome laufen.
- **`continuous: true`** für die Modbus-Reads bewusst **nicht** einsetzen, solange die Bereichszusammenfassung offen ist.
- **Veraltete Optionen (Warnungen unter 2026.9):** `command_throttle` ist wirkungslos (entfällt in 2027.2.0; Abstand nur noch über `turnaround_time` des `modbus`-Blocks), `rgb_order: GRB` → `channel_colors: GRB` (entfällt in 2027.3.0).

---

## Erweiterte NeoPool-Register (nur lesen)

Registersatz hinter der NeoPool-Steuerung (Slave 1, 19200 8N1). Die Gültigkeit von pH/Redox (bisher „Priorität 1") ist mit 0.4.0/0.4.1 umgesetzt, siehe [CHANGELOG.md](./CHANGELOG.md).

### Randbedingungen (gelten für alle Punkte)
- **Strikt nur lesen** — keine Schreibzugriffe auf USER-/INSTALLER-/FACTORY-Register (Schreiben verlangt EEPROM-Save `0x02F0`, nur ~100'000 Zyklen).
- Bestehende Entity-IDs **nicht** umbenennen — Historie, Dashboard, Template-Sensor `sensor.pool_ph_status` und die Pool-Alarmautomationen hängen daran. Gilt auch für „1.7 Redox …" (lesen `MBF_HIDRO_STATUS`, Namen bleiben — Entscheid 17.09.2026).
- Neue Entitäten nach der Discovery auf das Bereichspräfix `schwimmbad_` prüfen und im Entity-Registry korrigieren.
- Bit 12 von `PH_STATUS` (Laugenpumpe) entfällt bewusst — die Anlage regelt nur mit Säure.
- Updates: PoolBoy zuletzt — an ihm hängen Poolregelung und Modbus-Bus.

### Priorität 2 — echter Anlagenstatus
- `0x010E MBF_RELAY_STATE`: Bit 1 = Filtration (echter Relaiszustand statt Ableitung über `binary_sensor.poolcontrol_filter`), Bit 0 = pH-Dosierrelais, Bit 2 = Beleuchtung.
- `0x010D MBF_HIDRO_STATUS`, weitere Bits: Bit 4 (`0x0010`) = Abdeckung aktiv, Bit 8 (`0x0100`) = Chlorschock aktiv. Bits 0, 1, 3 sind als „1.7 Redox …" vorhanden.
- `0x0106 MBF_MEASURE_TEMPERATURE` (Zehntel °C) mit `state_class: measurement`. Heute kommt die Temperatur aus `sensor.poolcontrol_beckentemperatur_korrigiert`.

### Priorität 3 — Sollwerte als Sensoren
- `0x0502 MBF_PAR_HIDRO`, `0x0504 MBF_PAR_PH1` (×100, aktuell 730), `0x0505 MBF_PAR_PH2` (×100), `0x0508 MBF_PAR_RX1`. Macht die pH-Alarme absolut interpretierbar; eine Verstellung am Display fällt auf.
- Hydrolyse-Skala prüfen: `multiply: 0.1` mit Einheit % ist eine Annahme. Laut Doku hängt die Skala von `MBF_PAR_HIDRO_NOM` (`0x0306`) ab — 100 im Prozentmodus, sonst g/h.
- **Abfragefrequenz:** Sollwerte nicht im 30-s-Takt lesen. `skip_updates` ist in 2026.9 wirkungslos (entfällt in 2027.3.0). Stattdessen zweiter `modbus_controller` auf derselben Adresse mit langsamem Intervall, die Sollwert-Sensoren hängen daran:
  ```yaml
  modbus_controller:
    - id: poolboy_device          # bestehend, Messwerte
      modbus_id: poolboy_modbus
      address: 0x01
      update_interval: 30s
    - id: poolboy_device_slow     # neu, Sollwerte (USER-Seite)
      modbus_id: poolboy_modbus
      address: 0x01
      update_interval: 300s
  ```

### Bereichszusammenfassung (optional, nur mit Test)
- `reuse_previous_range` ganz weglassen: der Standard gruppiert `0x0100`–`0x010D` in eine Anfrage. Weniger Buslast (heute vier Einzelkommandos plus `0x0107`–`0x0108` und `0x010C`–`0x010D` pro Zyklus) und alle Werte aus demselben Moment. Risiko: Registerlücken bei `0x0104`–`0x0106` und `0x0109`–`0x010B`; nicht verifiziert, ob die NeoPool-Steuerung einen 14-Register-Block beantwortet.

### Abnahmekriterien
| Kriterium | Stand |
| :--- | :--- |
| Build unter 2026.9 fehlerfrei | erfüllt (0.4.0 auf dem Gerät, keine Modbus-Fehler); 0.4.1 validiert, Compile ausstehend |
| pH, Redox, Ionisation, Hydrolyse in der Langzeitstatistik | erfüllt; Temperatur offen (Priorität 2) |
| „pH Messmodul aktiv" während Filterbetrieb `on` | erfüllt |
| Nach dem Filterstopp kein neuer pH-Wert, insbesondere kein 7.00 | offen — erst mit 0.4.1 aussagekräftig |
| „pH Messmodul aktiv" fällt in den bisherigen 7.00-Phasen auf `off` | offen — entscheidender Test: bleibt das Bit `on`, ist 7.00 ein echter Messwert (Elektrode/Kalibrierung) |
| „Filtration" (`RELAY_STATE` Bit 1) deckt sich mit `binary_sensor.poolcontrol_filter` | offen (Priorität 2) |
