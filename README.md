# EÜR-Manager

Der **EÜR-Manager** ist eine lokal laufende Webanwendung zur Verwaltung der
Einnahmen-Überschuss-Rechnung (EÜR). Bankumsätze werden als CSV importiert,
automatisch kategorisiert und in Berichten und Statistiken aufbereitet.

Die Anwendung ist bewusst einfach gehalten:

- Läuft ausschließlich lokal auf dem eigenen Rechner (`uv run manage.py runserver`)
- Keine Anmeldung, keine Cloud, keine externen Dienste
- Alle Daten liegen in einer einzigen SQLite-Datei im Projektverzeichnis

---

## Funktionen im Überblick

- **CSV-Import** für DKB-Girokonto-, DKB-Visa-Kreditkarten- und generische CSV-Exporte
- **Duplikatschutz** auf Datei- und Transaktionsebene – mehrfaches Importieren ist gefahrlos
- **Automatische Kategorisierung** über frei definierbare Regeln (z. B. „alles von NETFLIX → Streaming")
- **Transaktionsliste** mit Filtern (Zeitraum, Empfänger, Kategorie, FIX/FLEX, Priorität, Intervall), Sortierung und laufender Summe
- **Schnellzuweisung direkt in der Liste**: Art (FIX/FLEX), Priorität und Intervall pro Buchung setzen, Kategorien zuweisen oder entfernen
- **Notizen**: freier Text zu jeder einzelnen Buchung (z. B. Erinnerungen, Belegnummer)
- **Vorhersagen**: wiederkehrende Zahlungen (Miete, Abos, Gehalt …) werden erkannt und der nächste Termin prognostiziert
- **EÜR-Jahresbericht** mit monatlichen Einnahmen, Ausgaben und Saldo
- **Dashboard** mit den wichtigsten Kennzahlen des aktuellen Monats

---

## Voraussetzungen

- [uv](https://docs.astral.sh/uv/getting-started/installation/) (installiert bei Bedarf automatisch ein passendes Python ≥ 3.13)
- Ein aktueller Webbrowser (die Oberfläche nutzt Bootstrap 5 von einem CDN, daher Internetzugang beim Aufruf)

Weitere Installationsschritte sind nicht erforderlich – die Datenbank wird automatisch angelegt.

---

## Installation und Start

Alle Befehle werden im Projektverzeichnis ausgeführt:

```powershell
# 1. Abhängigkeiten installieren (legt .venv an)
uv sync

# 2. Ins Verzeichnis der Django-Projekts wechseln
cd src\finman

# 3. Datenbank anlegen
uv run manage.py migrate

# 4. Server starten
uv run manage.py runserver
```

Danach ist der EÜR-Manager unter **http://127.0.0.1:8000/** erreichbar.
Beendet wird der Server mit `Strg+C`.

---

## Schnellstart: Erste CSV importieren

1. Umsätze aus dem Online-Banking als CSV exportieren (z. B. DKB Girokonto oder Visa-Kreditkarte).
2. Im EÜR-Manager die Seite **Import** öffnen.
3. Datei hochladen **oder** einen absoluten Pfad eingeben (z. B. `C:\Downloads\giro.csv`) und auf *Importieren* klicken.
4. Die Vorschau zeigt das erkannte Format (Parser), das Konto und die ersten Zeilen der Datei.
5. Nach dem Import erscheint eine Zusammenfassung: **importiert**, **übersprungen**, **Duplikate**.

Unter `/import/history/` findet sich zusätzlich eine Übersicht aller bisherigen Importe
(inkl. Zeitraum und Anzahl der Zeilen).

### Unterstützte Formate

| Format | Erkennung |
|---|---|
| DKB Girokonto | Erste Zeile beginnt mit `Girokonto;` |
| DKB Visa-Kreditkarte | Erste Zeile beginnt mit `Karte;` |
| Generische CSV | Fallback für alle anderen Dateien (Trennzeichen `;` oder `,` werden automatisch erkannt) |

Bei unbekannten Formaten sollte die Datei Spalten für Datum, Betrag und Empfänger enthalten.

---

## Die Oberfläche im Detail

### Dashboard

Die Startseite zeigt:

- **Kennzahlen des laufenden Monats:** Einnahmen, Ausgaben, Saldo
- **Top-5-Ausgaben** nach Kategorie im aktuellen Monat
- **Nächste erwartete Zahlungen** aus den Vorhersagen
- **Letzte Importe**

### Transaktionen

Die zentrale Übersicht aller importierten Umsätze.

- **Filterleiste:** Zeitraum (von/bis), Empfänger (Debitor, Teilstring-Suche),
  Kategorie (Unterkategorien werden einbezogen), Art (FIX/FLEX), Priorität und Intervall
- **Sortierung:** Dropdown (Neueste/Älteste zuerst, Betrag auf-/absteigend, Debitor A–Z)
- **Blätterung:** 50 Einträge pro Seite
- **Summenzeile:** Summe aller gefilterten Beträge – grün bei positiv, rot bei negativ
- **Schnellbearbeitung je Zeile:** Kategorie-Badges per Klick entfernen;
  Art und Priorität zurücksetzen; in der Zeile Kategorie sowie FIX/FLEX,
  Priorität und Intervall auf einmal zuweisen

Ein Klick auf eine Transaktion öffnet die **Detailseite** mit allen Feldern
(Datum, Status, Verwendungszweck, IBAN, Gläubiger-ID, Mandatsreferenz u. v. m.),
der zugehörigen Regel samt Zusatzinfos und einer freien **Info-Notiz**
(mit Datum der letzten Änderung). Hier kann auch manuell eine Kategorie
zugewiesen werden; manuelle Zuweisungen bleiben erhalten und werden beim
erneuten Anwenden der Regeln nicht überschrieben.

### Kategorien

Kategorien bilden eine **zweistufige Hierarchie**:

- **Hauptkategorie** – ohne übergeordnete Kategorie (z. B. *Haushalt*)
- **Unterkategorie** – gehört zu genau einer Hauptkategorie (z. B. *Haushalt / Lebensmittel*)

Jede Transaktion kann beliebig viele Kategorien erhalten – automatisch per Regel
beim Import oder manuell auf der Detailseite. Der Kategorie-Filter in der
Transaktionsliste schließt Unterkategorien automatisch ein: Ein Filter auf
*Haushalt* findet also auch alles unter *Haushalt / Miete*.

#### Empfohlene Kategorien-Struktur

Es werden keine Kategorien mitgeliefert – diese Struktur lässt sich bequem
unter **Kategorien** anlegen:

| Hauptkategorie | Unterkategorien |
|---|---|
| Haushalt | Strom, Gas, Wasser, Miete, Lebensmittel |
| Versicherungen | KFZ, Haftpflicht, Kranken, Leben |
| Subscriptions | Streaming, Software, Mitgliedschaften |
| Freizeit | Restaurant, Urlaub, Sport |
| Kinder | Schule, Kleidung, Spielzeug |
| Einnahmen | Gehalt, Erstattungen, Sonstiges |
| Steuern | Vorauszahlung, Erstattung |

#### Kategorien verwalten

Auf der Seite **Kategorien** lassen sich die Einträge pflegen:

- **Anlegen:** Formular oben auf der Übersichtsseite – Name eingeben und
  optional eine Hauptkategorie als Eltern-Eintrag wählen (ohne Eltern-Eintrag
  entsteht eine neue Hauptkategorie)
- **Bearbeiten:** Schaltfläche *Bearbeiten* an jeder Kategorie; als Eltern-Eintrag
  kann nicht die eigene Kategorie oder eine ihrer Unterkategorien gewählt werden
  (verhindert Zirkelbezüge)
- **Löschen:** Schaltfläche *Löschen* mit Bestätigungsseite. Eine Kategorie kann
  **nicht gelöscht** werden, solange sie noch von Transaktionen verwendet wird,
  in einer Regel referenziert ist oder eigene Unterkategorien besitzt – die
  Bestätigungsseite zeigt jeweils die Anzahl der betroffenen Einträge.
  Nach der Bestätigung wird eine ungenutzte Kategorie **endgültig aus der
  Datenbank entfernt** (echte Löschung, kein Papierkorb und keine Archivierung) –
  das ist unwiderruflich. Da jede genutzte Kategorie blockiert wird, lassen sich
  praktisch nur unbenannte Kategorien entfernen; versehentliches Verlieren von
  Kategorien mit Transaktionen ist ausgeschlossen.

### Regeln

Regeln steuern die automatische Kategorisierung beim Import. Jede Regel besteht aus:

- **Suchbegriff(en)** für Empfänger (Debitor) und/oder Verwendungszweck
- Der zuzuweisenden **Kategorie**
- Optionalen Zusatzinfos: **Art** (FIX = regelmäßig gleichbleibend, FLEX = veränderlich),
  **Priorität** (z. B. Familie, Kinder …) und **Intervall** (einmalig bis jährlich)

Wird beim Import eine Regel gefunden, deren Suchbegriffe passen, erhält die
Transaktion automatisch die Kategorie und Zusatzinfos der Regel. Passt mehr als
eine Regel, gewinnt die erste in der Liste. Über die Schaltfläche in der Regelliste
lässt sich eine Regel deaktivieren, ohne sie zu löschen.

#### Regeln verwalten

- **Anlegen:** Akkordeon-Formular auf der Regeln-Seite. Name und mindestens ein
  Suchbegriff (Debitor oder Verwendung) sind Pflicht.
- **Bearbeiten:** Stift-Symbol in der Regelliste öffnet das Bearbeitungsformular.
- **Löschen:** Papierkorb-Symbol öffnet eine Bestätigungsseite. Ist die Regel noch
  mit Transaktionen verknüpft, zeigt die Seite einen Hinweis mit der Anzahl – beim
  Löschen wird nur die Verknüpfung entfernt, die Transaktionen selbst bleiben
  unverändert.

#### Bestehende Transaktionen neu kategorisieren

Über den Button **Regeln anwenden** auf der Regeln-Seite lassen sich die aktiven
Regeln auf alle bereits importierten Transaktionen anwenden – nützlich nach
Regeländerungen:

- Vorherige **automatische** Zuweisungen werden entfernt und aus den aktuell
  aktiven Regeln neu aufgebaut; Transaktionen ohne passende Regel werden
  unkategorisiert
- **Manuelle Zuweisungen bleiben unberührt**
- Die **Vorhersagen** werden dabei nicht aktualisiert – dafür gibt es den
  Button auf der Vorhersagen-Seite bzw. `uv run manage.py update_predictions`

### Vorhersagen

Aus der Historie wird pro Empfänger (und Kategorie) berechnet, wie oft Zahlungen
wiederkehren:

- Durchschnittliches Intervall zwischen zwei Zahlungen
- Voraussichtlicher nächster Zahlungstermin
- **Confidence** (0–100 %): je höher, desto regelmäßiger sind die bisherigen Zahlungen

Mindestens zwei Buchungen desselben Empfängers sind nötig, damit eine Vorhersage
entsteht. Die Berechnung läuft nicht automatisch – aktualisieren entweder über
den Button auf der Vorhersagen-Seite oder per Kommandozeile:

```powershell
uv run manage.py update_predictions
```

Am besten nach jedem größeren Import ausführen.

### EÜR-Bericht

Jahresübersicht zur Einnahmen-Überschuss-Rechnung:

- Auswahl des Jahres (aktuelles Jahr ist vorausgewählt)
- Tabelle mit Monat, Einnahmen, Ausgaben und Saldo
- Jahressummen am Ende der Tabelle

Positive Salden werden grün, negative rot dargestellt.

---

## Duplikatschutz

Es ist unkritisch, eine Datei mehrfach anzubieten – es wird sichergestellt,
dass **kein Duplikat jemals in der Datenbank gespeichert wird**:

1. **Dateiebene (MD5):** Wurde eine Datei mit identischem Inhalt schon einmal
   importiert, bricht der Import sofort mit einer Meldung samt ursprünglichem
   Importdatum ab. Dabei zählt nur der Dateiinhalt, nicht der Dateiname.
   Es wird kein neuer Eintrag angelegt und keine Transaktion verändert.
2. **Transaktionsebene (SHA-256):** Enthält eine neue Datei einzelne Buchungen,
   die bereits vorhanden sind, werden nur diese übersprungen und als Duplikate
   gezählt – der Rest wird normal importiert. Der Hash wird aus
   `Datum + Debitor + Betrag + Verwendung + Zielkonto + Quellkonto` gebildet
   und ist in der Datenbank als `UNIQUE` gesichert (`Transaction.hash`);
   identische Buchungen aus unterschiedlichen Dateien oder wiederholten Imports
   werden daher zuverlässig erkannt. Übersprungene Zeilen werden nicht
   gespeichert, nur in der Import-Historie als `Duplikate` gezählt.

---

## Admin-Interface (optional)

Für direkten Zugriff auf die Rohdaten steht das Django-Admin-Interface unter
`http://127.0.0.1:8000/admin/` bereit. Dafür muss zunächst ein Administrator-Konto
angelegt werden:

```powershell
uv run manage.py createsuperuser
```

---

## Import löschen

Auf der Seite **Import-Historie** (`/import/history/`) kann jeder Import über das
Papierkorb-Symbol restlos entfernt werden:

- Bestätigungsseite zeigt Dateiname, Zeitraum und Anzahl der betroffenen
  Transaktionen; alle zugehörigen Buchungen samt Kategorisierungen/Metadaten
  werden unwiderruflich gelöscht (DB-CASCADE).
- **PIN erforderlich:** Standard `1234` – änderbar über die Umgebungsvariable
  `FINMAN_DELETE_PIN` (z. B. `FINMAN_DELETE_PIN=meinpin uv run manage.py runserver`).
- Nach dem Löschen ist der `file_md5` wieder frei – dieselbe Datei kann bei
  Bedarf erneut importiert werden.
- Auch das Löschen direkt im Admin unter `/admin/` löst dieselbe Kaskade aus.

## Daten sichern und zurücksetzen

Alle Daten liegen in einer einzigen Datei: **`src/db.sqlite3`**

- **Backup:** Server stoppen, Datei kopieren – fertig.
- **Wiederherstellen:** Kopie zurück an dieselbe Stelle legen.
- **Komplett zurücksetzen:** Datei löschen und anschließend erneut
  `uv run manage.py migrate` ausführen.

---

## Fehlerbehebung

| Meldung / Problem | Bedeutung / Lösung |
|---|---|
| „Datei wurde bereits am TT.MM.JJJJ HH:MM importiert" | Diese Datei wurde schon importiert (Duplikatschutz). Es ist nichts zu tun. |
| „Kein passender Parser für diese Datei gefunden." | Format nicht erkennbar. Prüfen, ob es eine CSV mit Trennzeichen `;` oder `,` ist und Spalten für Datum, Betrag und Empfänger enthält. Details stehen im Log. |
| Import liefert viele „Übersprungen" | Diese Buchungen waren bereits in der Datenbank vorhanden (Duplikate innerhalb neuer Datei). Normal und unproblematisch. |
| Kein Parser-Ergebnis / unerwartetes Verhalten | Logdatei prüfen: `logs/parser_import.log` (im Projektverzeichnis). |
| Seite lädt ohne Styles | Bootstrap wird von einem CDN geladen – Internetverbindung prüfen. |
