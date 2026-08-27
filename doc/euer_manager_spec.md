# EÜR-Manager — Vollständige Projektspezifikation

> **Hinweis:** Diese Spezifikation beschreibt den **Ist-Stand** der Anwendung.
> Bei Konflikten ist der Code unter `src/finman/` maßgeblich. Abläufe und
> Strukturen als Diagramme finden sich in [finman_architecture.md](finman_architecture.md).
> Jeder Abschnitt ist in sich abgeschlossen und kann unabhängig referenziert werden.

---

## Changelog

| Version | Datum      | Änderung |
| ------- | ---------- | -------- |
| 2.3     | 2026-08-27 | EÜR-Bericht auf Positionen (M2M) + Wizard (3 Schritte, Positions-eigene Felder) umgebaut; Positions-Werte überschreiben Transaktion nur als Fallback |
| 2.2     | 2026-08-27 | Import-Löschung per CASCADE + PIN-Härtung, Historie Von/Bis-Spalten & Links, Dashboard-Accordion |
| 2.1     | 2026-08-26 | An überarbeiteten Code angeglichen: `TransactionInfo` (Notiz pro Transaktion), FormView-/ListView-Umbau von Import, Liste und Detail, Regel-CRUD mit Bearbeiten/Löschen + „Regeln anwenden", 17 Routen, Meta-Schnellzuweisung in der Liste |
| 2.0     | 2026-08-26 | An Ist-Code angeglichen: Parser-Architektur, Import-Workflow, zweistufige Prognosen, URL-/GUI-Beschreibung, Settings. Fixtures und Implementierungsreihenfolge entfernt |
| 1.0     | 2026-05-05 | Initiale Spezifikation |

---

## Inhaltsverzeichnis

1. [Projektziel](#1-projektziel)
2. [Tech-Stack](#2-tech-stack)
3. [Projektstruktur](#3-projektstruktur)
4. [Datenmodelle](#4-datenmodelle)
5. [CSV-Parser-Architektur](#5-csv-parser-architektur)
6. [Duplikat-Erkennung](#6-duplikat-erkennung)
7. [Import-Workflow](#7-import-workflow)
8. [Filter & Gruppierung](#8-filter--gruppierung)
9. [Automatische Kategorisierung](#9-automatische-kategorisierung)
10. [Vorhersage (Prediction)](#10-vorhersage-prediction)
11. [URL-Struktur](#11-url-struktur)
12. [GUI-Anforderungen](#12-gui-anforderungen)
13. [Initiale Daten](#13-initiale-daten)
14. [Django-Einstellungen](#14-django-einstellungen)
15. [Offene Punkte](#15-offene-punkte)

---

## 1. Projektziel

Lokal laufende Django-Webanwendung zur Verwaltung der **Einnahmen-Überschuss-Rechnung (EÜR)**.

- Läuft ausschließlich lokal via `uv run manage.py runserver` (aus `src\finman\` — dort liegt `manage.py`)
- Kein Produktions-Setup, kein Nginx, kein Docker erforderlich
- Kein Benutzer-Login für die App (nur das Standard-Django-Admin unter `/admin/`)
- Datenbank: SQLite, Datei `db.sqlite3` unter `src/`

---

## 2. Tech-Stack

| Komponente | Version / Paket |
|---|---|
| Python | 3.13+ (`requires-python = ">=3.13"`) |
| Django | >= 5.0 (`pyproject.toml`), aktuell läuft 6.x |
| Paketverwaltung | uv (`pyproject.toml`, `uv.lock`) |
| Datenbank | SQLite (django.db.backends.sqlite3) |
| Frontend | Bootstrap 5 (via CDN, kein npm) |
| Kein Task-Queue | Alles synchron, kein Celery/Redis |

**Abhängigkeiten (`pyproject.toml`):**
```toml
dependencies = [
    "django>=5.0",
]
```

---

## 3. Projektstruktur

```
finman/
├── pyproject.toml
├── doc/
│   ├── euer_manager_spec.md                 # diese Spezifikation
│   ├── finman_architecture.md               # Architektur mit Mermaid-Diagrammen
│   ├── giro_beispiel.csv                    # Beispiel-Export DKB Girokonto
│   └── visa_beispiel.csv                    # Beispiel-Export DKB Visa
├── logs/
│   └── parser_import.log                    # Parser-/Import-Logging (siehe §14)
└── src/
    ├── db.sqlite3                           # wird automatisch erstellt
    └── finman/
        ├── manage.py                        # Django-Befehle von hier ausführen
        ├── finman/                          # Django-Projektkonfiguration
        │   ├── __init__.py
        │   ├── settings.py                  # inkl. IMPORT_DELETE_PIN (siehe §7a)
        │   ├── urls.py                      # /admin/ + include transactions
        │   └── wsgi.py
        └── transactions/                    # Haupt-Django-App (einzige App)
            ├── admin.py                     # 8 von 9 Modellen registriert (EuerPosition jetzt dabei)
            ├── apps.py
            ├── forms.py                     # 10 Formen + CategoryChoiceField
            ├── models.py                    # alle ORM-Modelle (9)
            ├── urls.py                      # 24 Routen unter '/'
            ├── views.py                     # 6 function-based + 16 class-based Views
            ├── migrations/
            │   ├── 0001_initial.py
            │   ├── 0002_transactioninfo.py
            │   ├── 0003_import_cascade_delete.py
            │   ├── 0004_euer_position.py
            │   └── 0005_euer_position_fields.py
            ├── parsers/                     # CSV-Parser-Modul
            │   ├── __init__.py
            │   ├── base_parser.py           # ABC + TransactionData + Hashing-Helfer
            │   ├── giro_parser.py           # GiroDKBCSVParser
            │   ├── visa_parser.py           # VisaDKBCSVParser
            │   ├── generic.py               # GenericCSVParser (Fallback)
            │   └── registry.py              # PARSERS-Liste + get_parser()
            ├── services/                    # Business-Logik
            │   ├── __init__.py
            │   ├── importer.py              # Import + Tempdatei-Helfer
            │   ├── categorization.py        # Auto-Kategorisierung + apply_rules_to_all
            │   ├── euer.py                  # EÜR-Positions-Logik & Normalisierung
            │   ├── filter_service.py        # Fluent QuerySet-Filter
            │   └── prediction.py            # Vorhersage nächster Zahlungstermine
            ├── management/
            │   └── commands/
            │       ├── __init__.py
            │       └── update_predictions.py
            └── templates/
                └── transactions/
                    ├── base.html            # inkl. Import-Dropdown
                    ├── dashboard.html       # Letzte-Imports-Accordion
                    ├── import.html          # Card-Header + original_filename
                    ├── import_history.html  # Von/Bis-Spalten, kleine Schrift
                    ├── import_confirm_delete.html
                    ├── transaction_list.html # Filter-Accordion
                    ├── transaction_detail.html
                    ├── category_list.html
                    ├── category_form.html
                    ├── category_confirm_delete.html
                    ├── rule_list.html
                    ├── rule_form.html
                    ├── rule_confirm_delete.html
                    ├── prediction_list.html
                    ├── report_euer.html      # Positionen-Tabelle (ohne ROI)
                    ├── euer_wizard_step1/2/3.html
                    ├── euer_hint_form.html   # nun vollständige Positionswerte
                    ├── euer_confirm_delete.html
                    ├── _category_node.html
                    ├── _field_errors.html
                    └── _form_alert.html
```

---

## 4. Datenmodelle

> **Hinweis für Agent:** Alle Modelle in `transactions/models.py`. Migrationen nach jeder Modelländerung ausführen.

### 4.1 `ImportHistory`

```python
class ImportHistory(models.Model):
    file_md5      = models.CharField(max_length=32, unique=True)
    filename      = models.CharField(max_length=255)
    konto         = models.CharField(max_length=100)
    imported_at   = models.DateTimeField(auto_now_add=True)
    row_count     = models.IntegerField(default=0)
    min_date      = models.DateField(null=True, blank=True)
    max_date      = models.DateField(null=True, blank=True)
    duplicate_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['-imported_at']
        verbose_name = 'Import'
        verbose_name_plural = 'Importe'
```

### 4.2 `Transaction`

```python
class Transaction(models.Model):
    hash          = models.CharField(max_length=64, unique=True)  # SHA-256
    date          = models.DateField()
    status        = models.CharField(max_length=50, blank=True)
    debitor       = models.CharField(max_length=255)
    verwendung    = models.TextField(blank=True)
    target_konto  = models.CharField(max_length=100, blank=True)
    src_konto     = models.CharField(max_length=100)
    value         = models.DecimalField(max_digits=12, decimal_places=2)
    debitor_id    = models.CharField(max_length=100, blank=True)
    mandats_ref   = models.CharField(max_length=100, blank=True)
    customer_ref  = models.CharField(max_length=100, blank=True)
    imported_at   = models.DateTimeField(auto_now_add=True)
    import_file   = models.ForeignKey(
        ImportHistory,
        on_delete=models.CASCADE,
        null=True,
        related_name='transactions'
    )

    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['debitor']),
            models.Index(fields=['value']),
        ]

    @property
    def attribute_count(self):
        """Anzahl zugewiesener Kategorien + gefüllter Meta-Felder."""
        count = self.categories.count()
        meta = getattr(self, 'meta', None)
        if meta:
            count += sum(1 for f in ('art', 'prioritaet', 'intervall') if getattr(meta, f))
        return count
```

### 4.3 `Category`

```python
class Category(models.Model):
    name    = models.CharField(max_length=100)
    parent  = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='subcategories'
    )

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['parent__name', 'name']

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} / {self.name}"
        return self.name

    def get_descendants(self):
        """IDs dieses Knotens + aller Nachkommen (rekursiv)."""
        ids = [self.pk]
        for child in self.subcategories.all():
            ids.extend(child.get_descendants())
        return ids

    def get_full_path(self):
        """Vollständiger Pfad, z. B. 'Haushalt / Lebensmittel'."""
        names = []
        current = self
        while current is not None:
            names.append(current.name)
            current = current.parent
        return ' / '.join(reversed(names))
```

> `get_descendants()` wird vom Filter (ganzer Kategorie-Teilbaum, siehe §8),
> vom CategoryForm (Selbstzuweisung als Parent verhindern) und von der
> Lösch-Sperre der Kategorien verwendet. `get_full_path()` liefert die Labels
> für Kategorie-Dropdowns (`CategoryChoiceField`).

### 4.4 `TransactionCategory` (Assoziationstabelle)

> **Wichtig:** Originaltransaktionen werden nie verändert. Kategorien werden ausschließlich über diese Tabelle zugewiesen.

```python
ASSIGNED_BY_CHOICES = [('auto', 'Automatisch'), ('manual', 'Manuell')]

class TransactionCategory(models.Model):
    transaction  = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='categories')
    category     = models.ForeignKey(Category, on_delete=models.CASCADE)
    assigned_by  = models.CharField(max_length=10, choices=ASSIGNED_BY_CHOICES, default='auto')
    assigned_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('transaction', 'category')]
```

### 4.5 `FilterRule`

```python
ART_CHOICES = [('FIX', 'Fix'), ('FLEX', 'Flex')]
PRIORITAET_CHOICES = [
    ('Familie', 'Familie'), ('Kinder', 'Kinder'),
    ('Waldemar', 'Waldemar'), ('Nastja', 'Nastja'),
    ('Uljana', 'Uljana'), ('Mischa', 'Mischa'),
]
INTERVALL_CHOICES = [
    ('einmalig', 'Einmalig'), ('wöchentlich', 'Wöchentlich'),
    ('monatlich', 'Monatlich'), ('quartal', 'Quartal'),
    ('halbjährlich', 'Halbjährlich'), ('jährlich', 'Jährlich'),
    ('abgelaufen', 'Abgelaufen'), ('geplant', 'Geplant'),
]

class FilterRule(models.Model):
    name                = models.CharField(max_length=100)
    debitor_contains    = models.CharField(max_length=255, blank=True)
    verwendung_contains = models.CharField(max_length=255, blank=True)
    category            = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    art                 = models.CharField(max_length=10, choices=ART_CHOICES, blank=True)
    prioritaet          = models.CharField(max_length=20, choices=PRIORITAET_CHOICES, blank=True)
    intervall           = models.CharField(max_length=20, choices=INTERVALL_CHOICES, blank=True)
    is_active           = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
```

> Die alphabetische Sortierung (`ordering = ['name']`) bestimmt die
> Prüfreihenfolge bei der Auto-Kategorisierung (siehe §9).

### 4.6 `TransactionMeta` (Assoziationstabelle für Regel-Metadaten)

> Speichert, welche FilterRule auf eine Transaktion gepasst hat — ohne die Transaktion selbst zu verändern.

```python
class TransactionMeta(models.Model):
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name='meta')
    rule        = models.ForeignKey(FilterRule, on_delete=models.SET_NULL, null=True, blank=True)
    art         = models.CharField(max_length=10, choices=ART_CHOICES, blank=True)
    prioritaet  = models.CharField(max_length=20, choices=PRIORITAET_CHOICES, blank=True)
    intervall   = models.CharField(max_length=20, choices=INTERVALL_CHOICES, blank=True)
```

### 4.7 `TransactionInfo` (Notiz pro Transaktion)

> Freitext-Notiz zu einer Transaktion (1:1), unabhängig von Kategorien/Regeln.
> Wird über die Detailseite gepflegt (`TransactionInfoForm`).

```python
class TransactionInfo(models.Model):
    transaction = models.OneToOneField(
        Transaction,
        on_delete=models.CASCADE,
        related_name='info',
    )
    text = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Info: {self.transaction.debitor}"
```

> **Hinweis:** `TransactionInfo` ist derzeit **nicht** im Django-Admin
> registriert — alle übrigen Modelle sind es (siehe §15, offener Punkt).

### 4.8 `EuerPosition` (EÜR-Sammelposten)

> Jede Transaktion gehört zu **maximal einer** Position je Jahr – eine Position bündelt mehrere Transaktionen und trägt **eigene** Werte für Kategorie/Typ/Intervall/Priorität/Hinweis. Leere Transaktionsfelder erben den Positionswert, abweichende gefüllte Werte lösen eine Warnung im Bericht aus.

```python
class EuerPosition(models.Model):
    name         = models.CharField(max_length=100)
    hint         = models.TextField(blank=True, default='')
    year         = models.IntegerField()
    category     = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL, related_name='euer_positions')
    art          = models.CharField(max_length=10, choices=ART_CHOICES, blank=True)       # in Tabelle als Typ
    intervall    = models.CharField(max_length=20, choices=INTERVALL_CHOICES, blank=True)
    prioritaet   = models.CharField(max_length=20, choices=PRIORITAET_CHOICES, blank=True)
    transactions = models.ManyToManyField('Transaction', blank=True, related_name='euer_positions')
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        unique_together = [('name', 'year')]
        verbose_name = 'EÜR-Position'
        verbose_name_plural = 'EÜR-Positionen'
```

> Details & Normalisierung siehe §9a. Ein Transaktionswechsel über Jahre hinweg ist erlaubt, weil nach `Position.year` (nicht `Transaction.date`) gefiltert wird – Januar-Buchungen können so dem abgelaufenen Jahr zugeordnet werden.

### 4.9 `PredictionResult`

```python
class PredictionResult(models.Model):
    debitor            = models.CharField(max_length=255)
    category           = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    next_expected_date = models.DateField()
    avg_interval_days  = models.IntegerField()
    last_occurrence    = models.DateField()
    confidence         = models.FloatField()   # 0.0 – 1.0
    predicted_at       = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('debitor', 'category')]
```

---

## 5. CSV-Parser-Architektur

### 5.1 `TransactionData` (Dataclass, kein ORM)

```python
# transactions/parsers/base_parser.py
@dataclass
class TransactionData:
    date:         date
    value:        Decimal
    debitor:      str
    src_konto:    str
    status:       str        = ''
    verwendung:   str        = ''
    target_konto: str        = ''
    debitor_id:   str        = ''
    mandats_ref:  str        = ''
    customer_ref: str        = ''
```

### 5.2 Abstrakte Basisklasse und Hilfsfunktionen (`base_parser.py`)

```python
class BaseCSVParser(ABC):

    @abstractmethod
    def detect(self, filepath: str) -> bool:
        """Returns True if this parser can handle the CSV file."""
        ...

    @abstractmethod
    def parse(self, filepath: str) -> list[TransactionData]:
        """Parses the CSV file and returns a list of TransactionData."""
        ...

    def get_meta_info(self, filepath: str) -> dict:
        """Metadaten für die Import-Vorschau.
        Erwartet wird ein Dict mit konto, parser_name und preview_rows."""
        return {}
```

Zusätzlich liegen hier die gemeinsamen Hilfsfunktionen:

```python
def compute_transaction_hash(td: TransactionData) -> str:
    raw = f"{td.date}{td.debitor}{td.value}{td.verwendung}{td.target_konto}{td.src_konto}"
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()

def compute_file_md5(filepath: str) -> str:
    # MD5 über die Rohdatei (8192-Byte-Blöcke)

def parse_german_number(s: str) -> Decimal:
    # entfernt ' EUR'/'€' und Tausenderpunkte, wandelt ',' → '.',
    # liefert signiertes Decimal
```

### 5.3 Konkrete Parser

Gemeinsame Konventionen aller DKB-Parser: Encoding `utf-8-sig`, Trennzeichen
`;`, Datumsformate `%d.%m.%Y` und `%d.%m.%y`. Spalten werden dynamisch über den
Header eingelesen (`col_map`) — fehlende Spalten ergeben leere Felder, defekte
Zeilen werden übersprungen und geloggt. Beispieldateien: `doc/giro_beispiel.csv`,
`doc/visa_beispiel.csv`.

#### `GiroDKBCSVParser` (`giro_parser.py`)

Dateiaufbau: Zeilen 1–3 Metadaten (Kontobezeichnung/IBAN, Zeitraum, Kontostand),
Zeile 4 leer, Zeile 5 Header, ab Zeile 6 Daten.

- `detect()`: erste Zeile beginnt mit `'Girokonto;'`
- `src_konto`: Kontobezeichnung aus Zeile 1 (zweites Segment)
- Debitor abhängig von `Umsatztyp`: **Eingang → Zahlungspflichtige\*r**,
  sonst → Zahlungsempfänger\*in

| CSV-Spalte | TransactionData-Feld |
|---|---|
| *Zeile 1, Segment 2* | `src_konto` |
| `Buchungsdatum` | `date` |
| `Status` | `status` |
| `Umsatztyp` | *(wählt das Debitor-Feld)* |
| `Zahlungspflichtige*r` | `debitor` (bei Eingang) |
| `Zahlungsempfänger*in` | `debitor` (bei Ausgang) |
| `Verwendungszweck` | `verwendung` |
| `IBAN` | `target_konto` |
| `Betrag (€)` | `value` (via `parse_german_number`) |
| `Gläubiger-ID` | `debitor_id` |
| `Mandatsreferenz` | `mandats_ref` |
| `Kundenreferenz` | `customer_ref` |
| `Wertstellung` | *(ignoriert)* |

#### `VisaDKBCSVParser` (`visa_parser.py`)

Dateiaufbau: Zeile 1 `Karte;<Bezeichnung>;<maskierte Nummer>`, Zeile 2 leer,
Zeile 3 Saldo, Zeile 4 leer, Zeile 5 Header (`Belegdatum;Wertstellung;Status;
Beschreibung;Umsatztyp;Betrag (€);Fremdwährungsbetrag`), ab Zeile 6 Daten.

- `detect()`: erste Zeile beginnt mit `'Karte;'`
- `src_konto`: drittes Segment der Zeile 1 (maskierte Kartennummer)
- Besonderheit: der `Umsatztyp` wird in `verwendung` gespeichert

| CSV-Spalte | TransactionData-Feld |
|---|---|
| *Zeile 1, Segment 3* | `src_konto` |
| `Belegdatum` | `date` |
| `Status` | `status` |
| `Beschreibung` | `debitor` |
| `Umsatztyp` | `verwendung` |
| `Betrag (€)` | `value` (via `parse_german_number`) |
| `Wertstellung`, `Fremdwährungsbetrag` | *(ignoriert)* |

#### `GenericCSVParser` (`generic.py`)

Fallback für alle übrigen CSVs — **muss immer der letzte Eintrag der Registry
bleiben** (siehe §5.4).

- `detect()`: gibt immer `True` zurück
- Trennzeichen-Erkennung automatisch: `';'` oder `','` je nach erster Zeile
- Liest die erste Zeile als Header (`csv.DictReader`)
- Ohne Spalten-Mapping müssen die Header exakt wie die Feldnamen von
  `TransactionData` heißen (`date`, `value`, `debitor`, …)
- Datumsformate zusätzlich: `%Y-%m-%d`, `%m/%d/%Y`
- `parse()` akzeptiert optional ein `column_mapping` (CSV-Spalte → Zielfeld);
  diese Schnittstelle ist vorhanden, wird vom Importer derzeit aber nicht
  genutzt und es existiert keine Mapping-Oberfläche

### 5.4 Parser-Registry

```python
# transactions/parsers/registry.py
PARSERS = [GiroDKBCSVParser, VisaDKBCSVParser, GenericCSVParser]

def get_parser(filepath: str):
    for parser_class in PARSERS:
        parser = parser_class()
        if parser.detect(filepath):
            return parser
    return None  # praktisch unerreichbar: GenericCSVParser matcht immer
```

Die Reihenfolge in `PARSERS` ist die Prüfreihenfolge — der erste Treffer
gewinnt. Neues Bankformat: Unterklasse von `BaseCSVParser` erstellen und in
der Liste **vor** `GenericCSVParser` eintragen.

---

## 6. Duplikat-Erkennung

> Beide Prüfungen sind zweistufig: Ebene 1 bricht den ganzen Import ab,
> Ebene 2 filtert einzelne Zeilen heraus (z. B. bei überlappenden
> Zeitraum-Exporten). Implementierung in `transactions/parsers/base_parser.py`,
> Einsatz im Workflow in §7 und [§4.2 der Architektur](finman_architecture.md#52-zweistufige-duplikaterkennung).

### 6.1 Datei-Ebene (MD5)

- Vor dem Parsen: `ImportHistory.objects.filter(file_md5=md5).exists()`
- Bei Treffer → Import sofort abbrechen (`ValueError`) mit Datum des ursprünglichen Imports

### 6.2 Transaktions-Ebene (SHA-256)

```python
def compute_transaction_hash(td: TransactionData) -> str:
    raw = f"{td.date}{td.debitor}{td.value}{td.verwendung}{td.target_konto}{td.src_konto}"
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()
```

- Vor jedem INSERT: `Transaction.objects.filter(hash=tx_hash).exists()`
- Bei Treffer → Transaktion überspringen, Zähler für `duplicate_count` erhöhen

---

## 7. Import-Workflow

> Service in `transactions/services/importer.py`, View als Class-Based View
> `ImportView(FormView)` in `transactions/views.py`.

```
Ablauf:
1. ImportView.form_valid(): Upload via save_upload_to_temp() in Tempdatei
   ODER Pfad-Input übernehmen (Formular verlangt genau eine der beiden Angaben;
   fehlende Datei → messages.error + form_invalid)
2. Vorschau: get_parser() + get_meta_info() → Konto, Parser-Name, 3 Vorschauzeilen
3. import_csv(filepath, original_filename):
   a. MD5 berechnen → Datei-Duplikat-Check (ValueError mit Ursprungsdatum)
   b. Parser aus Registry ermitteln
   c. CSV parsen → list[TransactionData]
   d. ImportHistory anlegen (md5, original_filename oder basename) und speichern
   e. Für jede TransactionData:
      - Hash berechnen, Transaktions-Duplikat-Check
      - Transaction speichern (inkl. FK CASCADE auf die ImportHistory)
      - auto_categorize(tx) aufrufen
   f. ImportHistory finalisieren: row_count, duplicate_count,
      konto (= src_konto der ersten Zeile), min_date, max_date
4. cleanup_temp() im finally-Block (nur eigene Tempdateien unter gettempdir())
5. Ergebnis: {imported, skipped, duplicates, import_id} — gerendert zusammen
   mit der Vorschau; ValueError wird als messages.error angezeigt
```

> **Dateiname vollständig & kein `…`:** Import speichert `original_filename` (vom Upload) statt Temp-Namen; Historie/Dashboard zeigen den vollen Namen (`word-break: break-all`).

### 7a. Import löschen (restlos, PIN-gehärtet)

> `Transaction.import_file` ist `CASCADE` – Löschen eines `ImportHistory`-Eintrags über `ImportDeleteView` (POST, PIN-Abfrage, `@never_cache`) entfernt automatisch alle zugehörigen Transaktionen samt `TransactionCategory`/`TransactionMeta`/`TransactionInfo`. Jeder Löschweg (auch Django-Admin) kaskadiert. PIN ist `settings.IMPORT_DELETE_PIN` (Default `1234`, via `FINMAN_DELETE_PIN` in der Umgebung überschreibbar). Nach dem Löschen ist `file_md5` wieder frei und dieselbe Datei kann erneut importiert werden. Route `import/<int:pk>/delete/` → `import_confirm_delete.html` zeigt Dateiname/Zeitraum/Tx-Anzahl.

```python
def import_csv(filepath: str, original_filename: str | None = None) -> dict:
    md5 = compute_file_md5(filepath)
    if ImportHistory.objects.filter(file_md5=md5).exists():
        existing = ImportHistory.objects.get(file_md5=md5)
        raise ValueError(f'Datei wurde bereits am '
                         f'{existing.imported_at:%d.%m.%Y %H:%M} importiert.')

    parser = get_parser(filepath)
    transactions_data = parser.parse(filepath)

    import_history = ImportHistory(
        file_md5=md5,
        filename=original_filename or os.path.basename(filepath),
    )
    import_history.save()

    for td in transactions_data:
        tx_hash = compute_transaction_hash(td)
        if Transaction.objects.filter(hash=tx_hash).exists():
            skipped += 1
            continue
        tx = Transaction(hash=tx_hash, ..., import_file=import_history)
        tx.save()
        auto_categorize(tx)
        imported += 1

    dates = [td.date for td in transactions_data]
    import_history.row_count = len(transactions_data)
    import_history.duplicate_count = skipped
    import_history.konto = transactions_data[0].src_konto if transactions_data else ''
    import_history.min_date = min(dates) if dates else None
    import_history.max_date = max(dates) if dates else None
    import_history.save()

    return {'imported': imported, 'skipped': skipped,
            'duplicates': skipped, 'import_id': import_history.pk}
```

> **Achtung:** Der Import läuft **nicht** in `transaction.atomic`. Bricht er
> mittendrin ab, bleiben Teilimporte plus ein angelegter `ImportHistory`-
> Eintrag zurück. Siehe Architekturdokument, offene Frage T-04.

---

## 8. Filter & Gruppierung

> Implementierung in `transactions/services/filter_service.py`

```python
from ..models import Transaction, TransactionCategory, TransactionMeta, Category


class TransactionFilter:
    """Fluent Builder: jede Methode filtert nur bei gesetztem Parameter
    und gibt self zurück; apply() liefert das finale distinct()-QuerySet."""

    def __init__(self):
        self.qs = Transaction.objects.all()

    def by_date_range(self, start: date, end: date):
        self.qs = self.qs.filter(date__range=(start, end))
        return self

    def by_debitor(self, name: str):
        if name:
            self.qs = self.qs.filter(debitor__icontains=name)
        return self

    def by_category(self, category_id: int):
        # inkl. aller Subkategorien (rekursiv über get_descendants)
        if category_id:
            cat = Category.objects.get(pk=category_id)
            cat_ids = cat.get_descendants()
            self.qs = self.qs.filter(categories__category__in=cat_ids)
        return self

    def by_art(self, art: str):
        if art:
            self.qs = self.qs.filter(meta__art=art)
        return self

    def by_prioritaet(self, prio: str):
        if prio:
            self.qs = self.qs.filter(meta__prioritaet=prio)
        return self

    def by_intervall(self, intervall: str):
        if intervall:
            self.qs = self.qs.filter(meta__intervall=intervall)
        return self

    def apply(self):
        return self.qs.distinct()
```

**Verwendung in View (`TransactionListView`, CBV):**
```python
SORT_FIELDS = {'date', '-date', 'value', '-value',
               'debitor', '-debitor', 'status', '-status'}   # Whitelist

class TransactionListView(ListView):
    model = Transaction
    paginate_by = 50                     # Pagination durch ListView

    def get_queryset(self):
        if self.request.GET:
            form = TransactionFilterForm(self.request.GET)   # validierte GET-Parameter
            ...
        f = TransactionFilter()
        cd = form.cleaned_data
        if cd.get('start') and cd.get('end'):
            f.by_date_range(cd['start'], cd['end'])
        f.by_debitor(cd.get('debitor') or '')
        if cd.get('category'):
            f.by_category(cd['category'].pk)
        f.by_art(cd.get('art') or '')
        f.by_prioritaet(cd.get('prioritaet') or '')
        f.by_intervall(cd.get('intervall') or '')

        sort = self.request.GET.get('sort', '-date')
        if sort not in SORT_FIELDS:      # Schutz vor Sort-Injection
            sort = '-date'
        return f.apply().order_by(sort)

    # get_context_data(): filter_form, meta_form, total_sum
    # (Sum über das gesamte gefilterte QuerySet, nicht nur die Seite)
```

> Ungültige Filterwerte werden verworfen (`messages.error`), die Liste zeigt
> dann die ungefilterte Menge. Das Filterformular liefert zusätzlich die
> Werte für die Sortier-Links im Template zurück.

---

## 9a. EÜR-Positionen (Sammelposten)

> Service `services/euer.py` + Modelle `EuerPosition` (§4.8) + Wizard (`views.py: EuerWizard*`) + Bericht (`report_euer`).

**Tabelle `EÜR-Bericht` pro Kalenderjahr (`Position.year`, nicht `Transaction.date`):**

`Position | Betrag (Σ aller zugeordneten Transaktionen) | Kategorie | Sub-Kategorie | Typ (= EuerPosition.art, FIX/FLEX) | Intervall | Priorität | Hinweis (editierbar, nur Position) | Betrag täglich / wöchentlich / monatlich / jährlich (aus Σ Betrag × Intervall-Faktor) | wird gezahlt über (= `src_konto` der ersten Transaktion) | Aktionen | Warnicon`

* Ableitung: `Kategorie/Sub-Kategorie` aus `position.category.get_full_path()`, `Typ/Intervall/Priorität` direkt aus `position.art/intervall/prioritaet`. Ist ein Transaktionsfeld leer, gilt es als *übernommen* (keine Warnung); ist es gefüllt und weicht vom Positionswert ab → Warnung (`bi-exclamation-triangle`, Felder `kategorie/typ/intervall/prioritaet/konto` getrennt geprüft). Eine Transaktion darf nur in **einer** Position je Jahr enthalten sein (Wizard filtert andere Positionen des Jahres aus).
* Intervall: `einmalig/geplant` wie `jährlich` gerechnet; `einmalig`/`abgelaufen` sind bei Neuanlage verboten (`CREATION_FORBIDDEN_INTERVALLS`), `abgelaufen` friert die vier normalisierten Werte ein (keine Neuberechnung). `geplant` wird wie `jährlich` behandelt.
* ROI-Spalte ist derzeit **nicht enthalten** (bewusst weggelassen).

**Wizard (3 Schritte, FormView, Session-basiert, `@never_cache`):**

1. `wizard/step1/` (`EuerPositionForm` – Name, Jahr, Kategorie, Typ, Intervall, Priorität, Hinweis) – bei `?edit=<pk>` lädt die Instanz als `instance` zwecks korrekter `unique_together`-Validierung.
2. `wizard/step2/` (`PositionTransactionsForm` – `MultipleChoice` der letzten 500 Transaktionen, bereits zugeordnete des gleichen Jahres ausgeblendet; beim Bearbeiten sind bisherige Zuordnungen vorausgewählt).
3. `wizard/step3/` (Vorschau inkl. `position_summary`-Warnungen, Betragssummen) → Speichern setzt `pos.transactions` und verwirft Session.

Zusätzlich `reports/euer/<pk>/hint/` (`EuerPositionHintView`, vollständige `EuerPositionForm`) und `reports/euer/<pk>/delete/` (DeleteView).

## 9. Automatische Kategorisierung

> Implementierung in `transactions/services/categorization.py`

```python
def _first_matching_rule(transaction: Transaction, rules) -> FilterRule | None:
    for rule in rules:
        debitor_match = (
            not rule.debitor_contains or
            rule.debitor_contains.lower() in transaction.debitor.lower()
        )
        verwendung_match = (
            not rule.verwendung_contains or
            rule.verwendung_contains.lower() in transaction.verwendung.lower()
        )
        if debitor_match and verwendung_match:
            return rule
    return None


def match_rule(transaction: Transaction) -> FilterRule | None:
    """Returns the first active FilterRule matching the transaction, or None."""
    rules = FilterRule.objects.filter(is_active=True).select_related('category')
    return _first_matching_rule(transaction, rules)


def _assign_rule(transaction: Transaction, rule: FilterRule) -> None:
    if rule.category_id:                      # Kategorie nur falls gesetzt
        TransactionCategory.objects.get_or_create(
            transaction=transaction,
            category=rule.category,
            defaults={'assigned_by': 'auto'},
        )
    TransactionMeta.objects.update_or_create(  # Meta immer (auch ohne Kategorie)
        transaction=transaction,
        defaults={
            'rule': rule,
            'art': rule.art,
            'prioritaet': rule.prioritaet,
            'intervall': rule.intervall,
        },
    )


def auto_categorize(transaction: Transaction) -> None:
    rule = match_rule(transaction)
    if rule:
        _assign_rule(transaction, rule)
```

**Regeln erneut anwenden (`apply_rules_to_all`):**
```python
def apply_rules_to_all() -> dict:
    TransactionCategory.objects.filter(assigned_by='auto').delete()
    TransactionMeta.objects.all().delete()

    rules = FilterRule.objects.filter(is_active=True).select_related('category')
    processed = matched = unmatched = 0
    for tx in Transaction.objects.iterator():
        processed += 1
        rule = _first_matching_rule(tx, rules)
        if rule:
            _assign_rule(tx, rule)
            matched += 1
        else:
            unmatched += 1

    return {'processed': processed, 'matched': matched, 'unmatched': unmatched}
```

**Regel-Reihenfolge:** Durch `ordering = ['name']` (siehe §4.5) werden die
aktiven Regeln alphabetisch geprüft — **die erste passende Regel gewinnt**.
Ein Auto-Lauf findet beim Import neuer Transaktionen statt; bestehende
Zuweisungen werden danach nicht mehr angetastet.

**„Regeln anwenden"-Button** (`action=apply_rules` in der Regelliste):
- Löscht **alle** automatisch zugewiesenen Kategorien und **alle**
  `TransactionMeta`-Einträge und baut sie aus den aktuell aktiven Regeln neu auf
- Manuelle Zuweisungen (`assigned_by='manual'`) bleiben unberührt
- Transaktionen ohne passende Regel werden vollständig unkategorisiert
- Ergebnis als Statistik-Meldung: geprüft / kategorisiert / ohne Treffer

**Manuelle Zuweisung:**
- User kann in `transaction_detail.html` per Formular eine Kategorie setzen
- Ablage als zusätzliche `TransactionCategory` mit `assigned_by='manual'`
  (`get_or_create`, kein Duplikat bei Wiederholung)
- Die Transaktion selbst bleibt unverändert (Immutable-Prinzip)

---

## 10. Vorhersage (Prediction)

> Implementierung in `transactions/services/prediction.py`
>
> Zwei Auslöser:
> - Management-Command: `uv run manage.py update_predictions` (aus `src\finman\`)
> - Link in der Vorhersagen-Liste: `GET /predictions/?refresh=1`
>   (danach Post/Redirect/Get auf die Liste)

**Algorithmus (zweistufige Gruppierung):**
```
1. Gruppe A: alle Transaktionen je Debitor (ohne Kategorie) → key (debitor, None)
2. Gruppe B: zusätzlich je Kategorie-Zuweisung → key (debitor, category_id)
3. Nur Gruppen mit >= 2 verschiedenen Daten verarbeiten
4. Daten deduplizieren und sortieren; Differenzen zwischen
   aufeinanderfolgenden Daten bilden (Tage)
5. avg_interval_days = Mittelwert der Differenzen
6. next_expected_date = letztes Datum + timedelta(days=round(avg))
7. confidence = max(0.0, 1.0 - stdev/avg), gerundet auf 2 Stellen
8. PredictionResult per update_or_create speichern (key: debitor + category)
```

```python
def update_predictions():
    predictions = {}

    for tx in Transaction.objects.order_by('debitor', 'date'):
        key = (tx.debitor, None)
        predictions.setdefault(key, []).append(tx.date)

    for tx in Transaction.objects.order_by('date'):
        cats = tx.categories.select_related('category').all()
        for tc in cats:
            key = (tx.debitor, tc.category.pk)
            predictions.setdefault(key, []).append(tx.date)

    for (debitor, cat_id), dates in predictions.items():
        if len(dates) < 2:
            continue
        dates = sorted(set(dates))
        diffs = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]
        if not diffs:
            continue

        avg = mean(diffs)
        std = stdev(diffs) if len(diffs) > 1 else 0
        confidence = max(0.0, 1.0 - (std / avg)) if avg > 0 else 0.0

        category = Category.objects.get(pk=cat_id) if cat_id is not None else None
        PredictionResult.objects.update_or_create(
            debitor=debitor,
            category=category,
            defaults={
                'next_expected_date': dates[-1] + timedelta(days=int(avg)),
                'avg_interval_days': int(avg),
                'last_occurrence': dates[-1],
                'confidence': round(confidence, 2),
            },
        )
```

> **Hinweis:** Prognosen laufen nicht automatisch nach einem Import — sie werden
> nur per Command oder über den Refresh-Link aktualisiert (Architekturdokument,
> offene Frage T-05).

---

## 11. URL-Struktur

```python
# transactions/urls.py — alle Routen hängen unter '/' (include in finman/urls.py)
urlpatterns = [
    path('',                                   views.dashboard,                    name='dashboard'),
    path('import/',                            views.ImportView.as_view(),         name='import'),
    path('import/history/',                    views.import_history,               name='import_history'),
    path('import/<int:pk>/delete/',            views.ImportDeleteView.as_view(),   name='import_delete'),                 # PIN + CASCADE
    path('transactions/',                      views.TransactionListView.as_view(),          name='transaction_list'),
    path('transactions/<int:pk>/',             views.TransactionDetailView.as_view(),        name='transaction_detail'),
    path('transactions/<int:pk>/meta/',        views.transaction_meta_save,        name='transaction_meta_save'),          # require_POST
    path('transactions/<int:pk>/meta/clear/',  views.transaction_meta_clear,       name='transaction_meta_clear'),         # require_POST
    path('transactions/<int:pk>/category/<int:cat_pk>/remove/',
                                               views.transaction_category_remove,  name='transaction_category_remove'),    # require_POST
    path('categories/',                        views.CategoryListView.as_view(),   name='category_list'),
    path('categories/new/<int:pk>/',           views.CategoryNewSubView.as_view(), name='category_new_sub'),
    path('categories/<int:pk>/edit/',          views.CategoryUpdateView.as_view(), name='category_edit'),
    path('categories/<int:pk>/delete/',        views.CategoryDeleteView.as_view(), name='category_delete'),
    path('rules/',                             views.RuleListView.as_view(),       name='rule_list'),
    path('rules/<int:pk>/edit/',               views.RuleUpdateView.as_view(),     name='rule_edit'),
    path('rules/<int:pk>/delete/',             views.RuleDeleteView.as_view(),     name='rule_delete'),
    path('predictions/',                       views.prediction_list,              name='prediction_list'),
    path('reports/euer/',                      views.report_euer,                  name='report_euer'),
    path('reports/euer/wizard/step1/',         views.EuerWizardStep1View.as_view(),name='euer_wizard_step1'),
    path('reports/euer/wizard/step2/',         views.EuerWizardStep2View.as_view(),name='euer_wizard_step2'),
    path('reports/euer/wizard/step3/',         views.EuerWizardStep3View.as_view(),name='euer_wizard_step3'),
    path('reports/euer/<int:pk>/hint/',        views.EuerPositionHintView.as_view(),name='euer_position_hint'),
    path('reports/euer/<int:pk>/delete/',      views.EuerPositionDeleteView.as_view(),name='euer_position_delete'),
]
```

> Die drei `meta`-/`category`-Endpunkte sind **nur per POST** erreichbar
> (`@require_POST`) und dienen der Schnellbearbeitung aus der Transaktionsliste
> heraus; sie akzeptieren ein `next`-Feld für den Rücksprung (nur relative
> Pfade, Schutz gegen offene Redirects). Kategorien und Regeln werden über
> je drei Class-Based Views abgebildet: Liste (+ Inline-Create via `FormMixin`),
> UpdateView, DeleteView.

---

## 12. GUI-Anforderungen

> Alle Templates erben von `base.html`. Bootstrap 5 via CDN (+ Bootstrap-Icons).
> Formular-Seiten folgen einem einheitlichen Muster: Class-Based Views mit
> `@never_cache`, ModelForms aus `forms.py`, Feedback über
> `django.contrib.messages`, Fehler-Rendering über die Partials
> `_form_alert.html` und `_field_errors.html`.

### 12.1 `base.html`

- Bootstrap 5 CDN (CSS + JS-Bundle) — ohne Internet keine Styles
- Navbar mit Links: Dashboard | Import | Transaktionen | Kategorien | Regeln | Vorhersagen | EÜR-Bericht
- Django-Messages als Alerts (`{% if messages %} … {% endif %}`)
- Template-Blöcke: `title`, `content`, `extra_css`, `extra_js`

### 12.2 `import.html` — `/import/`

**Elemente:**
- **Upload-Bereich:** `<input type="file" accept=".csv">` per Django-Form
- **ODER:** Textfeld für absoluten Dateipfad
  (Formular verlangt genau eine der beiden Angaben; Card-Header „Neuen Import starten“)
- **Nach POST:** Vorschau (erkanntes Format = Parser-Name, Konto, erste 3 Zeilen)
  **und** Ergebnis des Imports: Importiert | Übersprungen | Duplikate — oder
  Fehlermeldung als Message (z. B. Datei-Duplikat, Datei nicht gefunden)

### 12.3 `transaction_list.html` — `/transactions/`

**Filterleiste (`TransactionFilterForm`, GET) im Accordion (eingeklappt, wie „Letzte Imports“):**
- `start` / `end` — Datum von / bis (date inputs)
- `debitor` — text input, icontains
- `category` — Dropdown (nur Hauptkategorien; Filter schließt Subkategorien ein,
  Labels mit `get_full_path()`)
- `art` / `prioritaet` / `intervall` — Dropdowns
- Ungültige Angaben werden verworfen und gemeldet

**Sortier-Dropdown (GET `sort`, Whitelist):**
Neueste zuerst | Älteste zuerst | Betrag absteigend | Betrag aufsteigend |
Debitor A–Z — jeweils mit erhaltenen Filterparametern

**Tabelle (je Zeile zusätzlich zur Schnellbearbeitung):**
Kategorie-Badges (entfernbar) · Art/Priorität-Badges (einzelnt leerbar) ·
Inline-Zeile mit `meta_form`: Kategorie zuweisen + Art/Priorität/Intervall
setzen → POST auf `transaction_meta_save`; Rückkehr über verstecktes `next`-Feld

- Pagination: 50 Einträge pro Seite (ListView)
- **Fußzeile:** Summe `value` aller gefilterten Einträge (positiv = grün, negativ = rot)
- Klick auf eine Zeile öffnet die Detailseite

### 12.4 `transaction_detail.html` — `/transactions/<pk>/`

- Alle Felder der Transaktion anzeigen
- Kategorien als Badges mit Herkunft (auto = blau, manuell = gelb)
- Meta-Anzeige (Art/Priorität/Intervall) mit zugehöriger Regel
- **Meta-Formular** (`TransactionMetaForm`): Kategorie zuweisen,
  Art/Priorität/Intervall setzen/ändern — POST auf `transaction_meta_save`
- **Info-Notiz** (`TransactionInfoForm`, 1:1 `TransactionInfo`):
  Anlegen/Bearbeiten über Akkordeon; POST mit `form_type=info` wird im selben
  Detail-View verarbeitet
- **Manuelle Kategorie** (`ManualCategoryForm`): klassische Zuweisung per
  Dropdown (`assigned_by='manual'`)

### 12.5 `dashboard.html` — `/`

- **KPI-Karten:** Einnahmen diesen Monat | Ausgaben diesen Monat | Saldo
- **Letzte Imports** als Accordion (oben, volle Breite, initiale Anzahl, eingeklappt; Tabelle Datei + Von/Bis + Zeilen + Duplikate; Link „Alle Imports ansehen“)
- **Top-5 Ausgaben** nach Kategorie (aktueller Monat, nur Ausgaben) und **Nächste erwartete Zahlungen** (PredictionResult, die nächsten 10, Confidence-Balken) je `col-md-6`

### 12.6 `report_euer.html` — `/reports/euer/` (EÜR-Positionen)

> Fachlich: Bericht filtert nach `EuerPosition.year` (nicht `Transaction.date`) – Januar-Buchungen können so dem abgelaufenen Jahr zugeordnet werden. `EuerPositionForm` erlaubt Kategorie/Art/Intervall/Priorität/Hinweis je Position; leere Transaktionsfelder erben Positionswerte, abweichende zeigen Warnicon.

- Jahresauswahl via GET `year` (aktuelles Jahr vorausgewählt, `year - 5` bis `year + 2`) + Button „Position anlegen (Wizard)“
- **Positionen-Tabelle (14 Spalten, ohne ROI):** Position (+ Warnicon) | Betrag (Σ) | Kategorie | Sub-Kategorie | Typ | Intervall | Priorität | Hinweis (editierbar, `euer_hint_form.html` mit vollem `EuerPositionForm`) | Betrag täglich / wöchentlich / monatlich / jährlich (siehe §9a) | wird gezahlt über | Aktionen (Bearbeiten → Wizard `?edit=`, Löschen)
- Footer: Summen über alle Positionen des Jahres (je normalisierte Spalte)
- Wizard `euer_wizard_step1/2/3.html`: 1) Stammdaten, 2) Transaktionen zuweisen (500 neueste, year'seigene ausgenommen, beim Bearbeiten vorausgewählt), 3) Vorschau mit Warnungen → Speichern setzt `pos.transactions`
- Export als CSV/PDF: **nicht implementiert** (siehe §15)

### 12.7 Regel-Seiten — `/rules/`

- **Liste + Anlegen** (`RuleListView`, `FormMixin` + `FilterRuleForm`):
  Tabelle aller Regeln mit Kategorie, Art, Intervall und Aktiv-Status;
  Inline-Formular zum Anlegen (Akkordeon). Validierung: Name Pflicht,
  **mindestens ein Suchbegriff** (Debitor oder Verwendung) erforderlich
- **POST-Aktionen** im selben View:
  - `action=create` — Formular speichern
  - `action=toggle` (`rule_id`) — Aktiv/Inaktiv umschalten
  - `action=apply_rules` — `apply_rules_to_all()` ausführen (siehe §9),
    Statistik als Message
- **Bearbeiten** (`RuleUpdateView`, `rule_form.html`)
- **Löschen** (`RuleDeleteView`, `rule_confirm_delete.html`): Bestätigungsseite
  zeigt die Anzahl verknüpfter `TransactionMeta`; beim Löschen wird nur die
  Verknüpfung entfernt (`SET_NULL`), Transaktionen bleiben unverändert

### 12.8 `prediction_list.html` — `/predictions/`

- Tabelle sortiert nach `next_expected_date`: Debitor, Kategorie,
  nächstes erwartetes Datum, Ø-Intervall in Tagen, letztes Vorkommen, Confidence
- Refresh-Link (`?refresh=1`) löst `update_predictions()` aus und leitet
  per Redirect auf die Liste zurück

### 12.9 `import_history.html` — `/import/history/`

- Tabelle aller Importe (neueste zuerst): Dateiname (voll, `word-break`), Konto (voll), Datum/Uhrzeit, Zeilen gesamt, Duplikate, Von (`min_date`) / Bis (`max_date`) getrennt, Papierkorb-Spalte ohne Header – Schrift kleiner (`thead 0.75rem / tbody 0.60rem`); erreichbar via Import-Dropdown und Dashboard-Link. Löschseite `import_confirm_delete.html` mit PIN-Abfrage (`FINMAN_DELETE_PIN`, Default `1234`).

### 12.10 Kategorie-Seiten — `/categories/`

- **Liste + Anlegen** (`CategoryListView`, `FormMixin`): verschachtelter Baum
  über das rekursive Partial `_category_node.html`; Zähler (Haupt-/Gesamtanzahl);
  Inline-Formular (`CategoryForm`: name, parent). Validierung: Name Pflicht,
  **kein Doppelname** unter demselben Parent bzw. auf oberster Ebene;
  nach dem Anlegen Sprung zum Anker der neuen Kategorie (`#cat-<pk>`)
- **Subkategorie anlegen** (`CategoryNewSubView`): Button an jeder Haupt-
  kategorie; Parent wird fixiert und serverseitig erzwungen
- **Bearbeiten** (`CategoryUpdateView`, `category_form.html`):
  Parent-Auswahl nur Hauptkategorien; die Kategorie selbst ist ausgeschlossen
  (Zyklen verhindern)
- **Löschen** (`CategoryDeleteView`, `category_confirm_delete.html`) mit
  Sperren — Löschen wird verweigert mit Begründung, wenn die Kategorie
    - von Transaktionen verwendet wird (`TransactionCategory`),
    - in Filter-Regeln referenziert wird oder
    - Subkategorien besitzt

---

## 13. Initiale Daten

Es existieren **keine Fixtures** im Repository (`loaddata` ist nicht nötig).

Haupt- und Subkategorien sowie Filter-Regeln werden manuell angelegt:
- UI: `/categories/` (Anlegen/Bearbeiten/Löschen) und `/rules/` (Anlegen/Aktivieren)
- Alternativ: Django Admin unter `/admin/`

---

## 14. Django-Einstellungen

```python
# finman/settings.py (relevante Einstellungen)
import os
IMPORT_DELETE_PIN = os.environ.get("FINMAN_DELETE_PIN", "1234")  # PIN für Import-Löschung

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
SECRET_KEY = 'django-insecure-local-dev-key-change-in-production'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'transactions',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR.parent / 'db.sqlite3',   # → src/db.sqlite3
    }
}

AUTH_PASSWORD_VALIDATORS = []          # lokal ohne Login nicht erforderlich

LANGUAGE_CODE = 'de-de'
TIME_ZONE = 'Europe/Berlin'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```

**Logging (Parser/Import):**
```python
LOGGING = {
    'version': 1,
    'formatters': {
        'verbose': {'format': '{asctime} | {levelname:8} | {name:40} | {message}', 'style': '{'},
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'formatter': 'verbose'},
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR.parent.parent / 'logs' / 'parser_import.log',
            'formatter': 'verbose', 'encoding': 'utf-8',
        },
    },
    'loggers': {
        'transactions': {'handlers': ['console', 'file'], 'level': 'DEBUG', 'propagate': False},
    },
}
```

> Logging-Meldungen im Code sind englischsprachig, UI-Strings deutsch.

---

## 15. Offene Punkte

> Gelöste Punkte der ursprünglichen Spezifikation: CSV-Beispieldateien liegen
> unter `doc/giro_beispiel.csv` und `doc/visa_beispiel.csv`; das `src_konto`
> wird aus den Meta-Zeilen der DKB-Exporte gelesen (§5.3). Technische Schulden
> und Design-Fragen sind im Architekturdokument gesammelt
> ([§8 Offene Technische Fragen](finman_architecture.md#8-offene-technische-fragen)).

| #  | Offener Punkt                                                                 | Status |
|---|---|---|
| 1  | EÜR-Bericht als PDF exportierbar?                                              | `Offen` |
| 2  | EÜR-Bericht als CSV exportieren (optionales Feature laut §12.6)                | `Offen` |
| 3  | Mehrere Konten unterscheiden/filtern — `src_konto` wird je Transaktion gespeichert, aber es gibt noch keinen Konto-Filter in Liste/Dashboard | `Teilweise umgesetzt` |
| 4  | `TransactionInfo` ist im Django-Admin nicht registriert (alle übrigen Modelle sind es) | `Offen` |

---

*Spezifikation erstellt am: 2026-05-05*
*Aktualisiert am: 2026-08-26 · Version: 2.1*
