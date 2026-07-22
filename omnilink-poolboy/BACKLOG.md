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
