import csv
import os
from datetime import datetime


# Ordner, in dem alle Log-Dateien liegen
LOG_DIRECTORY = "/home/jetson/logs"


def write_log(filename, source, event, details):
    """
    Schreibt einen Log-Eintrag in eine CSV-Datei.
    -> In diesem Fall die für Operations

    Args:
        filename: Name der CSV-Datei
        source:   Node, der den Eintrag erzeugt hat
        event:    Art des Events
        details:  Zusätzliche Informationen
    """

    # Sicherstellen, dass der Log-Ordner existiert
    os.makedirs(LOG_DIRECTORY, exist_ok=True)

    filepath = os.path.join(LOG_DIRECTORY, filename)

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

def write_housekeeping_data(filename, source, event, details):
    """
    Schreibt einen Log-Eintrag in eine CSV-Datei.
    -> In diesem Fall die für Operations

    Args:
        filename: Name der CSV-Datei
        source:   Node, der den Eintrag erzeugt hat
        event:    Art des Events
        details:  Zusätzliche Informationen
    """

    # Sicherstellen, dass der Log-Ordner existiert
    os.makedirs(LOG_DIRECTORY, exist_ok=True)

    filepath = os.path.join(LOG_DIRECTORY, filename)

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

