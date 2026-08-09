# Backlog - filahygro (FilaHygro)

Offene Punkte, Ideen und geplante Erweiterungen, die (noch) nicht Teil einer Version sind. Umgesetzte Punkte wandern beim Release in die [CHANGELOG.md](./CHANGELOG.md) und werden hier entfernt.

---

## Bug: Akku-SoC/Spannung dauerhaft ~4V/100%

**Symptom:** Die gemeldete Akkuspannung (`FilaBox Battery Voltage`) bzw. der
daraus berechnete SoC (`FilaBox Battery SoC`) zeigt unabhängig vom
tatsächlichen Ladezustand des Akkus konstant ~4V/100%.

**GPIO15 für `vbat_switch`** (schaltet den Spannungsteiler R12/R13 über Q1
am Gate-Netz `M_BAT`) **ist bestätigt korrekt verdrahtet** — R7 (10K) an
diesem Netz ist ein Pull-down, kein Pull-up. Die Verdrahtung ist damit als
Ursache ausgeschlossen.

**Ursache:** noch offen, weiter zu untersuchen.

**Auswirkung:** Der Akku kann leerlaufen, ohne dass eine Warnung (niedriger
SoC) rechtzeitig sichtbar wird.

---

## Software

- **OTA-Update-Mechanismus (MQTT-getriggerter Dauerbetrieb-Modus):** Geplanter
  Ablauf für Firmware-Updates ohne FTDI-Adapter: per MQTT-Kommando auf
  Dauerbetrieb umschalten (Deep-Sleep-Zyklus aussetzen, `ota:`/`api:` aktiv
  halten), OTA durchführen, danach per MQTT zurück in den normalen
  Messzyklus schalten. Im aktuellen `filabox1.yaml` **nicht implementiert**
  (kein `ota:`-/`api:`-Block, kein MQTT-Subscribe dafür) — bis dahin läuft
  jedes Update per FTDI (J1).
- **Deep-Sleep-Produktivdauer festlegen:** `sleep_duration` steht aktuell auf
  300s (Testwert). Für den Feldeinsatz sinnvollen Wert festlegen (z. B. 1h) —
  sollte erst nach dem SoC-Bugfix entschieden werden, da sich die
  Akkulaufzeit-Abschätzung sonst nicht verlässlich beurteilen lässt.

## Hardware-Erweiterungen (laut Schema vorgesehen, noch nicht genutzt)

- **HDC1080 als Alternative zu SHT31-D** (Lötbrücke SB1, Adresse `0x40`):
  Auf allen aktuell im Feld befindlichen Boards ist SHT31-D (`0x44`)
  bestückt. Sobald ein Board mit HDC1080 im Einsatz ist, Sensor-Konfiguration
  entsprechend ergänzen (ggf. als Substitution/Kommentar-Wahl im YAML, analog
  zur MiniSensor-Vorlage für mehrere Sensortypen).

## Pendente Anpassungen

- **Logger-Level:** `logger: level: DEBUG` ist ein Test-Leftover.
  Debug-Logging verlängert die Wachzeit vor dem Deep-Sleep (mehr UART-Ausgabe)
  und kostet damit zusätzlichen Akku — auf Standard-Level (`INFO`, kein
  `level:`-Eintrag) reduzieren, sobald der SoC-Bug behoben und das Verhalten
  im Feld bestätigt ist.

Details zum Pin-Mapping: [Design-Dokument](./Design_filahygro.md).
