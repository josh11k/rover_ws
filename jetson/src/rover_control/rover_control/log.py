import csv
import os
from datetime import datetime


# Ordner, in dem alle Log-Dateien liegen
LOG_DIRECTORY = "/home/team/jetson/logs"


def write_log(filename, source, event, details):
    """
    Schreibt einen Log-Eintrag in eine CSV-Datei.
    -> Für Operations, Sensors, WiFi und STM-Kommunikation

    Args:
        filename: Name der CSV-Datei (ohne führenden Schrägstrich)
        source:   Node, der den Eintrag erzeugt hat
        event:    Art des Events
        details:  Zusätzliche Informationen
    """

    # Sicherstellen, dass der Log-Ordner existiert
    os.makedirs(LOG_DIRECTORY, exist_ok=True)

    # Führenden Schrägstrich entfernen, sonst verwirft os.path.join das Verzeichnis
    filepath = os.path.join(LOG_DIRECTORY, filename.lstrip("/"))

    # Prüfen, ob die Datei bereits existiert
    file_exists = os.path.isfile(filepath)

    # Datei im Append-Modus öffnen
    with open(filepath, "a", newline="") as file:

        writer = csv.writer(file)

        # Header nur beim ersten Erstellen schreiben
        if not file_exists:
            writer.writerow([
                "timestamp",
                "source",
                "event",
                "details"
            ])

        # Aktuellen Zeitpunkt erzeugen
        timestamp = datetime.now().astimezone().isoformat()

        # Log-Zeile schreiben
        writer.writerow([
            timestamp,
            source,
            event,
            details
        ])


def write_housekeeping_data(filename, source, component, type, value):
    """
    Schreibt einen Housekeeping-Eintrag in eine CSV-Datei.

    Args:
        filename:  Name der CSV-Datei (ohne führenden Schrägstrich)
        source:    Node, der den Eintrag erzeugt hat
        component: Komponente, zu der der Wert gehört
        type:      Art des Messwerts
        value:     Messwert
    """

    # Sicherstellen, dass der Log-Ordner existiert
    os.makedirs(LOG_DIRECTORY, exist_ok=True)

    # Führenden Schrägstrich entfernen, sonst verwirft os.path.join das Verzeichnis
    filepath = os.path.join(LOG_DIRECTORY, filename.lstrip("/"))

    # Prüfen, ob die Datei bereits existiert
    file_exists = os.path.isfile(filepath)

    # Datei im Append-Modus öffnen
    with open(filepath, "a", newline="") as file:

        writer = csv.writer(file)

        # Header nur beim ersten Erstellen schreiben
        if not file_exists:
            writer.writerow([
                "timestamp",
                "source",
                "component",
                "type",
                "value"
            ])

        # Aktuellen Zeitpunkt erzeugen
        timestamp = datetime.now().astimezone().isoformat()

        # Log-Zeile schreiben
        writer.writerow([
            timestamp,
            source,
            component,
            type,
            value
        ])