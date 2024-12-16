"""
Oberste Schicht. Hier wird nur Service, Config und helper oder libs importiert.
"""
import sys
import os

# Sicherstellen, dass der src-Ordner im PYTHONPATH liegt
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(CURRENT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

# Module importieren
 
from cfg.config import get_config  # Beispiel: Import aus cfg
from bugal.srvc import service as srvc



def main():
    """Hauptfunktion des Programms."""
    print("Starte die Anwendung...")

    # Beispiel: Config laden
    config = get_config()
    print(f"Geladene Konfiguration: {config}")

    result = srvc.import_data(config)
    print(f"CSV Import processed: {result}")


if __name__ == "__main__":
    main()
