# PDF zu MIDI Converter

Ein GUI-basiertes Tool zur Konvertierung von PDF-Noten in MIDI-Dateien unter Verwendung von Audiveris zur optischen Musikerkennung (OMR).

## Übersicht

Dieses Tool kombiniert die Leistungsfähigkeit von Audiveris (optische Musikerkennung) mit einer benutzerfreundlichen grafischen Oberfläche, um PDF-Notenblätter automatisch in abspielbare MIDI-Dateien zu konvertieren.

### Funktionsweise

1. **PDF-Import**: Auswahl einer PDF-Datei mit Musiknoten
2. **OMR-Verarbeitung**: Audiveris analysiert die PDF und erstellt MusicXML-Dateien
3. **MIDI-Konvertierung**: Konvertierung der MusicXML in MIDI-Format
4. **Automatische Wiedergabe**: Die erstellte MIDI-Datei wird automatisch geöffnet

## Projektstruktur

```
ML-2025-PDF2MIDI
├── README.md           # Diese Dokumentation
├── tool.py             # Haupt-GUI-Anwendung
├── tomidi.py           # MusicXML zu MIDI Konvertierungslogik
├── Audiveris/          # Audiveris OMR-Software
│   ├── Audiveris.exe   # Hauptausführbare Datei
│   └── ...
├── MXL/                # Ausgabeordner für MusicXML-Dateien
├── XML/                # Temporäre XML-Dateien
└── MIDI/               # Ausgabeordner für MIDI-Dateien
```

## Voraussetzungen

- Python 3.x
- Tkinter (normalerweise in Python enthalten)
- pretty_midi (`pip install pretty_midi`)
- Audiveris (bereits im Projekt enthalten)

## Installation

1. Repository klonen oder herunterladen
2. Benötigte Python-Pakete installieren:
   ```bash
   pip install pretty_midi
   ```
3. Sicherstellen, dass die Ordnerstruktur korrekt ist und `Audiveris.exe` vorhanden ist

## Verwendung

### GUI-Anwendung starten

```bash
python tool.py
```

### Schritte zur Konvertierung

1. **PDF auswählen**: Klicken Sie auf "PDF auswählen" und wählen Sie Ihre Notendatei
2. **Konvertierung starten**: Klicken Sie auf "Konvertierung starten"
3. **Fortschritt verfolgen**: Der Konvertierungsprozess wird im Log-Fenster angezeigt
4. **Ergebnis**: Die MIDI-Datei wird automatisch geöffnet und abgespielt

### Kommandozeilen-Konvertierung

Für die direkte Verwendung der Konvertierungsfunktion:

```python
from tomidi import mxl_to_midi
mxl_to_midi("dateiname")  # ohne .mxl Erweiterung
```

## Features

### GUI-Funktionen
- Intuitive Benutzeroberfläche
- Echtzeit-Logging des Konvertierungsprozesses
- Automatische Dateierkennung und -verwaltung
- Thread-sichere Verarbeitung

### Konvertierungsfeatures
- **Tempo-Erkennung**: Automatische BPM-Erkennung aus MusicXML
- **Multi-Instrument-Support**: Unterstützung mehrerer Instrumente und Parts
- **Stimmen-Verarbeitung**: Korrekte Behandlung mehrstimmiger Partituren
- **Notenbindungen**: Unterstützung von Tie-Noten
- **Schlüssel-Erkennung**: Automatische Anpassung für verschiedene Notenschlüssel
- **Akkorde**: Korrekte Verarbeitung von Akkorden und gleichzeitigen Noten

## Technische Details

### Unterstützte Dateiformate
- **Input**: PDF-Dateien mit Musiknoten
- **Zwischenformat**: MusicXML (.mxl)
- **Output**: Standard MIDI-Dateien (.mid)

### Verarbeitungspipeline
1. **Audiveris OMR**: PDF → MusicXML (komprimiert als .mxl)
2. **XML-Extraktion**: .mxl → .xml
3. **MIDI-Konvertierung**: .xml → .mid

### Konfiguration
- Standard-BPM: 120 (falls nicht in der Partitur angegeben)
- MIDI-Auflösung: 480 Ticks per Quarter Note
- Standard-Velocity: 64 (50 für Slur-Noten)

## Ausgabeordner

- **MXL/**: Enthält die von Audiveris generierten MusicXML-Dateien
- **XML/**: Temporäre entpackte XML-Dateien
- **MIDI/**: Finale MIDI-Ausgabedateien

## Fehlerbehandlung

Das Tool bietet umfassende Fehlerbehandlung:
- Validierung der Eingabedateien
- Behandlung von Audiveris-Fehlern
- Robuste XML-Parsing
- Detaillierte Fehlermeldungen im Log

## Bekannte Limitationen

- Qualität der OMR hängt von der PDF-Qualität ab
- Komplexe Notationen können möglicherweise nicht perfekt erkannt werden
- Textanweisungen und Dynamikmarkierungen werden möglicherweise nicht übertragen

## Entwicklung

### Dateien und ihre Funktionen

- **`tool.py`**: Hauptanwendung mit GUI und Prozesssteuerung
- **`tomidi.py`**: Kernlogik für MusicXML zu MIDI Konvertierung

### Erweiterungsmöglichkeiten

- Unterstützung weiterer Eingabeformate
- Erweiterte MIDI-Konfigurationsoptionen
- Batch-Verarbeitung mehrerer Dateien
- Vorschaufunktion für erkannte Noten

## Lizenz

Dieses Projekt nutzt Audiveris für die optische Musikerkennung. Bitte beachten Sie die entsprechenden Lizenzbedingungen.

## Unterstützung

Bei Problemen oder Fragen überprüfen Sie bitte:
1. Die Qualität der PDF-Eingabedatei
2. Die Vollständigkeit der Audiveris-Installation
3. Die Log-Ausgabe für detaillierte Fehlermeldungen

---

*Entwickelt für das Machine Learning Projekt im Rahmen des Master-Studiums an der HFU.*
