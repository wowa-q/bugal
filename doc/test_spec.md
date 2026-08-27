# Test-Spezifikation EÜR-Manager

> **Status:** Draft · **Version:** 0.2 · **Datum:** 2026-08-27
> **Bezug:** `doc/euer_manager_spec.md` v2.3 (Ist-Stand), `doc/finman_architecture.md` v1.1, `README.md` (Nutzer-Handbuch)
> **Ziel-Framework (für spätere Umsetzung):** `pytest-django` + Django `Client` · **Sprache:** UI/Messages Deutsch, Logging/Technik Englisch (wie Bestand)
> **Ablage:** `doc/test_spec.md` · **Verifikation Bestand:** `uv run manage.py check` aus `src\finman\` (`AGENTS.md:11`)

Bei Konflikt zwischen Dokumenten gilt der Code unter `src/finman/` (`euer_manager_spec.md:3`).

---

## Inhaltsverzeichnis

1. [Ziel & Geltungsbereich](#1-ziel--geltungsbereich)
2. [Konventionen](#2-konventionen)
3. [Testfall-Schablone](#3-testfall-schablone)
4. [Modultests Nutzersicht (Blackbox)](#4-modultests-nutzersicht-blackbox)
    - M01 Navigation & Layout
    - M02 CSV-Import (Upload / Pfad)
    - M03 Import-Historie (+ Löschen mit PIN)
    - M04 Transaktionsliste — Filter-Accordion / Sort / Paginierung / Summe
    - M05 Schnellbearbeitung in der Liste
    - M06 Detailseite & Info-Notiz
    - M07 Kategorien (Hierarchie, CRUD, Sperren)
    - M08 Regeln (CRUD, Toggle, Regeln anwenden)
    - M09 Vorhersagen
    - M10 Dashboard (Accordion, Navigation)
    - M11 EÜR-Positionen & Wizard (Tabelle, Normalisierung, Warnung, n:1)
5. [Anhang Unit — Services & Parser (Whitebox)](#5-anhang-unit--services--parser-whitebox)
   - U01 CSV-Parser
   - U02 Duplikat-Erkennung
   - U03 FilterService & Kategorisierung
   - U04 Modelle & Hilfsfunktionen
6. [Traceability-Matrix](#6-traceability-matrix)
7. [Abdeckung, Nicht-Ziele & Risiken](#7-abdeckung-nicht-ziele--risiken)
8. [Testdaten & Fixtures](#8-testdaten--fixtures)

---

## 1. Ziel & Geltungsbereich

Diese Spezifikation beschreibt **prüfbares Nutzerverhalten** des EÜR-Managers, abgeleitet ausschließlich aus den drei Nutzer-/Architektur-Dokumenten. Sie ist **modular**: jedes Modul `M01–M10` ist unabhängig verständlich und unabhängig ausführbar (eigene Vorbedingungen, keine implizite Reihenfolge). `U01–U04` ergänzt als **Hybrid-Anhang** isolierte Unit-Tests für Parser/Services, die aus Nutzersicht nicht direkt sichtbar sind, aber Nutzerverhalten absichern.

**In Scope:**

- Alle 17 Routen aus `transactions/urls.py:5` und alle 7 GUI-Seiten aus `euer_manager_spec.md:12`
- Import-Workflow inkl. 2-stufigem Duplikatschutz (`spec:6`, `arch:5.2`, `services/importer.py:36`)
- Automatische Kategorisierung (`spec:9`, `arch:4.3`, `services/categorization.py:1`) und `Regeln anwenden` (`arch:4.7`)
- Filter/Sort/Paging/Summe (`spec:8,12.3`, `arch:4.6`, `views.py:127`)
- Kategorien/Regeln CRUD mit Sperren (`spec:12.7,12.10`, `views.py:318,440`)
- Vorhersagen (`spec:10`, `arch:4.5`, `services/prediction.py:9`) und EÜR-Bericht (`spec:12.6`, `views.py:541`)

**Außerhalb (Nicht-Ziele):** Django-Admin `/admin/` (nur Smoke), Produktions-Setup (`DEBUG=True`, `SECRET_KEY` hartcodiert `spec:14`/`arch:T-01`), echte Bank-Anbindung, CDN-Verfügbarkeit von Bootstrap 5.

---

## 2. Konventionen

- **IDs:** `M<Modul>-<Fortlaufend>` für Nutzersicht (z.B. `M02-01`), `U<Modul>-<Fortlaufend>` für Unit. Modul-Präfix bleibt stabil.
- **Priorität:** `Hoch` = Kernpfad / Datenverlust-Risiko, `Mittel` = wichtige Variante, `Niedrig` = Kosmetik/Randfall.
- **Schreibweise:** Schritte als `GET`/`POST` mit Pfad + Parametern; Erwartungen als **HTTP-Status + Template + DB-Zustand + Message**. Deutsch für Nutzertexte, Englisch für Log-Level.
- **Isolation:** Jeder Test startet mit definiertem DB-Zustand (Fixtures/Factory), nutzt `pytest-django` (`@pytest.mark.django_db`) und `django.test.Client`. Keine Test-Reihenfolge-Abhängigkeit.
- **Referenzpflicht:** Jeder Testfall nennt `Bezug: spec § / arch § / README-Abschnitt / Code-Stelle` mit `file:line` (z.B. `transactions/views.py:81`).
- **Negativfälle** sind Pflicht (ungültige Eingaben, fehlende Ressourcen, Schutz gegen offene Redirects/Sort-Injection).

---

## 3. Testfall-Schablone

| Feld | Inhalt |
|---|---|
| **ID / Titel** | `M04-03` — Kategorie-Filter schließt Unterkategorien ein |
| **Bezug** | `spec §4.3, §8` · `arch §4.6` · `models.py:23` `get_descendants()` · `views.py:127` |
| **Priorität** | Hoch / Mittel / Niedrig |
| **Vorbedingung** | DB-Zustand vor dem Test (Kategorien, Transaktionen, Regeln) |
| **Schritte** | Nummerierte Nutzeraktionen (HTTP-Methode, URL, Formularwerte) |
| **Erwartung** | Status, Template, DB-Effekt, `messages`-Text, Redirect-Ziel |
| **Negativ/Variante** | Abweichung und erwartetes Alternativverhalten |

---

## 4. Modultests Nutzersicht (Blackbox)

> Alle Tests nutzen den Django-Test-Client, prüfen Status/Template/Messages/DB und folgen der Schablone aus §3. `pytest-django` implizit (`client.get/post`, `assertContains`, `follow=True`).

### M01 — Navigation & Layout

*Ziel:* Grundgerüst `base.html` und Routing (`spec:12.1`, `arch:6`, `transactions/urls.py:5`). *Abhängigkeit:* keine.

| ID | Titel | Bezug | Priorität | Vorbedingung | Schritte | Erwartung |
|---|---|---|---|---|---|---|
| M01-01 | Navbar enthält 7 Hauptlinks | `spec:12.1` · `arch:6` · `templates/transactions/base.html:1` · `README:Die Oberfläche` | Hoch | — | 1. `GET /` | 200, `dashboard.html`, enthält Links `Dashboard`, `Import`, `Transaktionen`, `Kategorien`, `Regeln`, `Vorhersagen`, `EÜR-Bericht` |
| M01-02 | Unbekannte Route liefert 404 | `spec:11` · `finman/urls.py:1` | Mittel | — | 1. `GET /unbekannt/` | 404 |
| M01-03 | Django-Messages werden als Alert gerendert | `spec:12.1` · `views.py:97,117` | Mittel | — | 1. `GET /transactions/?start=ungültig` (siehe M04-06) | 200, enthält Messages-Alert mit Text `Ungültige Filterangaben` |
| M01-04 | `TransactionInfo` nicht im Admin, übrige 7 Modelle registriert | `spec:4.7,15#4` · `admin.py:1` | Niedrig | — | 1. `GET /admin/` nach `createsuperuser` | Admin-Liste zeigt 7 Modelle, `TransactionInfo` fehlt (offener Punkt, dokumentiert) |

### M02 — CSV-Import (Upload / Pfad)

*Ziel:* Import-Workflow Ende-zu-Ende (`spec:5,6,7,12.2`, `arch:4.1,5.1,5.2`, `services/importer.py:36`, `views.py:81`). *Abhängigkeit:* keine (nutzt Beispiel-CSVs).

| ID | Titel | Bezug | Priorität | Vorbedingung | Schritte | Erwartung |
|---|---|---|---|---|---|---|
| M02-01 | Giro-Upload erfolgreich: Preview + Statistik | `spec:5.3,7` · `arch:4.1` · `views.py:81` · `README:Schnellstart` · `doc/giro_beispiel.csv` | Hoch | Leere DB | 1. `GET /import/` → Formular sichtbar 2. `POST /import/` mit `file=giro_beispiel.csv` | 200 `import.html`, `preview` enthält `parser_name=GiroDKBCSVParser` (`parsers/giro_parser.py:1`), `konto` aus Zeile 1 Segment 2, `preview_rows` = 3; DB: `ImportHistory` angelegt (`models.py:114`), `Transaction`-Anzahl = Parser-Zeilen, `imported/duplicate_count/konto/min_date/max_date` korrekt |
| M02-02 | Visa-Upload erfolgreich | `spec:5.3` · `parsers/visa_parser.py:1` · `doc/visa_beispiel.csv` | Hoch | Leere DB | 1. `POST /import/` mit `file=visa_beispiel.csv` | 200, `parser_name=VisaDKBCSVParser`, `src_konto` = Segment 3 Zeile 1, `verwendung` = Umsatztyp |
| M02-03 | Generischer Fallback für unbekanntes Format | `spec:5.3` · `parsers/generic.py:1` · `parsers/registry.py:9` | Hoch | Leere DB | 1. `POST /import/` mit generischer CSV (Header `date,value,debitor`) | 200, `parser_name=GenericCSVParser`, Import erfolgreich |
| M02-04 | Dateipfad statt Upload (absoluter Pfad) | `spec:7,12.2` · `views.py:94` · `forms.py:19` | Hoch | Datei existiert unter absolutem Pfad | 1. `POST /import/` mit `file_path=/tmp/giro.csv` (ohne `file`) | 200, identisch M02-01, `filename` = basename des Pfads |
| M02-05 | Validierung: weder Datei noch Pfad | `spec:7` · `forms.py:30` `ImportForm.clean` · `views.py:116` | Mittel | — | 1. `POST /import/` leer | 200, `form_invalid`, Message `Import fehlgeschlagen. Bitte Eingaben prüfen.` + Form-Error `Bitte laden Sie eine Datei hoch…` |
| M02-06 | Pfad existiert nicht | `spec:7` · `views.py:96` | Mittel | — | 1. `POST /import/` mit `file_path=/nicht/existent.csv` | 200, Message `Datei nicht gefunden.` |
| M02-07 | Datei-Duplikat (MD5) bricht Import ab | `spec:6.1,7` · `arch:5.2` · `services/importer.py:41` · `models.py:116` `file_md5 unique` · `README:Duplikatschutz` | Hoch | `giro_beispiel.csv` bereits importiert | 1. `POST /import/` gleiche Datei erneut | 200, `messages.error` enthält `Datei wurde bereits am TT.MM.JJJJ HH:MM importiert.` (`importer.py:43`), kein neuer `ImportHistory`, keine neuen `Transaction` |
| M02-08 | Transaktions-Duplikat (SHA-256) wird übersprungen | `spec:6.2` · `parsers/base_parser.py:compute_transaction_hash` · `services/importer.py:69` | Hoch | DB enthält Transaktion X; neue Datei enthält X + Y | 1. `POST /import/` mit zweiter Datei (überlappend) | 200, `result.duplicates/skipped` = 1, nur Y neu, `ImportHistory.duplicate_count` = 1 |
| M02-09 | Defekte Zeilen werden übersprungen und geloggt | `spec:5.3` · `parsers/giro_parser.py:1` | Mittel | — | 1. `POST /import/` mit CSV bei der eine Zeile ungültiges Datum/Betrag enthält | 200, gültige Zeilen importiert, defekte Zeile gezählt als nicht importiert, Log `logs/parser_import.log` enthält Warnung (manuell prüfbar) |
| M02-10 | Temp-Datei wird immer aufgeräumt | `spec:7` · `services/importer.py:27` `cleanup_temp` · `views.py:110` `finally` | Mittel | — | 1. `POST /import/` mit Upload (auch bei Fehler M02-07) | Temp-Datei unter `gettempdir()` existiert nach Request nicht mehr; Nicht-Temp-Pfad wird nicht gelöscht |

### M03 — Import-Historie (+ Löschen)

*Ziel:* Historienübersicht & PIN-gehärtetes restloses Löschen (`spec:4.1,7a,12.9`, `views.py:121`, `settings:IMPORT_DELETE_PIN`). *Abhängigkeit:* M02-01.

| ID | Titel | Bezug | Priorität | Vorbedingung | Schritte | Erwartung |
|---|---|---|---|---|---|---|
| M03-01 | Liste sortiert neueste zuerst | `spec:4.1` `ordering=-imported_at` · `models.py:126` · `views.py:121` | Mittel | 2 Imports | 1. `GET /import/history/` | 200 `import_history.html`, erste Zeile = jüngster Import |
| M03-02 | Spalten Von/Bis getrennt, volle Dateinamen, Papierkorb ohne Header | `spec:4.1,7a,12.9` · `services/importer.py:62` `original_filename` | Mittel | 1 Import | 1. `GET /import/history/` | Zeigt `filename` voll (kein `…`, `word-break: break-all`), `konto` voll, `imported_at`, `row_count`, `duplicate_count`, `Von=min_date` / `Bis=max_date` separat, letzte Spalte ohne Header, `thead 0.75rem / tbody 0.60rem` |
| M03-03 | Leerer Import (0 gültige Zeilen) | `spec:7` | Niedrig | CSV nur mit Header | 1. `POST /import/` dann `GET /import/history/` | `row_count=0`, `konto=''`, `min_date/max_date=None` (`—`) |
| M03-04 | Import löschen – falscher PIN blockiert | `spec:7a` · `views.py:ImportDeleteView` · `settings:IMPORT_DELETE_PIN=1234` | Hoch | Import mit Transaktionen | 1. `GET /import/<pk>/delete/` → PIN-Feld 2. `POST` mit `pin=falsch` | 200, `messages.error` `Falscher PIN`, DB unverändert |
| M03-05 | Import löschen – korrekter PIN kaskadiert | `spec:7a` · `models:Transaction.import_file CASCADE` · `services/importer.py` | Hoch | Import mit N Transaktionen | 1. `POST /import/<pk>/delete/` mit `pin=1234` | 302 → `/import/history/`, `ImportHistory` + `Transaction`s + `Category/Meta/Info` kaskadiert gelöscht, `file_md5` wieder frei (Re-Import möglich) |
| M03-06 | Navigation erreichbar | `spec:12.9` · `templates/base.html` Dropdown | Mittel | — | 1. `GET /` Navbar Dropdown `Import → Import-Historie` 2. Dashboard „Alle Imports ansehen“ | Beide Links vorhanden und `GET /import/history/` 200 |

### M04 — Transaktionsliste — Filter-Accordion / Sort / Paginierung / Summe

*Ziel:* Fluent Filter + Sort + Paging + Aggregation (`spec:8,12.3`, `arch:4.6,5.4`, `services/filter_service.py:1`, `views.py:127`). *Abhängigkeit:* Transaktionen vorhanden.

| ID | Titel | Bezug | Priorität | Vorbedingung | Schritte | Erwartung |
|---|---|---|---|---|---|---|
| M04-01 | Datumsbereich filtert nur wenn beide Grenzen gesetzt | `spec:8` · `services/filter_service.py:by_date_range` · `views.py:149` | Hoch | 3 Transaktionen 01.01/15.01/01.02.2026 | 1. `GET /transactions/?start=2026-01-01&end=2026-01-31` | 200, enthält nur Jan-Transaktionen; bei nur `start` ohne `end` → kein Datumsfilter (alle 3) |
| M04-02 | Debitor icontains, leer = kein Filter | `spec:8` · `services/filter_service.py:by_debitor` | Hoch | Debitoren NETFLIX, Netto | 1. `GET /transactions/?debitor=net` | 200, findet beide (case-insensitive) |
| M04-03 | Kategorie-Filter schließt Unterkategorien ein | `spec:4.3,8,12.3` · `arch:4.6` · `models.py:23` · `views.py:154` | Hoch | `Haushalt` + `Haushalt/Lebensmittel` + Transaktionen mit beiden | 1. `GET /transactions/?category=<Haushalt.pk>` | 200, Ergebnis enthält Transaktionen beider Kategorien |
| M04-04 | Filter Art / Priorität / Intervall | `spec:8` · `models.py:62,83` · `views.py:156` | Mittel | Transaktionen mit Meta `art=FIX`, `prioritaet=Familie`, `intervall=monatlich` | 1. `GET /transactions/?art=FIX` 2. `?prioritaet=Familie` 3. `?intervall=monatlich` | Jeweils nur passende Transaktionen |
| M04-05 | Kombinierte Filter (AND) | `spec:8` · `arch:4.6` | Mittel | — | 1. `GET /transactions/?debitor=net&art=FIX&start=2026-01-01&end=2026-12-31` | 200, Schnittmenge aller Kriterien |
| M04-06 | Ungültige Filterwerte werden verworfen | `spec:8,12.3` · `forms.py:197` · `views.py:134` | Mittel | — | 1. `GET /transactions/?start=ungültig&art=UNBEKANNT` | 200, `messages.error` `Ungültige Filterangaben wurden ignoriert.`, Liste zeigt ungefilterte Menge |
| M04-07 | Sort-Whitelist mit Fallback | `spec:8` · `views.py:45` `SORT_FIELDS` · `views.py:160` | Mittel | — | 1. `GET /transactions/?sort=-value` gültig 2. `?sort=;DROP TABLE` ungültig | 1. Sortiertbetrag absteigend 2. Fallback `-date` |
| M04-08 | Sort erhält Filterparameter | `spec:12.3` | Niedrig | — | 1. `GET /transactions/?debitor=net&sort=debitor` | Links/Dropdown behalten `debitor=net` |
| M04-09 | Paginierung 50 pro Seite | `spec:12.3` · `views.py:131` `paginate_by=50` | Mittel | 60 Transaktionen | 1. `GET /transactions/` 2. `GET /transactions/?page=2` | Seite 1 = 50, Seite 2 = 10 |
| M04-10 | Summe über gefilterte Gesamtmenge (nicht nur Seite) | `spec:12.3` · `views.py:173` `total_sum` | Hoch | 60 Transaktionen, Seite 1 | 1. `GET /transactions/?debitor=net` | Footer `total_sum` = Summe aller gefilterten (nicht nur 50), grün bei positiv, rot bei negativ |
| M04-11 | Leeres Ergebnis | `spec:12.3` | Niedrig | — | 1. `GET /transactions/?debitor=XXXUNBEKANNTXXX` | 200, leere Tabelle, `total_sum=0` |

### M05 — Schnellbearbeitung in der Liste

*Ziel:* Drei `require_POST`-Endpunkte mit `next`-Redirect (`spec:12.3`, `arch:4.4`, `views.py:250,260,285,303`). *Abhängigkeit:* Transaktion vorhanden.

| ID | Titel | Bezug | Priorität | Vorbedingung | Schritte | Erwartung |
|---|---|---|---|---|---|---|
| M05-01 | Meta speichern: Art/Priorität/Intervall setzen | `spec:12.3` · `views.py:260` `transaction_meta_save` · `forms.py:97` | Hoch | Transaktion ohne Meta | 1. `POST /transactions/<pk>/meta/` mit `art=FIX&prioritaet=Familie&intervall=monatlich&next=/transactions/` | 302 → `/transactions/`, DB: `TransactionMeta` angelegt, `messages.success` enthält `aktualisiert` |
| M05-02 | Meta speichern mit Kategorie-Zuweisung (manual) | `spec:12.3` · `views.py:273` | Hoch | — | 1. `POST /transactions/<pk>/meta/` mit `category=<cat.pk>&art=FLEX` | 302, Meta gesetzt + `TransactionCategory(assigned_by='manual')` angelegt |
| M05-03 | Ungültige Meta-Angaben | `spec:12.3` · `views.py:264` | Mittel | — | 1. `POST /transactions/<pk>/meta/` mit `art=UNGÜLTIG` | 302, `messages.error` `Ungültige Angaben für Transaktion #<pk>.`, DB unverändert |
| M05-04 | Einzelnes Feld leeren (clear) | `spec:12.3` · `views.py:285` `transaction_meta_clear` | Mittel | Meta mit `art=FIX, prioritaet=Familie` | 1. `POST /transactions/<pk>/meta/clear/` mit `field=art&next=/transactions/` 2. gleiches mit `field=prioritaet` | 302, jeweils Feld geleert, Message `Art wurde entfernt.` / `Priorität wurde entfernt.`; `intervall` nicht über clear (nur art/prioritaet erlaubt) |
| M05-05 | Unbekanntes Feld beim Clear | `spec:12.3` · `views.py:289` | Niedrig | — | 1. `POST /transactions/<pk>/meta/clear/` mit `field=intervall` | 302, `messages.error` `Unbekanntes Feld.` |
| M05-06 | Kategorie-Badge entfernen | `spec:12.3` · `views.py:303` `transaction_category_remove` | Hoch | Transaktion mit Kategorie X | 1. `POST /transactions/<pk>/category/<cat_pk>/remove/` mit `next=/transactions/` | 302, Zuweisung gelöscht, Message `Kategorie '…' wurde entfernt.` |
| M05-07 | `next` nur relativ, sonst Fallback | `spec:12.3` · `views.py:253` `_redirect_back_to_list` | Hoch | — | 1. `POST …/meta/` mit `next=https://evil.com` | 302 → `/transactions/` (Schutz offene Redirects); `//evil` ebenfalls geblockt |
| M05-08 | GET auf POST-Endpunkte nicht erlaubt | `spec:11` · `views.py:260,285,303` `@require_POST` | Mittel | — | 1. `GET /transactions/<pk>/meta/` | 405 |

### M06 — Detailseite & Info-Notiz

*Ziel:* Vollanzeige + 3 Formulare (`spec:4.7,12.4`, `views.py:188`, `forms.py:85,97,121`). *Abhängigkeit:* Transaktion vorhanden.

| ID | Titel | Bezug | Priorität | Vorbedingung | Schritte | Erwartung |
|---|---|---|---|---|---|---|
| M06-01 | Detail zeigt alle Felder + Badges | `spec:4.2,12.4` · `views.py:188` · `models.py:134` | Hoch | Transaktion mit Kategorie + Meta | 1. `GET /transactions/<pk>/` | 200 `transaction_detail.html`, enthält `date/status/debitor/verwendung/target_konto/src_konto/value/debitor_id/mandats_ref/customer_ref`, Kategorie-Badges `auto` blau / `manual` gelb, Meta-Anzeige mit Regel-Link |
| M06-02 | Manuelle Kategorie zuweisen | `spec:9` `Manuelle Zuweisung` · `views.py:237` · `forms.py:85` | Hoch | — | 1. `POST /transactions/<pk>/` mit `form_type` implizit + `category=<pk>` | 302 → Detail, DB: `TransactionCategory(assigned_by='manual')` angelegt, Message `wurde manuell zugewiesen.` |
| M06-03 | Doppelte manuelle Zuweisung erzeugt kein Duplikat | `spec:9` · `views.py:238` `get_or_create` · `models.py:56` `unique_together` | Mittel | Bereits manuell zugewiesen | 1. `POST /transactions/<pk>/` gleiche Kategorie erneut | 302, Message `war bereits zugewiesen.`, nur ein Eintrag in DB |
| M06-04 | Info-Notiz anlegen | `spec:4.7,12.4` · `views.py:219` · `models.py:202` · `forms.py:121` | Hoch | Keine Info | 1. `POST /transactions/<pk>/` mit `form_type=info&text=Beleg 123` | 302, `TransactionInfo` angelegt (`related_name='info'`), `messages.success` `Info wurde gespeichert.` |
| M06-05 | Info-Notiz bearbeiten | `spec:4.7` · `models.py:209` `updated_at auto_now` | Mittel | Info vorhanden | 1. `POST /transactions/<pk>/` mit `form_type=info&text=Aktualisiert` | 302, Text überschrieben, `updated_at` aktualisiert |
| M06-06 | `attribute_count` korrekt | `spec:4.2` · `models.py:165` | Niedrig | Kategorien=2, Meta `art+prioritaet` gesetzt | 1. `GET /transactions/<pk>/` | Property `attribute_count` = 4 (2 Kategorien + 2 Meta-Felder) |
| M06-07 | Nicht existierende Transaktion 404 | `spec:11` · `views.py:189` | Mittel | — | 1. `GET /transactions/999999/` | 404 |

### M07 — Kategorien (Hierarchie, CRUD, Sperren)

*Ziel:* Zweistufige Hierarchie + CRUD + Löschsperren (`spec:4.3,12.10`, `views.py:318,348,386,402`, `forms.py:39`, `README:Kategorien`). *Abhängigkeit:* keine.

| ID | Titel | Bezug | Priorität | Vorbedingung | Schritte | Erwartung |
|---|---|---|---|---|---|---|
| M07-01 | Hauptkategorie anlegen | `spec:12.10` · `views.py:318` `CategoryListView` · `forms.py:39` | Hoch | — | 1. `POST /categories/` mit `name=Haushalt` (ohne `parent`) | 302 → `/categories/#cat-<pk>`, `messages.success`, DB: `parent=None` |
| M07-02 | Doppelname auf gleicher Ebene wird abgelehnt | `spec:12.10` · `forms.py:67` `clean` | Hoch | `Haushalt` existiert | 1. `POST /categories/` mit `name=Haushalt` | 200, Form-Error `existiert bereits auf der obersten Ebene` |
| M07-03 | Subkategorie anlegen | `spec:12.10` · `views.py:348` `CategoryNewSubView` | Hoch | `Haushalt` existiert | 1. `GET /categories/new/<Haushalt.pk>/` 2. `POST /categories/new/<Haushalt.pk>/` mit `name=Lebensmittel` | 200 Form mit `fixed_parent=True`, danach 302, DB: `parent=Haushalt`, Parent-Auswahl fixiert |
| M07-04 | Doppelname unter gleichem Parent abgelehnt | `spec:12.10` · `forms.py:72` | Mittel | `Haushalt/Lebensmittel` existiert | 1. `POST /categories/new/<Haushalt.pk>/` mit `name=Lebensmittel` | 200, Error `existiert bereits unter 'Haushalt'` |
| M07-05 | Gleicher Name unter anderem Parent erlaubt | `spec:12.10` | Mittel | `Haushalt/Lebensmittel` existiert | 1. `POST /categories/` mit `name=Lebensmittel` als Hauptkategorie | 302, erlaubt (andere Ebene) |
| M07-06 | Bearbeiten: Parent-Auswahl enthält nicht sich selbst | `spec:12.10` · `forms.py:54` `exclude(pk=self.pk)` · `views.py:386` | Mittel | `Haushalt` + `Kinder` | 1. `GET /categories/<Haushalt.pk>/edit/` | 200, Dropdown `parent` enthält nicht `Haushalt` |
| M07-07 | Bearbeiten erfolgreich | `spec:12.10` · `views.py:386` | Mittel | — | 1. `POST /categories/<pk>/edit/` mit `name=Haushalt neu` | 302 → `/categories/`, Message `wurde aktualisiert.` |
| M07-08 | Löschen verweigert: von Transaktion verwendet | `spec:12.10` · `views.py:402` `CategoryDeleteView` · `models.py:41` | Hoch | Kategorie X in `TransactionCategory` | 1. `GET /categories/<pk>/delete/` zeigt `tx_count>0` 2. `POST /categories/<pk>/delete/` | `GET` zeigt Zähler, `POST` → 302 `/categories/` mit `messages.error` `wird von Transaktionen verwendet`, nicht gelöscht |
| M07-09 | Löschen verweigert: von Regel referenziert | `spec:12.10` · `views.py:419` | Hoch | Kategorie in `FilterRule.category` | 1. `POST /categories/<pk>/delete/` | 302, Error `wird von Filter-Regeln verwendet` |
| M07-10 | Löschen verweigert: besitzt Subkategorien | `spec:12.10` · `views.py:420` | Hoch | `Haushalt` hat `Lebensmittel` | 1. `POST /categories/<Haushalt.pk>/delete/` | 302, Error `besitzt Sub-Kategorien` |
| M07-11 | Löschen ungenutzter Kategorie erfolgreich | `spec:12.10` · `views.py:437` | Hoch | Ungenutzte Kategorie | 1. `POST /categories/<pk>/delete/` | 302, Message `wurde gelöscht.`, DB-Eintrag entfernt (echte Löschung) |
| M07-12 | Baum-Darstellung & Zähler | `spec:12.10` · `views.py:325` · `templates/_category_node.html` | Niedrig | 2 Wurzeln + 3 Subs | 1. `GET /categories/` | Enthält verschachtelten Baum, `total_roots` + `total_categories` korrekt |

### M08 — Regeln (CRUD, Toggle, Regeln anwenden)

*Ziel:* Regel-Lebenszyklus + erneutes Anwenden (`spec:4.5,9,12.7`, `arch:4.7`, `views.py:440`, `README:Regeln`). *Abhängigkeit:* Kategorien vorhanden.

| ID | Titel | Bezug | Priorität | Vorbedingung | Schritte | Erwartung |
|---|---|---|---|---|---|---|
| M08-01 | Regel anlegen erfolgreich | `spec:12.7` · `views.py:440` `RuleListView` · `forms.py:130` | Hoch | Kategorie `Streaming` | 1. `POST /rules/` mit `action=create&name=Netflix&debitor_contains=NETFLIX&category=<pk>&art=FIX` | 302 → `/rules/`, Message `wurde erstellt.`, DB: `is_active=True` |
| M08-02 | Validierung: Name Pflicht | `spec:12.7` · `forms.py:176` `clean_name` | Mittel | — | 1. `POST /rules/` mit `action=create&name=` | 200, Form-Error `Bitte einen Namen angeben.` |
| M08-03 | Validierung: mind. ein Suchbegriff | `spec:12.7` · `forms.py:188` `clean` | Hoch | — | 1. `POST /rules/` mit `name=Test` ohne `debitor_contains`/`verwendung_contains` | 200, Non-field-Error `Bitte mindestens einen Suchbegriff…` |
| M08-04 | Bearbeiten Regel | `spec:12.7` · `views.py:498` `RuleUpdateView` | Mittel | Regel vorhanden | 1. `POST /rules/<pk>/edit/` mit geändertem `debitor_contains` | 302, Message `wurde aktualisiert.` |
| M08-05 | Toggle aktiv/inaktiv | `spec:12.7` · `views.py:466` `action=toggle` | Hoch | Regel aktiv | 1. `POST /rules/` mit `action=toggle&rule_id=<pk>` 2. erneut | 302, 1. → `is_active=False` + Message `deaktiviert`, 2. → `aktiviert` |
| M08-06 | Löschen mit Verknüpfungs-Hinweis | `spec:12.7` · `views.py:514` `RuleDeleteView` · `models.py:179` `SET_NULL` | Mittel | Regel mit `TransactionMeta.rule` | 1. `GET /rules/<pk>/delete/` zeigt `meta_count` 2. `POST /rules/<pk>/delete/` | `GET` zeigt Anzahl, `POST` → 302, Regel gelöscht, Transaktionen bleiben, `TransactionMeta.rule` auf `NULL` |
| M08-07 | Erste passende Regel gewinnt (alphabetisch) | `spec:4.5,9` · `arch:4.3` · `models.py:109` `ordering=name` · `services/categorization.py:match_rule` | Hoch | Regeln `A-Netflix` (NETFLIX→CatA) + `B-Netflix` (NETFLIX→CatB) | 1. Transaktion mit `debitor=NETFLIX` importieren | `TransactionCategory` = CatA (A gewinnt) |
| M08-08 | `Regeln anwenden` — Auto neu, Manual bleibt | `spec:9` `Regeln erneut anwenden` · `arch:4.7` · `views.py:474` · `services/categorization.py:apply_rules_to_all` · `README:Bestehende neu kategorisieren` | Hoch | Transaktion mit `auto`+`manual` + `TransactionMeta` | 1. `POST /rules/` mit `action=apply_rules` | 302, Message `Regeln angewendet: X geprüft, Y kategorisiert, Z ohne …`, DB: alle `assigned_by='auto'` gelöscht+neu, `manual` unberührt, `TransactionMeta` neu aufgebaut, ohne Treffer → unkategorisiert |
| M08-09 | `Regeln anwenden` ohne Transaktionen | `spec:9` | Niedrig | Leere DB | 1. `POST /rules/` mit `action=apply_rules` | 302, `processed=0, matched=0, unmatched=0` |
| M08-10 | Regel ohne Kategorie setzt nur Meta | `spec:9` · `services/categorization.py:_assign_rule` | Mittel | Regel ohne `category` aber mit `art=FIX` | 1. Transaktion importieren die matcht | `TransactionMeta` mit `art=FIX` angelegt, keine `TransactionCategory` |

### M09 — Vorhersagen

*Ziel:* Zweistufige Gruppierung + Refresh (`spec:4.8,10,12.8`, `arch:4.5`, `services/prediction.py:9`, `views.py:530`). *Abhängigkeit:* Transaktionen mit Historie.

| ID | Titel | Bezug | Priorität | Vorbedingung | Schritte | Erwartung |
|---|---|---|---|---|---|---|
| M09-01 | Refresh via `?refresh=1` löst Neuberechnung aus | `spec:10,12.8` · `views.py:530` `prediction_list` · `arch:4.5` | Hoch | Transaktionen vorhanden | 1. `GET /predictions/?refresh=1` | 302 → `/predictions/`, danach `GET /predictions/` zeigt `PredictionResult` |
| M09-02 | Ohne Refresh keine automatische Neuberechnung | `spec:10` Hinweis · `arch:T-05` | Mittel | Neue Transaktion nach letztem Refresh | 1. `GET /predictions/` ohne `refresh` | Keine neuen `PredictionResult` bis Refresh/Command |
| M09-03 | Mind. 2 verschiedene Daten nötig | `spec:10` · `services/prediction.py:27` | Hoch | 1× `Miete` 01.01, 1× `Miete` 01.01 (Duplikat-Datum) | 1. `GET /predictions/?refresh=1` | Kein `PredictionResult` für `Miete` (nur 1 distinct date) |
| M09-04 | Gruppe A (Debitor) und B (Debitor+Kategorie) | `spec:10` · `arch:4.5` · `services/prediction.py:12,18` | Hoch | 2× `NETFLIX` (verschiedene Kategorien) je 2 Termine | 1. `GET /predictions/?refresh=1` 2. `GET /predictions/` | Tabelle enthält Zeile `(NETFLIX, None)` + Zeilen `(NETFLIX, Cat)` getrennt |
| M09-05 | Intervall-Mittel und Confidence | `spec:10` · `services/prediction.py:34` `mean/stdev` `confidence=max(0,1-std/avg)` | Hoch | Termine 01.01, 01.02, 01.03 (30/28 Tage) | 1. `GET /predictions/?refresh=1` | `avg_interval_days=int(mean(diffs))`, `confidence=round(...,2)` 0.0–1.0, `next_expected_date = last + timedelta(days=int(avg))` |
| M09-06 | Unregelmäßige Zahlungen → niedrige Confidence | `spec:10` · `services/prediction.py:36` | Mittel | Termine 01.01, 02.01, 01.04 (1/89 Tage) | 1. Refresh | `confidence` nahe 0.0 |
| M09-07 | Sortierung nach `next_expected_date` | `spec:12.8` · `models.py:231` `ordering` · `views.py:535` | Mittel | Mehrere Predictions | 1. `GET /predictions/` | Tabelle aufsteigend `next_expected_date` |
| M09-08 | Management-Command `update_predictions` | `spec:10` · `transactions/management/commands/update_predictions.py:1` | Mittel | — | 1. `uv run manage.py update_predictions` aus `src\finman\` | Gleiche `PredictionResult` wie via Refresh |

### M10 — Dashboard (Accordion & Navigation)

*Ziel:* Dashboard-Aggregationen und Navigation zum Bericht/Historie.

| ID | Titel | Bezug | Priorität | Vorbedingung | Schritte | Erwartung |
|---|---|---|---|---|---|---|
| M10-01 | Dashboard KPIs aktueller Monat | `spec:12.5` · `views.py:50` `dashboard` · `README:Dashboard` | Hoch | Transaktionen im aktuellen Monat Einnahmen + Ausgaben | 1. `GET /` | 200 `dashboard.html`, `income` / `expenses` / `balance=income+expenses` korrekt |
| M10-02 | Top-5 Ausgaben nach Kategorie | `spec:12.5` · `views.py:59` | Mittel | Ausgaben mit Kategorien | 1. `GET /` | Liste `top_expenses` max 5, sortiert `total` aufsteigend (negativste zuerst), nur aktueller Monat |
| M10-03 | Nächste Zahlungen (10) + letzte 5 Imports | `spec:12.5` · `views.py:67` | Mittel | Predictions + Imports | 1. `GET /` | Enthält 10 `PredictionResult` sortiert `next_expected_date`, 5 `ImportHistory` neuste |
| M10-04 | Letzte Imports als Accordion + Link | `spec:12.5` · `templates/dashboard.html` | Mittel | — | 1. `GET /` | Accordion `Letzte Imports (N)` oben, eingeklappt, Tabelle Datei/Von/Bis/Zeilen/Duplikate, Button „Alle Imports ansehen“ → `/import/history/` |
| M10-05 | Navigation Import-Dropdown | `spec:12.9` · `templates/base.html` | Mittel | — | 1. `GET /` Navbar | Dropdown `Import → CSV importieren / Import-Historie` |

### M11 — EÜR-Positionen & Wizard (ersetzt monatlichen EÜR)

*Ziel:* Positionen je Kalenderjahr als Sammelposten (`spec:4.8,9a,12.6`, `models:EuerPosition`, `services/euer.py`, `views:report_euer + EuerWizard*`, `forms:EuerPositionForm`). *Abhängigkeit:* Transaktionen vorhanden.

| ID | Titel | Bezug | Priorität | Vorbedingung | Schritte | Erwartung |
|---|---|---|---|---|---|---|
| M11-01 | Bericht filtert nach Position.year | `spec:9a` `Position.year` · `views.py:report_euer` | Hoch | Position `Miete` 2025 + `Miete` 2026 | 1. `GET /reports/euer/?year=2025` | Nur 2025-Positionen, Januar-Buchung im 2026-Report nur wenn Position 2026 |
| M11-02 | Position anlegen Wizard 3 Schritte | `spec:9a` · `views.py:EuerWizardStep1/2/3` · `forms:EuerPositionForm` | Hoch | — | 1. `GET /reports/euer/wizard/step1/?year=2026` → `POST` Name/Jahr/Kategorie/Typ/Intervall/Priorität/Hinweis 2. `GET/POST wizard/step2` Transaktionen wählen 3. `GET/POST wizard/step3` | 302 → `step2` → `step3` → `302 /reports/euer/?year=2026`, `EuerPosition` mit M2M angelegt, `PositionTransactionsForm` blendet year'seigene bereits zugeordnete aus |
| M11-03 | Transaktion nur in einer Position je Jahr (n:1) | `spec:9a` · `services/euer.py` · `views.py:wizard step3` | Hoch | `Miete` 2026 enthält `tx1` | 1. Zweite Position anlegen, `tx1` in `step2` wählen | `tx1` nicht in Auswahl; falls erzwungen: Warnung `… bereits zugeordnet und wurden übersprungen.` |
| M11-04 | Bearbeiten behält Zuweisungen + Unique-Validierung | `spec:9a` · `views.py:EuerWizardStep1View.get_form_kwargs(instance)` | Hoch | `KV` 2025 vorhanden | 1. `GET /reports/euer/wizard/step1/?edit=<pk>` → `POST` gleicher Name/Jahr (Form mit `instance`) 2. `GET step2` zeigt bisherige `transaction_ids` vorausgewählt | 1. 302 statt Fehler `existiert bereits`, 2. Checkboxes `checked` |
| M11-05 | Ableitung & Warnung (leer = vererbt) | `spec:9a` · `services/euer.py:position_summary` | Hoch | Position `FIX/monatlich/Familie` + `tx` mit `FLEX` bzw. leerer `art` | 1. `GET /reports/euer/?year=2026` | Warnicon nur wenn `tx.art` gesetzt und ≠ Positionstyp; leeres `tx.art` → keine Warnung (vererbt). Gleiches für Kategorie/Intervall/Priorität/Konto |
| M11-06 | Normalisierte Beträge je Intervall + `abgelaufen` friert | `spec:9a` · `services/euer.py:normalize_amount` · `INTERVALL_TO_ANNUAL_FACTOR` | Hoch | Position Betrag 1200, Intervall monatlich | 1. `GET /reports/euer/?year=2026` | `täglich≈32.85` `wöchentlich≈230.77` `monatlich=1200` `jährlich=14400`; bei `abgelaufen` alle vier = `1200` |
| M11-07 | Hinweis editierbar (vollständige Positionsfelder) | `spec:9a` · `views.py:EuerPositionHintView` `EuerPositionForm` | Mittel | Position vorhanden | 1. `GET /reports/euer/<pk>/hint/` → `POST` `art=FLEX … hint=neu` | 302 → Bericht, Felder aktualisiert, Message `wurde aktualisiert.` |
| M11-08 | Positionen-Tabelle 14 Spalten ohne ROI | `spec:9a,12.6` · `templates/report_euer.html` | Mittel | — | 1. `GET /reports/euer/?year=2026` | Header `Position\|Betrag\|Kategorie\|Sub-Kategorie\|Typ\|Intervall\|Priorität\|Hinweis\|täglich\|wöchentlich\|monatlich\|jährlich\|wird gezahlt über\|Aktion`, `thead 0.75rem / tbody 0.68rem`, kein ROI |

---

## 5. Anhang Unit — Services & Parser (Whitebox)

> Jede Testgruppe ist isoliert (kein HTTP), nutzt `pytest` + `pytest-django` (`@pytest.mark.django_db` nur wo ORM nötig). Parser-Tests arbeiten mit temporären Dateien (`tmp_path`).

### U01 — CSV-Parser

*Bezug:* `spec:5`, `arch:5.1`, `parsers/base_parser.py:1`, `parsers/registry.py:9`, `parsers/giro_parser.py:1`, `parsers/visa_parser.py:1`, `parsers/generic.py:1`

| ID | Titel | Bezug | Schritte | Erwartung |
|---|---|---|---|---|
| U01-01 | `parse_german_number` deutsche Formate | `spec:5.2` · `parsers/base_parser.py:parse_german_number` | Inputs: `1.234,56 EUR`, `-12,30`, `12,30€`, `1.000` | Liefert `Decimal('1234.56')`, `-12.30`, etc.; Tausenderpunkt entfernt, `,`→`.` |
| U01-02 | `compute_file_md5` stabil über Encoding `utf-8-sig` | `spec:6.1` · `parsers/base_parser.py:compute_file_md5` | Gleiche Datei 2×, dann 1 Byte geändert | Gleiche MD5 bei identischem Inhalt, andere bei Änderung; 8192-Byte-Blöcke |
| U01-03 | `compute_transaction_hash` SHA über 6 Felder | `spec:6.2` · `parsers/base_parser.py:compute_transaction_hash` | Gleicher `TransactionData` 2×, dann 1 Feld geändert | Gleiche SHA-256 (64 Hex), Änderung in einem der 6 Felder → anderer Hash |
| U01-04 | `GiroDKBCSVParser.detect` | `spec:5.3` · `parsers/giro_parser.py:detect` | Datei Zeile 1 `Girokonto;…` vs `Karte;…` vs leer | `True` nur bei `Girokonto;` |
| U01-05 | `GiroDKBCSVParser.parse` Spaltenmapping | `spec:5.3` Tabelle · `parsers/giro_parser.py:parse` | `doc/giro_beispiel.csv` parsen | `src_konto` aus Zeile 1 Segment 2, `date` `%d.%m.%Y`/`%d.%m.%y`, `debitor` abhängig `Umsatztyp` (Eingang→Zahlungspflichtige, sonst Empfänger), `value` via `parse_german_number` |
| U01-06 | `VisaDKBCSVParser.detect/parse` | `spec:5.3` · `parsers/visa_parser.py:1` | `doc/visa_beispiel.csv` | `detect` bei `Karte;`, `src_konto` Segment 3 Zeile 1, `debitor=Beschreibung`, `verwendung=Umsatztyp` |
| U01-07 | `GenericCSVParser.detect` immer True + Delimiter-Erkennung | `spec:5.3` · `parsers/generic.py:1` · `arch:5.1` | CSV mit `;` bzw `,` als Delimiter | `detect=True`, Trennzeichen korrekt erkannt, Header als `DictReader` |
| U01-08 | `GenericCSVParser` Header exakt = `TransactionData`-Felder | `spec:5.3` · `parsers/generic.py:parse` | CSV Header `date,value,debitor,…` vs `Datum,Betrag` ohne Mapping | Erster Fall importiert, zweiter liefert leere/gefüllte Defaults oder `column_mapping`-Pfad (vorhanden aber vom Importer nicht genutzt `arch:T-02`) |
| U01-09 | Fehlende Spalten → leere Felder, defekte Zeile übersprungen | `spec:5.3` | CSV Zeile ohne `Betrag` / ungültiges Datum | Zeile übersprungen, geloggt (`parser_import.log`), restliche Zeilen ok |
| U01-10 | Registry-Reihenfolge | `spec:5.4` · `arch:4.2` · `parsers/registry.py:9` `PARSERS` | `get_parser` auf Giro/Visa/Generisch | Giro gewinnt vor Visa vor Generic; Generic immer letzter Eintrag |
| U01-11 | Encoding `utf-8-sig` (BOM) | `spec:5.3` · `AGENTS.md:53` | Datei mit BOM `\xef\xbb\xbf` | Parser erkennt trotz BOM korrekt |

### U02 — Duplikat-Erkennung (Integration mit ORM)

*Bezug:* `spec:6`, `arch:5.2`, `services/importer.py:39,69`, `models.py:116,135`

| ID | Titel | Bezug | Schritte | Erwartung |
|---|---|---|---|---|
| U02-01 | Datei-Duplikat: zweiter `import_csv` wirft `ValueError` | `spec:6.1,7` · `services/importer.py:41` | `import_csv(path)` 2× gleicher Pfad | Beim 2. Mal `ValueError` mit Datum, `ImportHistory` nicht dupliziert |
| U02-02 | Transaktions-Duplikat: `hash` unique überspringt | `spec:6.2` · `services/importer.py:69` · `models.py:135` `hash unique` | Zwei Dateien teilen 1 Transaktion (gleiche 6 Felder) | 2. Import `skipped=1`, `duplicate_count` erhöht, nur neue Transaktion gespeichert |

### U03 — FilterService & Kategorisierung

*Bezug:* `spec:8,9`, `arch:4.3,4.6,5.4`, `services/filter_service.py:1`, `services/categorization.py:1`

| ID | Titel | Bezug | Schritte | Erwartung |
|---|---|---|---|---|
| U03-01 | `TransactionFilter` fluent Builder `distinct()` | `spec:8` · `services/filter_service.py:TransactionFilter` · `arch:5.4` | `TransactionFilter().by_debitor('a').by_art('FIX').apply()` | Verkettung liefert `self`, `apply()` → `distinct()` QuerySet |
| U03-02 | `by_category` erweitert via `get_descendants` | `spec:4.3,8` · `models.py:23` | Kategorie-Baum | Filter auf Parent findet auch Sub-Transaktionen |
| U03-03 | `match_rule` case-insensitive, leer = Wildcard | `spec:9` · `services/categorization.py:_first_matching_rule` | Regel `debitor_contains=''` / `verwendung_contains='Netflix'` vs `netflix` | Match trotz Case, leeres Feld = Platzhalter |
| U03-04 | `auto_categorize` legt `TransactionCategory` nur bei `category_id` | `spec:9` · `services/categorization.py:_assign_rule` | Regel ohne Kategorie | Nur `TransactionMeta` via `update_or_create`, keine Kategorie |
| U03-05 | `apply_rules_to_all` Statistik | `spec:9` · `services/categorization.py:apply_rules_to_all` | Aufruf | Return `{processed, matched, unmatched}` korrekt, `auto` gelöscht, `manual` bleibt |

### U04 — Modelle & Hilfsfunktionen

*Bezug:* `spec:4`, `models.py:1`, `settings.py:LOGGING`

| ID | Titel | Bezug | Schritte | Erwartung |
|---|---|---|---|---|
| U04-01 | `Category.get_descendants` rekursiv | `spec:4.3` · `models.py:23` | Baum A→B→C | Liefert `[A,B,C]` |
| U04-02 | `Category.get_full_path` | `spec:4.3` · `models.py:29` | `Haushalt/Lebensmittel` | `Haushalt / Lebensmittel` |
| U04-03 | `Category.__str__` | `spec:4.3` · `models.py:18` | Mit/ohne Parent | `Haushalt / Lebensmittel` bzw `Haushalt` |
| U04-04 | `Transaction.attribute_count` | `spec:4.2` · `models.py:165` | Meta `art+intervall` + 1 Kategorie | `count == 3` |
| U04-05 | `FilterRule` ordering alphabetisch | `spec:4.5` · `models.py:109` | Regeln `B`, `A` anlegen | QuerySet `FilterRule.objects.all()` liefert `A,B` |

---

## 6. Traceability-Matrix

| Test-ID | Spec-§ | Architektur-§ | README-Abschnitt | Code/URL | Bemerkung |
|---|---|---|---|---|---|
| M01-01–04 | 11,12.1 | 6 | Die Oberfläche | `urls.py:5` `dashboard` · `templates/base.html` | Navigation |
| M02-01–10 | 5,6,7,12.2 | 4.1,5.1,5.2 | Schnellstart, Duplikatschutz, Unterstützte Formate | `views.py:81` · `forms.py:19` · `services/importer.py:36` · `parsers/registry.py:9` | Import |
| M03-01–06 | 4.1,7a,12.9 | — | /import/history | `views.py:121,ImportDeleteView` · `models.py:114,147` `CASCADE` | Historie + PIN-Löschung |
| M04-01–11 | 8,12.3 | 4.6,5.4 | Transaktionen | `views.py:127` · `services/filter_service.py:1` · `forms.py:197` | Filter/Sort/Paging/Summe |
| M05-01–08 | 12.3 | 4.4 | Schnellzuweisung | `views.py:253,260,285,303` | Quick-Edit |
| M06-01–07 | 4.2,4.7,12.4 | 4.4 | Notizen | `views.py:188` · `models.py:202` · `forms.py:85,121` | Detail/Info |
| M07-01–12 | 4.3,12.10 | — | Kategorien | `views.py:318,348,386,402` · `forms.py:39` · `models.py:4` | Kategorie-CRUD |
| M08-01–10 | 4.5,9,12.7 | 4.3,4.7 | Regeln + Regeln anwenden | `views.py:440,498,514` · `forms.py:130` · `services/categorization.py:1` | Regel-CRUD |
| M09-01–08 | 4.8,10,12.8 | 4.5,5.3 | Vorhersagen | `views.py:530` · `services/prediction.py:9` · `management/.../update_predictions.py` | Prognosen |
| M10-01–05 | 12.5 | — | Dashboard | `views.py:50` · `templates/dashboard.html` · `templates/base.html` | Dashboard + Navigation |
| M11-01–08 | 4.8,9a,12.6 | 4.x | EÜR-Positionen | `views.py:report_euer,EuerWizard*` · `services/euer.py` · `forms:EuerPositionForm` | Positionen/Wizard |
| U01-01–11 | 5,6 | 5.1 | — | `parsers/base_parser.py:1` · `parsers/registry.py:9` | Parser-Unit |
| U02-01–02 | 6 | 5.2 | Duplikatschutz | `services/importer.py:39,69` | Dedup-Unit |
| U03-01–05 | 8,9 | 4.3,4.6 | — | `services/filter_service.py` · `services/categorization.py` | Service-Unit |
| U04-01–05 | 4 | 3 | — | `models.py:1` | Model-Unit |

---

## 7. Abdeckung, Nicht-Ziele & Risiken

**Abgedeckt:** Alle Pflichtfelder aus Spec §4–§12, alle Sequenzdiagramme Arch §4.1–4.7, alle README-Nutzerflüsse. Quote: je Modul ≥1 Positiv + ≥1 Negativ, Quick-Edit 3 POST-Endpunkte je mit `next`-Schutz, Kategorien 3 Lösch-Sperren, Regeln `apply_rules_to_all` inkl. Erhalt `manual`.

**Nicht abgedeckt / bewusst offen (verweist auf Arch T-01..T-07):**

- T-01 `SECRET_KEY`/`DEBUG` — kein Exposure-Test (lokal).
- T-02 `GenericCSVParser.column_mapping` — nur dokumentiert, nicht via UI erreichbar (`parsers/generic.py`).
- T-03 Doppelte Parser-Erkennung (Preview + Import) — kein Cache-Test.
- T-04 `import_csv` ohne `transaction.atomic` — Teilimport bei Abbruch wird nicht als Fehlerfall automatisiert (nur dokumentiert `spec:7` Hinweis).
- T-05 Keine Auto-Prediction nach Import — erwartet, Test M09-02 prüft explizit.
- T-06 Keine Fixtures im Repo — Tests legen Daten selbst an.
- T-07 `TransactionInfo` nicht im Admin — M01-04 dokumentiert.
 - `spec:15` PDF/CSV-Export EÜR — nicht implementiert (als ROI/Export offen, M11 abgedeckt).

**Risiken:** Bootstrap-CDN offline → M01-01 prüft Links, nicht Styles. `logs/parser_import.log` (`spec:14`) nur manuell via Dateisystem.

**Abnahmekriterium je Modul:** Modul gilt als bestanden, wenn alle `Hoch`-Fälle grün und keine `Mittel`-Regression.

---

## 8. Testdaten & Fixtures

- **Beispiel-CSVs:** `doc/giro_beispiel.csv` (Giro), `doc/visa_beispiel.csv` (Visa) — als Golden-Master für M02/U01.
- **Generisch:** Minimal-CSVs in `tmp_path` (z.B. `date,value,debitor,src_konto\n2026-01-01,12.34,NETFLIX,DE00\n`) für U01-07/08 und M02-03.
- **Factories (pytest):** `make_category(name, parent)`, `make_transaction(debitor, date, value, src_konto)`, `make_rule(name, debitor_contains, category, is_active)`, `make_tx_with_meta(...)`. Datumshilfen `timezone.now()` / `Europe/Berlin` (`settings.py:LANGUAGE_CODE`).
- **DB-Reset:** `pytest-django` transaktional pro Test, `Transaction`, `ImportHistory`, `Category`, `FilterRule` werden nicht über Fixtures geteilt.
- **Logs:** Vor Parser-Tests `logs/parser_import.log` leeren oder per `caplog` prüfen.

---

*Erstellt: 2026-08-27 · Pfad: `doc/test_spec.md` · Nächste Schritte: Umsetzung als `pytest-django`-Suite unter `src/finman/transactions/tests/` (ein Testmodul je M/U-Modul, z.B. `test_import.py`, `test_filter.py`), Ausführung `uv run pytest` + `uv run manage.py check`.*
