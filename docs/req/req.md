# Bugal Requirements

## User interaction layer

### CLI

- Es soll ein Kommando zum Import csv geben mit Pfadangabe
- Es ein Kommando zum Excel export geben
- Es soll ein Kommando zum Import der Excel geben
- CLI ruft bootstrap mit Pfadangaben

### Model

- Kann aus csv Liste der Transaktionen erstellen
- Kann mehrere csv verarbeiten

### DB

- Es soll folgende Tabellen enthalten:
  - Transactions
  - Properties
  - Mapping
  - Rules
  - History

## Funktionale Anforderungen

- Jede Transaktion soll nur einmal vorkommen
- Transaktionen sollen Tags zugewiesen werden können
- Transaktionen können neue Tags aufnehmen
- Tags sollen entfernt werden können
- Tags sollen automatisch zugewiesen werden
- Die Tags sollen anhand der Regeln die Tags automatisch berechnen
- Transaktionen sollen von csv Dateien importiert werden
- Das System soll mehrere csv Dateien importieren können
- Importierte csv soll nicht noch einmal importiert werden
- Es soll eine csv Import-Historie persistent gespeichert werden
- Importierte csv Dateien sollen archiviert werden
- Das System verarbeitet nur gültige csv Dateien
- Das System extrahiert max und min Datum und gibt Filter für DB um die Liste der Hashes aus DB einzuschränken
- Transaktionen sollen in Datenbank persistent gespeichert werden
- Die Transaktionen sollen anhand der Regeln für Automapping geprüft werden und Mapping soll für Treffer aktualisiert werden
- Liste der Transaktionen soll in Excel dargestellt werden können
- Reports sollen konfigurierbar sein (Spalten und Filter)
- System soll Standardreport ausgeben, wenn vom Nutzer kein Report konfiguriert worden ist
- Reports sollen importiert werden können (dry-run soll unterstützt werden)
- Das System soll einen Forecast für einen Monat und einen Jahr berechnen. Besondere Monate sollen aus der Berechnung ausgeschlossen werden können.
- Das system soll die Filter in Excel exportieren und wieder importieren können
- Der Filter soll einen Zeitraum filtern können
- Der Filter soll über properties gefiltert werden können
- Das System soll die Properties aus Excel importieren können.
- Excel soll folgende Tabellen aufweisen:
  - Historie
  - Regeln
  - Properties
  - Transaktionen (schreibgeschützt)
  - Jahr
  - Users Guide
  - Forecast (optional)
- Beim Import der Exceldatei werden folgende Daten für den Import erstellt:
  - Liste der Transaktionshashes
  - Liste der Properties (unique ID)
  - Mapping Liste
  - Neue Properties
- Die Liste der Properties wird auf neue Properties durchsucht und legt neue in DB an.
- Die Mappingliste wird durchsucht und neue Mappings werden angelegt.

## Test drivers

- Fake DB um Zusammenarbeit mit DB zu testen:
  - get_list_csv_hashes()
  - get_properties()
  - get_rules()
  - get_mapping(filter:Filter)
  - push_transactions(transaction:list(Transaction)) -> bool
  - push_mapping(map:list(Mapping)) -> bool
  - push_history(history)
  