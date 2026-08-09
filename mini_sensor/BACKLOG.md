# Backlog - mini_sensor (MiniSensor)

Offene Punkte, Ideen und geplante Erweiterungen, die (noch) nicht Teil einer Version sind. Umgesetzte Punkte wandern beim Release in die [CHANGELOG.md](./CHANGELOG.md) und werden hier entfernt.

---

## Hardware-Erweiterungen (auf der Platine vorhanden, noch nicht genutzt)

- **I²C-Sensor** (J3, `GPIO4`/`GPIO5`): Bus ist im Beispiel-YAML bereits aktiv (`scan: true`), es hängt aber noch kein Sensor daran. Sobald ein konkreter I²C-Sensor angeschlossen wird, hier ergänzen — ggf. als eigenes Beispiel-YAML (z. B. `mini-sensor-i2c-<sensor>.yaml`), da die Platine mehrere unabhängige Anwendungen tragen kann.

Details zum Pin-Mapping: [Design-Dokument](./Design_mini-sensor.md).

---

## Software

- **DS18B20-Adresse fixieren:** Falls künftig ein zweiter 1-Wire-Sensor an denselben Bus (`GPIO2`) angeschlossen wird, muss die Adresse des Temperatursensors im YAML fest eingetragen werden (aktuell automatische Erkennung, da nur ein Sensor am Bus hängt).
