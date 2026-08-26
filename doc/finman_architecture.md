# finman — Architecture

**Version:** 1.1
**Status:** `Draft`
**Erstellt:** 2026-08-26
**Zuletzt aktualisiert:** 2026-08-26

---

## Changelog

| Version | Datum      | Änderung |
| ------- | ---------- | -------- |
| 1.1     | 2026-08-26 | An überarbeiteten Code angeglichen: FormView-/ListView-Umbau, `TransactionInfo`, Regel-CRUD + „Regeln anwenden" (neuer Ablauf §4.7), Meta-Schnellbearbeitung, 17 Routen |
| 1.0     | 2026-08-26 | Initiale Version |

---

## KI-Kontext

```
Zweck           : Wie die finman-App konkret funktioniert —
                  CSV-Import, automatische Kategorisierung, Prognosen,
                  EÜR-Bericht. Kein Ersatz für Code-Kommentare oder
                  vollständige Doku.
Fachliches Was  : doc/euer_manager_spec.md (Ist-Stand, v2.0)
Feature-Details : —
Verwandter Code : src/finman/
```

> **Hinweis zum Umfang:** Dieses Dokument beschreibt den Ist-Zustand aus dem Code.
> Es zeigt nur, was andere Docs nicht zeigen können — konkrete Abläufe und
> Strukturen als Diagramme. Kein Code im Dokument.

---

## 1. Systemübersicht

> Lokal laufende Django-Webapp zur Verwaltung der Einnahmen-Überschuss-Rechnung.
> Ein Nutzer bedient die App im Browser; Bank-CSV-Exporte werden importiert;
> alle Daten liegen in einer lokalen SQLite-Datei.

```mermaid
flowchart TD
    Nutzer([Nutzer])

    subgraph Local ["Lokaler Rechner · Python 3.13 · uv"]
        Django["Django Webapp 'finman'<br/>runserver · DEBUG=True"]
        DB[("SQLite<br/>db.sqlite3")]
        LogFile["logs/parser_import.log"]
        Cmd["Management-Command<br/>update_predictions"]
    end

    Browser(["Browser<br/>Server-gerenderte Templates<br/>Bootstrap 5 via CDN"])
    Admin(["Django Admin<br/>/admin/"])
    Exports(["CSV-Exporte der Bank<br/>DKB Giro · DKB Visa · sonstige"])

    Nutzer --> Browser
    Nutzer --> Admin
    Nutzer --> Cmd
    Browser <-->|"HTTP · localhost"| Django
    Admin <--> Django
    Exports -->|"Datei-Upload oder<br/>lokaler Dateipfad"| Django
    Django -->|"ORM"| DB
    Django -->|"Parser-/Import-Logs"| LogFile
    Cmd -->|"Prognosen aktualisieren"| Django
```

---

## 2. Bausteine & Schichten

> Eine einzige Django-App `transactions` trägt alle Fachlichkeit.
> Schichtung: URLs → Views → Services → Models. Das Parser-Paket kapselt
> die bankenspezifischen CSV-Formate.

```mermaid
flowchart LR
    subgraph Config ["Projektkonfiguration · finman"]
        Settings["settings.py<br/>SQLite · Logging · de-de · Europe/Berlin"]
        RootUrls["urls.py"]
        WSGI["wsgi.py"]
    end

    subgraph App ["Django-App · transactions"]
        Urls["urls.py<br/>17 Routen unter '/'"]
        Views["views.py<br/>7 function-based · 10 class-based"]
        Forms["forms.py<br/>7 Formen + CategoryChoiceField:<br/>TransactionFilterForm · FilterRuleForm ·<br/>TransactionMetaForm · TransactionInfoForm …"]
        Models["models.py<br/>8 Modelle"]
        AdminCfg["admin.py<br/>7 von 8 Modellen registriert"]
        Commands["management/commands/<br/>update_predictions"]

        subgraph ServicesLayer ["services · Fachlogik"]
            Importer["importer.py<br/>import_csv · Tempdatei-Helfer"]
            Categorization["categorization.py<br/>auto_categorize ·<br/>apply_rules_to_all"]
            FilterService["filter_service.py<br/>TransactionFilter"]
            Prediction["prediction.py<br/>update_predictions"]
        end

        subgraph Parsers ["parsers · CSV-Erkennung"]
            Registry["registry.py<br/>get_parser"]
            BaseP["base_parser.py<br/>BaseCSVParser ABC · TransactionData ·<br/>Hashing · parse_german_number"]
            Giro["giro_parser.py<br/>GiroDKBCSVParser"]
            Visa["visa_parser.py<br/>VisaDKBCSVParser"]
            Generic["generic.py<br/>GenericCSVParser"]
        end
    end

    Templates["templates/transactions/<br/>base.html + 13 Seiten<br/>+ 3 Partials (_form_alert, _field_errors,<br/>_category_node)"]

    RootUrls --> Urls
    Urls --> Views
    Views --> Forms
    Views --> Templates
    Views -->|"Listen-Filterung"| FilterService
    Views -->|"Import"| Importer
    Views -->|"Refresh-Link"| Prediction
    Views -->|"Preview"| Registry
    Views -->|"Regeln anwenden"| Categorization
    Importer --> Registry
    Importer --> BaseP
    Importer --> Categorization
    Registry --> Giro
    Registry --> Visa
    Registry --> Generic
    Giro --> BaseP
    Visa --> BaseP
    Generic --> BaseP
    Importer --> Models
    Categorization --> Models
    FilterService --> Models
    Prediction --> Models
    AdminCfg --> Models
    Commands --> Prediction
```

> **Konvention:** Views enthalten nur HTTP-Aufbereitung (Forms, Pagination,
> Aggregationen fürs Template). Wiederverwendbare Fachlogik liegt in `services/`,
> Formatwissen in `parsers/`. Ausnahmen: die Detail-Ansicht und die drei
> Quick-Edit-Endpunkte der Liste schreiben manuelle Kategorien bzw.
> `TransactionMeta` direkt über das ORM (siehe §4.4).

---

## 3. Datenmodell

> Sieben Kernmodelle plus `TransactionInfo`. Zentral ist `Transaction`
> (dedupliziert über SHA-256-Hash). Kategorien hängen n:m über
> `TransactionCategory`; `TransactionMeta` speichert als Snapshot, welche Regel
> welche Attribute (Art/Priorität/Intervall) gesetzt hat; `TransactionInfo`
> hält eine freie Notiz je Transaktion.

```mermaid
erDiagram
    IMPORT_HISTORY ||--o{ TRANSACTION : "import_file"
    TRANSACTION ||--o| TRANSACTION_META : "meta"
    TRANSACTION ||--o| TRANSACTION_INFO : "info"
    TRANSACTION ||--o{ TRANSACTION_CATEGORY : "categories"
    CATEGORY ||--o{ TRANSACTION_CATEGORY : "category"
    CATEGORY ||--o{ FILTER_RULE : "category"
    FILTER_RULE ||--o{ TRANSACTION_META : "rule"
    CATEGORY ||--o{ PREDICTION_RESULT : "category"
    CATEGORY ||--o{ CATEGORY : "parent"

    IMPORT_HISTORY {
        string file_md5 UK "unique"
        string filename
        string konto
        datetime imported_at
        int row_count
        int duplicate_count
        date min_date
        date max_date
    }
    TRANSACTION {
        string hash UK "SHA-256, unique"
        date date
        decimal value
        string status
        string debitor
        text verwendung
        string src_konto
        string target_konto
        string debitor_id
        string mandats_ref
        string customer_ref
        datetime imported_at
    }
    CATEGORY {
        string name
    }
    TRANSACTION_CATEGORY {
        string assigned_by "auto oder manual"
        datetime assigned_at
    }
    FILTER_RULE {
        string name
        string debitor_contains
        string verwendung_contains
        string art "FIX oder FLEX, optional"
        string prioritaet "optional"
        string intervall "optional"
        bool is_active
    }
    TRANSACTION_META {
        string art
        string prioritaet
        string intervall
    }
    TRANSACTION_INFO {
        text text
        datetime updated_at
    }
    PREDICTION_RESULT {
        string debitor
        date next_expected_date
        int avg_interval_days
        date last_occurrence
        float confidence
        datetime predicted_at
    }
```

> **Wesentliche Regeln:**
>
> - `Category` ist hierarchisch (`parent` auf sich selbst); `get_descendants()`
>   liefert die gesamte Teilbaum-ID-Liste — genutzt beim Filtern und bei der
>   Lösch-Sperre.
> - `Transaction.hash` (SHA-256 über Datum, Debitor, Betrag, Verwendung,
>   Ziel-/Quellkonto) verhindert Zeilen-Duplikate; `ImportHistory.file_md5`
>   verhindert Datei-Duplikate (siehe §5.2).
> - `TransactionMeta` ist ein 1:1-Snapshot pro Transaktion und verweist optional
>   auf die auslösende `FilterRule`.
> - `PredictionResult` ist ein berechneter Datensatz, der über `(debitor,
>   category)` eindeutig bestimmt wird — nicht über eine FK zu `Transaction`.
> - `TransactionInfo` ist eine freie Nutzer-Notiz (1:1), losgelöst von
>   Kategorien/Regeln; gepflegt über die Detailseite.
> - Löschen von `Category`, `FilterRule`, `Transaction` setzt Referenzen auf
>   `NULL` bzw. kaskadiert nur bei den Assoziationstabellen.

---

## 4. Schlüssel-Abläufe

### 4.1 CSV-Import End-to-End

> Der wichtigste Ablauf: Von Upload/Pfad bis zur kategorisierten Transaktion.
> Zeigt das Zusammenspiel ImportView → Parser-Preview → Importer → Auto-Kategorisierung.

```mermaid
sequenceDiagram
    actor Nutzer
    participant IV as ImportView (FormView)
    participant Imp as services.importer
    participant Parser as Parser (via get_parser)
    participant Cat as auto_categorize
    participant DB as SQLite

    Nutzer->>IV: POST /import/<br/>(Datei oder Dateipfad)
    IV->>IV: ImportForm validieren<br/>(genau eine der beiden Angaben)
    IV->>Imp: save_upload_to_temp(upload)<br/>oder Pfad prüfen
    alt Pfad existiert nicht
        IV-->>Nutzer: messages.error + Formular erneut
    end

    IV->>Parser: get_parser(filepath)
    Parser-->>IV: Parser-Instanz
    IV->>Parser: get_meta_info(filepath)
    Parser-->>IV: Konto + 3 Vorschauzeilen

    IV->>Imp: import_csv(filepath, original_filename)

    Imp->>DB: file_md5 (MD5) bereits in ImportHistory?
    alt Datei schon importiert
        DB-->>Imp: Treffer
        Imp-->>IV: ValueError mit Ursprungsdatum
        IV-->>Nutzer: messages.error
    else Neue Datei
        DB-->>Imp: kein Treffer
        Imp->>Parser: parse(filepath)
        Parser-->>Imp: list[TransactionData]
        Imp->>DB: ImportHistory anlegen<br/>(md5, original_filename)
        loop für jede Transaktion
            Imp->>Imp: compute_transaction_hash<br/>(SHA-256 über 6 Felder)
            alt Hash existiert bereits
                Imp->>Imp: Zeile überspringen,<br/>duplicate_count++
            else Neue Transaktion
                Imp->>DB: Transaction speichern
                Imp->>Cat: auto_categorize(tx)
                Cat->>Cat: match_rule(tx)<br/>(erste passende aktive Regel)
                alt Regel gefunden
                    Cat->>DB: TransactionCategory<br/>(nur falls rule.category_id)
                    Cat->>DB: TransactionMeta<br/>(Snapshot + Regelreferenz)
                else keine Regel
                    Cat->>DB: nichts gespeichert
                end
            end
        end
        Imp->>DB: ImportHistory finalisieren<br/>(row_count, duplicates, Zeitraum, Konto)
        Imp-->>IV: {imported, skipped, duplicates, import_id}
    end

    IV->>IV: cleanup_temp(filepath)<br/>(finally — nur eigene Tempdateien)
    IV-->>Nutzer: Ergebnisseite<br/>(Vorschau + Statistik)
```

### 4.2 Parser-Auswahl zur Laufzeit

> Die Detect-Kette: Die Registry probiert die Parser in Listenreihenfolge;
> der erste Treffer gewinnt, der Generic-Parser fängt alles übrige ab.

```mermaid
sequenceDiagram
    participant Caller as Aufrufer<br/>(View oder Importer)
    participant Reg as registry.get_parser
    participant Giro as GiroDKBCSVParser
    participant Visa as VisaDKBCSVParser
    participant Gen as GenericCSVParser

    Caller->>Reg: get_parser(filepath)
    Reg->>Giro: detect(filepath)
    Note over Giro: liest Zeile 1 (utf-8-sig)<br/>Prüft Präfix 'Girokonto;'
    alt Zeile 1 beginnt mit 'Girokonto;'
        Giro-->>Reg: True
        Reg-->>Caller: GiroDKBCSVParser
    else kein Treffer
        Reg->>Visa: detect(filepath)
        Note over Visa: Prüft Präfix 'Karte;'
        alt Zeile 1 beginnt mit 'Karte;'
            Visa-->>Reg: True
            Reg-->>Caller: VisaDKBCSVParser
        else kein Treffer
            Reg->>Gen: detect(filepath)
            Note over Gen: gibt immer True zurück<br/>(Fallback)
            Gen-->>Reg: True
            Reg-->>Caller: GenericCSVParser
        end
    end
```

### 4.3 Automatische Kategorisierung

> Läuft pro neu importierter Transaktion. Erste passende aktive Regel gewinnt;
> die Reihenfolge ergibt sich alphabetisch aus `ordering = ['name']`.

```mermaid
sequenceDiagram
    participant Imp as importer.import_csv
    participant Cat as auto_categorize<br/>(categorization.py)
    participant Rules as FilterRule (aktiv)
    participant DB as SQLite

    Imp->>Cat: auto_categorize(tx)
    Cat->>Cat: match_rule(tx)
    Cat->>Rules: alle is_active=True<br/>(sortiert nach name)
    loop Regel für Regel (_first_matching_rule)
        Cat->>Cat: debitor_contains in tx.debitor?<br/>(case-insensitive, leer = Platzhalter)
        Cat->>Cat: verwendung_contains in tx.verwendung?<br/>(case-insensitive, leer = Platzhalter)
    end
    alt Regel gefunden
        Cat->>DB: _assign_rule(tx, rule)
        alt rule.category_id gesetzt
            Cat->>DB: TransactionCategory get_or_create<br/>(assigned_by='auto')
        else nur Attribute ohne Kategorie
            Cat->>DB: keine Kategorie-Zuweisung
        end
        Cat->>DB: TransactionMeta update_or_create<br/>(rule, art, prioritaet, intervall)<br/>— immer, auch ohne Kategorie
    else keine Regel
        Cat->>DB: nichts gespeichert
    end
```

### 4.4 Manuelle Zuweisung und Schnellbearbeitung

> Zwei Wege: Die Detailseite (Kategorie + Meta + Info-Notiz) und die drei
> `require_POST`-Endpunkte für die Schnellbearbeitung aus der Liste heraus.

```mermaid
sequenceDiagram
    actor Nutzer
    participant DV as TransactionDetailView<br/>(DetailView + FormMixin)
    participant Form as ManualCategoryForm /<br/>TransactionInfoForm
    participant DB as SQLite

    Nutzer->>DV: GET /transactions/pk/
    DV->>DB: Transaction + Kategorien + Meta + Info laden
    DV-->>Nutzer: Detailseite (3 Formulare)

    Nutzer->>DV: POST (form_type=info)
    DV->>Form: TransactionInfoForm validieren
    alt gültig
        DV->>DB: TransactionInfo update_or_create<br/>(1:1, updated_at automatisch)
        DV-->>Nutzer: Redirect + messages.success
    else ungültig
        DV-->>Nutzer: Seite mit Fehlermeldungen erneut
    end

    Nutzer->>DV: POST (form_type=category)
    DV->>Form: ManualCategoryForm validieren
    DV->>DB: TransactionCategory get_or_create<br/>(assigned_by='manual')
    Note over DB: get_or_create — Wiederholung<br/>erzeugt kein Duplikat
    DV-->>Nutzer: Redirect auf Detailseite
```

**Quick-Edit-Endpunkte (nur POST, Rücksprung über `next`-Feld):**

| Endpunkt | Wirkung |
|---|---|
| `/transactions/<pk>/meta/` | `TransactionMeta` setzen (art/prioritaet/intervall) + optional Kategorie zuweisen (`assigned_by='manual'`) |
| `/transactions/<pk>/meta/clear/` | Einzelnes Feld (`art` oder `prioritaet`) leeren |
| `/transactions/<pk>/category/<cat_pk>/remove/` | Kategorie-Zuweisung löschen |

> Die Endpunkte schreiben direkt per ORM; das `next`-Feld wird nur bei
> relativen Pfaden akzeptiert (Schutz vor offenen Redirects).

### 4.5 Prognosen aktualisieren

> Zwei Auslöser: Management-Command oder Refresh-Parameter in der Vorhersagen-
> Liste. Gruppiert nach Debitor (gesamt) und Debitor je Kategorie, bildet
> Intervallstatistik und überschreibt `PredictionResult`.

```mermaid
sequenceDiagram
    participant Trigger as Command update_predictions<br/>oder GET /predictions/?refresh=1
    participant Pred as update_predictions
    participant DB as SQLite

    Trigger->>Pred: update_predictions()
    Pred->>DB: alle Transaktionen lesen
    Pred->>Pred: Gruppe A: Daten je (debitor, ohne Kategorie)<br/>Gruppe B: Daten je (debitor, category)
    loop jede Gruppe mit ≥ 2 verschiedenen Daten
        Pred->>Pred: Intervall-Differenzen bilden<br/>mean(diffs), stdev(diffs)
        Pred->>Pred: confidence = max(0, 1 − stdev/mean)<br/>next = letztes Datum + Ø-Intervall
        Pred->>DB: PredictionResult update_or_create<br/>(key: debitor + category)
    end
    Pred-->>Trigger: fertig
    Note over Trigger: Bei refresh=1: Redirect auf<br/>/predictions/ (Post/Redirect/Get)
```

### 4.6 Transaktionsliste filtern

> GET-getriebene Filterkette über den Fluent Builder, validiert durch das
> `TransactionFilterForm`; ListView übernimmt Pagination und Summen-Aggregation.

```mermaid
sequenceDiagram
    actor Nutzer
    participant LV as TransactionListView<br/>(ListView)
    participant Form as TransactionFilterForm
    participant TF as TransactionFilter
    participant DB as SQLite

    Nutzer->>LV: GET /transactions/?start=&end=&debitor=&category=&art=...
    LV->>Form: GET-Parameter binden
    alt Parameter vorhanden aber ungültig
        Form-->>LV: invalid → verwerfen
        LV-->>Nutzer: messages.error,<br/>ungefilterte Liste
    end
    LV->>TF: new TransactionFilter()
    LV->>TF: by_date_range(start, end)
    LV->>TF: by_debitor(name)
    LV->>TF: by_category(category.pk)
    Note over TF: inkl. get_descendants()<br/>(ganzer Teilbaum)
    LV->>TF: by_art / by_prioritaet / by_intervall
    LV->>TF: apply()
    TF-->>LV: distinctes QuerySet
    LV->>LV: order_by(sort)<br/>(Whitelist SORT_FIELDS,<br/>Default '-date')
    LV->>DB: paginate_by = 50<br/>Sum(value) über Gesamtmenge
    DB-->>LV: Seite + Gesamtsumme
    LV-->>Nutzer: Liste mit Filterleiste, Sortier-Dropdown<br/>und Inline-Meta-Bearbeitung je Zeile
```

### 4.7 Regeln erneut anwenden

> Button „Regeln anwenden" in der Regelliste (`action=apply_rules`) ruft
> `apply_rules_to_all()` auf: Alle Auto-Zuweisungen und alle Metadaten werden
> gelöscht und aus den aktuell aktiven Regeln neu aufgebaut. Manuelle
> Zuweisungen bleiben unberührt.

```mermaid
sequenceDiagram
    actor Nutzer
    participant RL as RuleListView
    participant App as apply_rules_to_all<br/>(categorization.py)
    participant DB as SQLite

    Nutzer->>RL: POST /rules/ (action=apply_rules)
    RL->>App: apply_rules_to_all()
    App->>DB: TransactionCategory löschen<br/>(nur assigned_by='auto')
    Note over DB: manuelle Zuweisungen bleiben erhalten
    App->>DB: TransactionMeta vollständig löschen<br/>(wird nur von auto_categorize geschrieben)
    App->>DB: aktive FilterRule laden<br/>(sortiert nach name)
    loop jede Transaktion (iterator)
        App->>App: _first_matching_rule(tx, rules)
        alt Regel gefunden
            App->>DB: _assign_rule(tx, rule)<br/>(Kategorie + Meta neu aufgebaut)
        else keine Regel
            App->>App: unmatched++
            Note over DB: Transaktion bleibt unkategorisiert
        end
    end
    App-->>RL: {processed, matched, unmatched}
    RL-->>Nutzer: Redirect + Statistik-Message
```

---

## 5. Patterns & Zusammenhänge

### 5.1 Strategy + Registry (CSV-Parser)

> Jede Bankdatei-Form ist eine Strategy hinter der gemeinsamen Schnittstelle
> `BaseCSVParser`; die Registry hält eine geordnete Liste und wählt per
> `detect()` aus. Der Generic-Parser ist bewusst der letzte Eintrag (Fallback).

```mermaid
flowchart TD
    Start["get_parser(filepath)"] --> D1{"GiroDKBCSVParser.detect()<br/>Zeile 1 beginnt mit 'Girokonto;'?"}
    D1 -->|ja| M1["GiroDKBCSVParser"]
    D1 -->|nein| D2{"VisaDKBCSVParser.detect()<br/>Zeile 1 beginnt mit 'Karte;'?"}
    D2 -->|ja| M2["VisaDKBCSVParser"]
    D2 -->|nein| M3["GenericCSVParser<br/>detect() = True · Fallback"]
    M1 --> Out["parse() → list[TransactionData]<br/>get_meta_info() → Vorschau<br/>deutsche Zahlenformate via parse_german_number"]
    M2 --> Out
    M3 --> Out

    subgraph Contract ["BaseCSVParser · Vertrag für alle Parser"]
        direction LR
        C1["detect() · parse() · get_meta_info()"]
        C2["TransactionData · neutrale Dataclass<br/>kein ORM"]
        C3["compute_transaction_hash · compute_file_md5"]
    end

    Out -.-> Contract
```

> **Erweiterungspunkt:** Neues Bankformat = neue Unterklasse von
> `BaseCSVParser` + Eintrag in `PARSERS` **vor** `GenericCSVParser`.
> Sonst greift der Fallback zuerst.

### 5.2 Zweistufige Duplikaterkennung

> Ebene 1 bricht den ganzen Import ab (gleiche Datei), Ebene 2 filtert
> einzelne Zeilen heraus (überlappende Zeitraum-Exporte).

```mermaid
flowchart TD
    A["CSV-Datei eingegangen"] --> B{"MD5 der Datei bereits<br/>in ImportHistory?"}
    B -->|ja| X["Import abgelehnt<br/>ValueError mit Ursprungsdatum"]
    B -->|nein| C["Datei parsen"]
    C --> D{"SHA-256-Hash der Transaktion<br/>(Datum · Debitor · Betrag · Verwendung ·<br/>Zielkonto · Quellkonto)<br/>bereits vorhanden?"}
    D -->|ja| E["Zeile überspringen<br/>duplicate_count++"]
    D -->|nein| F["Transaction speichern"]
    F --> G["auto_categorize(tx)"]
    E --> H["nächste Zeile"]
    G --> H
```

### 5.3 Service-Schichtung

> Wer ruft welche Fachlogik? Views nutzen drei Services direkt, der
> Management-Command teilt sich `update_predictions` mit der Vorhersagen-View.
> Der Importer ist der einzige Orchestrator und ruft seinerseits Services auf.

```mermaid
flowchart LR
    subgraph Callers ["Aufrufer"]
        V["views.py<br/>(Import-, Listen-, Regel-Views)"]
        CMD["management command<br/>update_predictions"]
    end

    subgraph SVC ["services"]
        IMP["import_csv + Tempdatei-Helfer<br/>Orchestrierung Import"]
        CAT["auto_categorize ·<br/>apply_rules_to_all"]
        FLT["TransactionFilter<br/>QuerySet-Builder"]
        PRD["update_predictions<br/>Intervall-Statistik"]
    end

    subgraph DATA ["Datenzugriff"]
        ORM["Django ORM<br/>8 Modelle"]
        DIRECT["Views schreiben zusätzlich<br/>direkt per ORM:<br/>· manuelle Kategorie-Zuweisung (Detail)<br/>· Meta-Schnellbearbeitung (3 POST-Endpunkte)<br/>· Category/Rule CRUD (CBVs)"]
    end

    V --> IMP
    V -->|"Listen-Filterung"| FLT
    V -->|"Refresh-Link"| PRD
    V -->|"action=apply_rules"| CAT
    CMD --> PRD
    IMP --> CAT
    IMP --> ORM
    CAT --> ORM
    FLT --> ORM
    PRD --> ORM
    DIRECT -.-> ORM
```

### 5.4 Fluent Filter Builder

> `TransactionFilter` verpackt ein QuerySet in verkettbare Methoden.
> Leere/leere-artige Parameter ändern das QuerySet nicht; jede Methode gibt
> `self` zurück, `apply()` liefert das finale `distinct()`-QuerySet.

```mermaid
flowchart LR
    New["new TransactionFilter()<br/>qs = alle Transaktionen"] --> DR["by_date_range(start, end)<br/>nur wenn beide gesetzt"]
    DR --> DEB["by_debitor(name)<br/>icontains, nur wenn nicht leer"]
    DEB --> CATF["by_category(id)<br/>erweitert um get_descendants()<br/>→ ganzer Kategorie-Teilbaum"]
    CATF --> ART["by_art(art)"]
    ART --> PRI["by_prioritaet(prio)"]
    PRI --> INT["by_intervall(intervall)"]
    INT --> APPL["apply()<br/>→ distinct()"]
    APPL --> USE["Views sortieren, aggregieren<br/>und paginieren das Ergebnis"]
```

---

## 6. Routing & Navigation

> Alle Fach-Routen hängen unter `/` (include der App-URLs). Die Navbar in
> `base.html` spiegelt die sieben Hauptseiten; Historie, Detail, Quick-Edit-
> Endpunkte sowie Regel-/Kategorie-Unterseiten sind ohne eigenen Nav-Eintrag.

```mermaid
flowchart LR
    NAV(["Navbar · base.html"])

    subgraph Pages ["transactions/urls.py · 17 Routen"]
        direction TB
        P1["'' · Dashboard"] --> V1["dashboard"] --> T1["dashboard.html"]
        P2["/import/ · Import"] --> V2["ImportView<br/>(FormView)"] --> T2["import.html"]
        P3["/import/history/ · Historie"] --> V3["import_history"] --> T3["import_history.html"]
        P4["/transactions/ · Liste"] --> V4["TransactionListView<br/>(ListView · paginate_by=50)"] --> T4["transaction_list.html"]
        P5["/transactions/&lt;pk&gt;/ · Detail"] --> V5["TransactionDetailView<br/>(DetailView + FormMixin)"] --> T5["transaction_detail.html"]
        P5B["POST: /meta/ · /meta/clear/<br/>· /category/&lt;cat_pk&gt;/remove/"] -.->|"require_POST<br/>+ next-Redirect"| V4
        P6["/categories/ · Liste + new/&lt;pk&gt;/ +<br/>edit/ + delete/"] --> V6["CategoryListView<br/>CategoryNewSubView<br/>CategoryUpdateView<br/>CategoryDeleteView"] --> T6["category_list.html<br/>category_form.html<br/>category_confirm_delete.html"]
        P7["/rules/ · Liste + &lt;pk&gt;/edit/ +<br/>&lt;pk&gt;/delete/"] --> V7["RuleListView<br/>RuleUpdateView<br/>RuleDeleteView"] --> T7["rule_list.html<br/>rule_form.html<br/>rule_confirm_delete.html"]
        P8["/predictions/ · Vorhersagen"] --> V8["prediction_list"] --> T8["prediction_list.html"]
        P9["/reports/euer/ · EÜR-Bericht"] --> V9["report_euer"] --> T9["report_euer.html"]
    end

    ADMIN["/admin/ · Django Admin<br/>7 von 8 Modellen"]

    NAV --> P1
    NAV --> P2
    NAV --> P4
    NAV --> P6
    NAV --> P7
    NAV --> P8
    NAV --> P9
```

---

## 7. Zustandsdiagramme

Entfallen bewusst. Keine der Entitäten besitzt einen Status-Feld-Lebenszyklus
(`Transaction.status` ist ein Rohdatenfeld aus dem CSV, kein Workflow-Status);
auch der Import ist ein einmaliger Batch-Vorgang ohne persistenten Zustand —
seine Schritte sind in §4.1 und §5.2 vollständig beschrieben.

---

## 8. Offene Technische Fragen

> Technische Entscheidungen, die noch ausstehen.
> Entschiedene Fragen nicht löschen — Status auf `Entschieden: [Begründung]` setzen.

| #    | Frage                                                                                                                                                  | Status  |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | ------- |
| T-01 | `SECRET_KEY` und `DEBUG=True` sind hart codiert. Für reinen Lokalbetrieb akzeptabel — fehlt aber ein Profil/Mechanismus, falls die App doch exponiert wird? | `Offen` |
| T-02 | `GenericCSVParser.parse(column_mapping)` bietet Spalten-Mapping an — der Importer nutzt es nie. Fremdformate laufen daher ohne Zuordnung ins Leere.          | `Offen` |
| T-03 | Der Import-View durchläuft die Parser-Kette zweimal (Vorschau + erneut im Importer). Detect-Ergebnis cachen oder Vorschau aus dem Importer liefern?         | `Offen` |
| T-04 | Import läuft ohne `transaction.atomic`: ein Fehler mittendrin hinterlässt Teilimporte plus angelegten `ImportHistory`-Eintrag.                              | `Offen` |
| T-05 | Prognosen aktualisieren sich nicht automatisch nach einem Import — nur per Command oder Refresh-Link. Automatischer Nachlauf gewünscht?                     | `Offen` |
| T-06 | Keine Tests, keine Fixtures im Repo. Mindest-Testabdeckung für Parser, Dedup und Kategorisierung festlegen?                                                | `Offen` |
| T-07 | `TransactionInfo` ist im Django-Admin nicht registriert (alle übrigen Modelle sind es) — Nachtrag gewünscht?                                                | `Offen` |
