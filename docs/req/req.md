# Bugal Requirements

## Funktionale Anforderungen

## Design requirements

### CLI

> Es soll ein Kommando zum Import csv geben mit Pfadangabe

| Parameter | Status    |
|-----------|-----------|
| tested    | yes       |
| module    | cli.py    |

- test_import_single_csv
- test_import_banch_of_csv
  
> Es soll ein Kommando zum Excel export geben

| Parameter | Status    |
|-----------|-----------|
| tested    | partly    |
| module    | cli.py    |

- test_export_excel
  
> Es soll ein Kommando zum Import der Excel geben

| Parameter | Status    |
|-----------|-----------|
| tested    | partly    |
| module    | cli.py    |

- test_import_excel

> CLI ruft bootstrap mit Pfadangaben

| Parameter | Status    |
|-----------|-----------|
| tested    | no |
| module    | -  |

### Model {#model-unctional-req}

#### csv import {#csv-import-req}

> Kann aus csv Liste der Transaktionen erstellen. Transaktionen sollen von csv Dateien importiert werden

| Parameter | Status    |
|-----------|-----------|
| tested    | partially |
| module    | model.py  |

- test_transaction_creation
- test_transaction_equality_for_every_par
- test_create_transactions_list

> Das System soll mehrere csv Dateien importieren können

| Parameter | Status    |
|-----------|-----------|
| tested    | no |
| module    | model.py  |

- ?
  
> Importierte csv soll nicht noch einmal importiert werden Jede Transaktion soll nur einmal vorkommen

| Parameter | Status    |
|-----------|-----------|
| tested    | yes |
| module    | model.py  |

- test_transaction_creation
- test_transaction_equality_for_every_par
- test_create_transactions_list
- test_transactions_unique_hash_printed

> Importierte csv soll nicht noch einmal importiert werden

| Parameter | Status    |
|-----------|-----------|
| tested    | no |
| module    | model.py  |

> Es soll eine csv Import-Historie persistent gespeichert werden

| Parameter | Status    |
|-----------|-----------|
| tested    | no |
| module    | model.py  |

> Importierte csv Dateien sollen archiviert werden

| Parameter | Status    |
|-----------|-----------|
| tested    | no |
| module    | model.py  |

> Das System verarbeitet nur gültige csv Dateien

| Parameter | Status    |
|-----------|-----------|
| tested    | no |
| module    | model.py  |

>

| Parameter | Status    |
|-----------|-----------|
| tested    | no |
| module    | model.py  |

> 

| Parameter | Status    |
|-----------|-----------|
| tested    | no |
| module    | model.py  |

#### Mapping der Properties zu den Transactions

> Transaktionen sollen Tags zugewiesen werden können

| Parameter | Status    |
|-----------|-----------|
| tested    | no |
| module    | .py  |

> Transaktionen können neue Tags aufnehmen

| Parameter | Status    |
|-----------|-----------|
| tested    | no |
| module    | .py  |

> Tags sollen entfernt werden können

| Parameter | Status    |
|-----------|-----------|
| tested    | no |
| module    | .py  |

> Tags sollen automatisch zugewiesen werden

| Parameter | Status    |
|-----------|-----------|
| tested    | no |
| module    | .py  |

> Die Tags sollen anhand der Regeln die Tags automatisch berechnen

| Parameter | Status    |
|-----------|-----------|
| tested    | no |
| module    | .py  |

#### DB Import der Transaktionen aus der csv

> Transaktionen sollen in Datenbank persistent gespeichert werden

| Parameter | Status    |
|-----------|-----------|
| tested    | no |
| module    | model.py  |

> Das System extrahiert max und min Datum und gibt Filter für DB um die Liste der Hashes aus DB einzuschränken

| Parameter | Status    |
|-----------|-----------|
| tested    | no |
| module    | model.py  |

> Die Transaktionen sollen anhand der Regeln für Automapping geprüft werden und Mapping soll für Treffer aktualisiert werden

| Parameter | Status    |
|-----------|-----------|
| tested    | no |
| module    | model.py  |

#### Excel Import / Export

> Liste der Transaktionen soll in Excel dargestellt werden können

| Parameter | Status    |
|-----------|-----------|
| tested    | yes |
| module    | model.py  |

- test_excel_file_created
- test_transactions_header_printed
- test_transactions_printed_in_right_column
- test_transactions_unique_hash_printed
- test_transactions_printed

> Excel soll folgende Tabellen aufweisen:
>
>- Historie
>- Regeln
>- Properties
>- Transaktionen (schreibgeschützt)
>- Jahr
>- Users Guide
>- Forecast (optional)

| Parameter | Status    |
|-----------|-----------|
| tested    | yes |
| module    | model.py  |

- test_required_sheets_created

> Reports sollen konfigurierbar sein (Spalten und Filter)

| Parameter | Status    |
|-----------|-----------|
| tested    | no |
| module    | model.py  |

> System soll Standardreport ausgeben, wenn vom Nutzer kein Report konfiguriert worden ist

| Parameter | Status    |
|-----------|-----------|
| tested    | no |
| module    | model.py  |

> Reports sollen importiert werden können (dry-run soll unterstützt werden)

| Parameter | Status    |
|-----------|-----------|
| tested    | no |
| module    | model.py  |

> Das System soll die Properties aus Excel importieren können.

| Parameter | Status    |
|-----------|-----------|
| tested    | no |
| module    | model.py  |

> Das System soll einen Forecast für einen Monat und einen Jahr berechnen. Besondere Monate sollen aus der Berechnung ausgeschlossen werden können.

| Parameter | Status    |
|-----------|-----------|
| tested    | no |
| module    | model.py  |

> Das system soll die Filter in Excel exportieren und wieder importieren können

| Parameter | Status    |
|-----------|-----------|
| tested    | no |
| module    | model.py  |

> Der Filter soll einen Zeitraum filtern können

| Parameter | Status    |
|-----------|-----------|
| tested    | no |
| module    | model.py  |

> Der Filter soll über properties gefiltert werden können

| Parameter | Status    |
|-----------|-----------|
| tested    | no |
| module    | model.py  |

> Beim Import der Exceldatei werden folgende Daten für den Import erstellt:
>
>- Liste der Transaktionshashes
>- Liste der Properties (unique ID)
>- Mapping Liste
>- Neue Properties

| Parameter | Status    |
|-----------|-----------|
| tested    | no |
| module    | model.py  |

> Die Liste der Properties wird auf neue Properties durchsucht und legt neue in DB an.

| Parameter | Status    |
|-----------|-----------|
| tested    | no |
| module    | model.py  |

> Die Mappingliste wird durchsucht und neue Mappings werden angelegt.

| Parameter | Status    |
|-----------|-----------|
| tested    | no |
| module    | model.py  |

### DB

#### Module

> DB soll folgende Tabellen anlegen:
>
> - Transactions
> - Properties
> - Mapping
> - Rules
> - History

| Parameter | Status    |
|-----------|-----------|
| tested    | no |
| module    | -  |

#### Tabelle - Transactions

> Transactions Tabelle soll alle Werte von Transaction Value-Object enthalten

| Parameter | Status    |
|-----------|-----------|
| tested    | no |
| module    | -  |

> Transaction soll zusätzlich zu Value-Object einen hash enthalten

| Parameter | Status    |
|-----------|-----------|
| tested    | no |
| module    | -  |

## Test drivers

- Fake DB um Zusammenarbeit mit DB zu testen:
  - get_list_csv_hashes()
  - get_properties()
  - get_rules()
  - get_mapping(filter:Filter)
  - push_transactions(transaction:list(Transaction)) -> bool
  - push_mapping(map:list(Mapping)) -> bool
  - push_history(history)
  