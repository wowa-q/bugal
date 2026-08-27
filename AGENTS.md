# AGENTS.md – Projektinformationen für KI-Agenten

## Projektüberblick

**EÜR-Manager**: lokal laufende Django-Webanwendung zur Verwaltung der
Einnahmen-Überschuss-Rechnung (EÜR). Deutschsprachige UI, SQLite-Datenbank,
kein Login, `DEBUG=True`, kein Produktionsbetrieb vorgesehen.
Endnutzer-Dokumentation: [README.md](README.md).

## Befehle

> **Wichtig:** Alle Django-Befehle müssen aus `src\finman\` ausgeführt werden –
> dort liegt `manage.py`. Im Repo-Root funktioniert kein Django-Befehl.

```powershell
# Setup (einmalig)
uv sync
uv run manage.py migrate            # aus src\finman\

# Entwicklung
uv run manage.py runserver          # http://127.0.0.1:8000/
uv run manage.py check              # Verifikation
```

- **Es gibt KEINE Testsuite.** `uv run manage.py check` plus ein manueller
  Serverlauf sind die einzige Verifikationsmöglichkeit.
- Nach Modelländerungen: `uv run manage.py makemigrations` und danach `migrate`.
- Vorhersagen neu berechnen: `uv run manage.py update_predictions`.

## Projektstruktur

| Pfad | Inhalt |
|---|---|
| `src\finman\manage.py` | Django-Einstiegspunkt (Befehle hierher) |
| `src\db.sqlite3` | Datenbank (Backup = Datei kopieren, Server vorher stoppen) |
| `src\finman\transactions\models.py` | alle ORM-Modelle |
| `src\finman\transactions\views.py` | alle Views |
| `src\finman\transactions\forms.py` | 10 Formen + CategoryChoiceField: ImportForm, CategoryForm, ManualCategoryForm, TransactionMetaForm, TransactionInfoForm, FilterRuleForm, TransactionFilterForm, PlannedInvestmentForm, InvestmentDecisionForm + EuerPositionForm, PositionTransactionsForm |
| `src\finman\transactions\urls.py` | App-URLs inkl. `/investments/` (CRUD + Entscheidung) und Wizard-Step1 mit Auswahl bestehender Position |
| `src\finman\transactions\parsers\` | CSV-Parser (`base_parser.py`, `giro_parser.py`, `visa_parser.py`, `generic.py`, `registry.py`) |
| `src\finman\transactions\services\` | Business-Logik: `importer.py`, `categorization.py`, `filter_service.py`, `prediction.py` |
| `src\finman\templates\transactions\` | Templates (erben von `base.html`) |
| `logs\parser_import.log` | Logdatei für Parser/Import-Debugging |
| `doc\euer_manager_spec.md` | Projektspezifikation (Ist-Stand) |
| `doc\finman_architecture.md` | Architektur mit Mermaid-Diagrammen |

## Architektur & Konventionen

- **Parser-Pattern:** Jeder CSV-Parser erbt von `BaseCSVParser`
  (`detect()`/`parse()`/`get_meta_info()`). Neue Parser in der `PARSERS`-Liste
  in `parsers/registry.py` registrieren – Reihenfolge ist die Prüfreihenfolge,
  `GenericCSVParser` muss **immer der letzte Eintrag** bleiben (Fallback mit
  `detect() = True`). Encoding aller DKB-Parser: `utf-8-sig`, Trennzeichen `;`.
- **Business-Logik liegt in `services/`**, nicht in Views. Views bleiben dünn.
- **Formular-Seiten folgen dem Kategorien-Muster:** CBV (`ListView`/`UpdateView`/
  `DeleteView`/`FormView` + `FormMixin`) mit `@never_cache`, `ModelForm` in
  `forms.py`, Feedback über `django.contrib.messages`, Fehler-Rendering über die
  Partials `_form_alert.html` / `_field_errors.html`.
- **Transaktionen sind immutable:** Ein gespeichertes `Transaction`-Objekt wird
  nie verändert. Kategorien und Regel-Metadaten werden ausschließlich über die
  Assoziationstabellen `TransactionCategory` und `TransactionMeta` zugewiesen.
- **Duplikatschutz:** MD5 je Datei (Import bricht bei Wiederholung ab),
  SHA-256 je Transaktion (Duplikate werden übersprungen). Die Hash-Felder
  (`file_md5`, `hash`) nicht verändern oder neu berechnen, ohne das
  Duplikatkonzept zu beachten.
- **Import-Löschung:** `Transaction.import_file` ist `CASCADE` – Löschen eines
  `ImportHistory`-Eintrags entfernt automatisch alle zugehörigen
  Transaktionen samt `TransactionCategory`/`TransactionMeta`/`TransactionInfo`.
  Jeder Löschweg (auch Admin) kaskadiert. Schutz vor versehentlichem Löschen
  erfolgt über PIN-Abfrage (`FINMAN_DELETE_PIN`, Default `1234`,
  `settings.IMPORT_DELETE_PIN`).
- **Auto-Kategorisierung:** Beim Import gewinnt die erste aktive passende
  `FilterRule`. Manuelle Zuweisungen (`assigned_by='manual'`) haben Vorrang und
  dürfen von Code **niemals** verändert oder gelöscht werden.
- **Regeln erneut anwenden:** Button „Regeln anwenden" auf der Regeln-Seite
  (`action=apply_rules` in `rule_list`) ruft
  `services.categorization.apply_rules_to_all()` auf: löscht alle
  Auto-Zuweisungen + `TransactionMeta` und baut sie aus den aktiven Regeln neu
  auf. Manuelle Zuweisungen bleiben unberührt.

## Sprachkonventionen

- UI-Strings, Nutzer-Meldungen und Dokumentation: **Deutsch**
- Logging-Meldungen: **Englisch** (wie im Bestandscode)

## Fallstricke

- Die Datenbank liegt unter `src\db.sqlite3` (nicht im Repo-Root).
- Bootstrap 5 wird per CDN geladen – ohne Internet laden Seiten ohne Styles.
- `TransactionInfo` ist (noch) nicht im Django-Admin registriert – alle
  übrigen Modelle sind es.
- **Investments:** `PlannedInvestment.euer_position` ist 1:1 (OneToOne) zu `EuerPosition` – ein Investment kann max. einer Position zugeordnet sein. Wizard Step1 zeigt zusätzlich bestehende Positionen zur Auswahl an.
