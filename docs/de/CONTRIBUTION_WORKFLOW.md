# Übersetzungsaufträge

> **Sprachaufnahmen einreichen:** siehe die [Anleitung für Aufnahmen im privaten Drive (Englisch)](../VOICE_SUBMISSIONS.md). Nach Upload und Ankreuzen hört eine andere Person die Dateien an und gibt sie frei. Erst dann entsteht ein PR mit der Abgabeliste. Die Audiodateien bleiben in Drive. Die folgende Anleitung behandelt Textübersetzungen.

Dieser Leitfaden wurde mit KI-Unterstützung übersetzt. Maßgeblich ist die [englische Fassung](../CONTRIBUTION_WORKFLOW.md). Wenn du gut Deutsch sprichst, sind sprachliche Korrekturen willkommen. Diese Fassung wird nicht als muttersprachlich geprüft ausgegeben.

In Google Tabellen werden Übersetzungen geschrieben und geprüft. Ein Arbeitsauftrag als GitHub-Issue reserviert den Umfang, hält die Zuständigkeiten fest und bestimmt, wann eine geprüfte Kopie als Pull Request (PR) eingereicht werden kann.

**Eine Änderung in der Tabelle aktualisiert weder das Repository noch das Spiel.** Der Bot übernimmt eine genaue Kopie des geprüften Textes in einen PR. Ein Maintainer prüft und übernimmt diesen PR anschließend; der Entwickler baut das Ergebnis in eine Spielversion ein.

Dieser Ablauf gilt für vorhandene Oberflächentexte (`ui`) und schriftliche Übersetzungen von Sprechtexten (`voice-text`). Tonaufnahmen, Vorsprechen, neue Dialogentwürfe und Texte ohne Quell-ID haben einen eigenen Vorbereitungsprozess. Dieser Leitfaden teilt keine Arbeit zu: Warte vor dem Beginn auf die Bestätigung des Bots.

Übersetzungen aus der Community werden über den PR des Bots eingereicht. Ein manuell erstellter Übersetzungs-PR kann die Reservierung und Freigabe der geprüften Kopie nicht umgehen.

## Wer macht was?

| Rolle | Aufgabe |
| --- | --- |
| Übersetzer (`Contributor`) | Bearbeitet die zugeteilte Übersetzung in der Tabelle und fordert eine Vorschau an. |
| Prüfer (`Reviewer`) | Prüft Kontext, Begriffe, natürliche Sprache und die genaue Kopie. Gibt deren Hash mit dem eigenen GitHub-Konto frei. |
| Maintainer | Erstellt oder prüft den Auftrag, reserviert die Zeilen, verwaltet den Tabellenzugriff und prüft und übernimmt den PR. |

Übersetzer und Prüfer müssen **verschiedene GitHub-Benutzer** sein. Der Bot prüft Identität und Dateistruktur; die sprachliche Qualität wird von Menschen beurteilt.

Du kannst vollständig in Google Tabellen arbeiten. Du musst weder Git installieren noch das Repository klonen oder selbst einen PR erstellen. Für die Freigabe einer Vorschau ist ein GitHub-Konto nötig. Wenn du Hilfe mit GitHub-Kommentaren brauchst, kann ein Maintainer die Vorschau für dich anfordern.

## 1. Einen kleinen Auftrag vereinbaren

Melde dich über das vorhandene Bewerbungs-Issue für Übersetzer oder ein Support-Ticket in Discord. Vor Arbeitsbeginn vereinbart ein Maintainer Sprache, Übersetzer, Prüfer und Umfang.

Die private Bewerbertabelle dient nur zur Verwaltung der Anmeldungen. Sie ist nicht das Reservierungsregister. Ihre Inhalte dürfen nicht in öffentliche GitHub-Issues kopiert werden.

Öffne ein Issue mit dem Formular [Translation work order](https://github.com/Epheria/Ebbtide-Community/issues/new?template=work_order.yml). Die Feldnamen bleiben unverändert:

| Feld | Eingabe |
| --- | --- |
| Kind | `ui` oder `voice-text` |
| Locale | Sprachcode des Repositorys, zum Beispiel `ja`, `ru` oder `pt-BR` |
| Table or voice role | Name einer vorhandenen Quelltabelle oder Sprecherrolle, ohne Pfad und ohne `.csv` |
| Contributor | Ein GitHub-Benutzername ohne `@` |
| Reviewer | Ein anderer GitHub-Benutzername ohne `@` |
| Spreadsheet URL | Link zur Google-Tabelle für diesen Auftrag |
| Sheet tab | Genauer Name des Tabellenblatts |
| First key | Erster vorhandener Quellschlüssel des Bereichs |
| Last key | Letzter vorhandener Quellschlüssel des Bereichs |

Der Bereich enthält **beide Grenzen in der Reihenfolge der Quelldatei im Repository**. Es gilt weder die alphabetische Reihenfolge noch die aktuelle Zeilenfolge im Tabellenblatt. Er darf höchstens **200 Schlüssel** enthalten. Bei Sprechtexten ist der Schlüssel die Kennung `file` aus dem Skript, ohne `.wav` oder `.flac`.

Ein Auftrag umfasst eine Sprache und eine Oberflächentabelle oder Sprecherrolle. Kleine Bereiche sind leichter zu prüfen und verursachen weniger Konflikte bei Änderungen am Spieltext.

## 2. Vor dem Übersetzen reservieren

Ein Maintainer schreibt diesen Kommentar in das Issue:

```text
/work assign
```

Warte auf die Reservierungsbestätigung des Bots. Ein ausgefülltes oder geschlossenes Issue und ein Name in der Tabelle reservieren oder entsperren keine Arbeit.

Der Bot speichert den Auftrag in `registry.json` auf dem Branch `community-work-state`. Er fixiert die Issue-Felder, die genauen Quellschlüssel und den Hash der Quelle. Er verweigert Überschneidungen mit aktiven Aufträgen desselben Typs, derselben Sprache und derselben Tabelle oder Rolle. Verschiedene Sprachen können dieselben Quellschlüssel bearbeiten.

Spätere Änderungen am Issue-Text ändern den laufenden Auftrag nicht. Wenn sich Umfang, Tabelle, Übersetzer oder Prüfer ändern sollen, muss ein Maintainer die Reservierung aufheben und einen korrigierten neuen Auftrag anlegen.

## 3. In der Tabelle arbeiten

Ein Maintainer stellt die aktuellen Quellzeilen bereit und erteilt den zugeteilten Personen Bearbeitungsrechte. Der Bot muss die Tabelle ohne Google-Anmeldung lesen können. Bearbeiten dürfen sie aber nur die dafür vorgesehenen Personen.

Schütze Quellschlüssel und englischen Text. Mitwirkende erhalten nur Zugriff auf die benötigten Eingabezellen. Aktiviere nicht „Jeder mit dem Link darf bearbeiten“. Zugriffsrechte und geschützte Bereiche werden manuell eingerichtet; der GitHub-Bot verwaltet keine Google-Berechtigungen.

Für Oberflächentexte müssen diese vier CSV-Spalten erhalten bleiben:

```text
key,en,translation,status
```

Das Tabellenblatt enthält Zeilen aus **genau der einen Quelltabelle**, die im Auftrag steht. Eine Gesamtliste aus mehreren Tabellen ist eine Referenz und lässt sich nicht direkt als Arbeitsblatt importieren. Der Bot prüft alle ausgefüllten Zeilen des gewählten Blatts gegen diese Quelltabelle.

Bearbeite `translation` und verwende die vorhandenen Werte für `status`. Eine Oberflächenzeile kann nur importiert werden, wenn `status` **leer** ist. `review` und `outdated` halten die Zeile zurück. Ein leerer Status ist noch keine Freigabe: Die unabhängige Prüfung ist weiterhin erforderlich.

Für schriftliche Übersetzungen von Sprechtexten bleiben diese Spaltennamen in genau dieser Reihenfolge erhalten:

```text
Take file,English source,Translation,Review status,Notes,Role,Situation,Tone,Current voices,Source readiness,Source file,Source record
```

Die vorhandenen japanischen, russischen und koreanischen Blätter verwenden dieses Format. Der Bot filtert nach dem genauen Wert von `Role`, etwa `carrier_jet_pilot`, und wählt dann die reservierten `Take file`-Schlüssel. Fülle `Translation` aus und setze `Review status` für geprüfte Zeilen auf `Approved`.

Freigegebener Text wird unter `voice/translations/<locale>/<role>.csv` mit den Spalten `key,en,translation,status` gespeichert. Das importiert **nur geschriebenen Text**. Es gibt keine Tonaufnahme frei und bestätigt nicht, dass eine geplante Zeile bereits im Spiel umgesetzt ist.

Für beide Auftragsarten gilt:

- Platzhalter, erforderliche Tags und Codes für Zeilenumbrüche bleiben erhalten.
- Schlüssel und englischer Text müssen exakt mit der zugeteilten Quelle übereinstimmen.
- Fülle alle Übersetzungen des reservierten Bereichs aus, bevor du eine Vorschau anforderst.
- Behandle Zellen als Text. Verwende keine Formeln zum Abrufen oder Erzeugen von Übersetzungen.
- Private Kontaktdaten, Ticketnachrichten und Aufnahmen zum Vorsprechen gehören nicht in die Tabelle oder das öffentliche Issue.

Wenn du einen Auftrag nicht abschließen kannst, vereinbare mit einem Maintainer eine Aufteilung oder Aufhebung der Reservierung. Halbfertige Arbeit sollte nicht auf unbestimmte Zeit blockiert bleiben.

## 4. Eine Vorschau anfordern und prüfen

Der zugeteilte Übersetzer, der zugeteilte Prüfer oder ein Maintainer kommentiert:

```text
/work preview
```

Der Bot liest den reservierten Bereich über den öffentlichen CSV-Export von Google Tabellen. Er prüft die fixierte Quelle, Statuswerte, ausgefüllte Übersetzungen und benötigte Variablen. Auch die aktuelle Übersetzung im Repository wird erfasst, damit spätere Änderungen anderer Personen vor der Freigabe erkannt werden.

Der Bot speichert eine unveränderliche Kopie und veröffentlicht ihren SHA-256-Hash mit einem Prüf-Link. Prüfe **diese Kopie**, nicht nur die Issue-Zusammenfassung oder die gerade geöffnete Tabelle. Die Tabelle kann sich nach der Vorschau ändern.

Der Prüfer kontrolliert:

- Bedeutung und Kontext anhand des englischen Originals.
- Natürliche Formulierungen und einheitliche Begriffe aus dem Glossar.
- Verfügbaren Platz in der Oberfläche oder die gesprochene Formulierung, je nach Aufgabe.
- Platzhalterpositionen, Tags und Zeilenumbrüche.

Sind Änderungen nötig, bearbeite die Tabelle und führe `/work preview` erneut aus. Verwende den neuen Hash. Der Vorschau-Link dient der Prüfung und ist keine Erlaubnis zum Zusammenführen.

## 5. Genau diese Kopie freigeben

**Nur der zugeteilte Prüfer** kommentiert und ersetzt `<sha256>` durch den vollständigen Hash aus der Vorschau:

Poste die Befehle als Kommentare im zugeteilten GitHub-Arbeits-Issue. Kopiere für die Freigabe alle 64 Zeichen nach `Digest:` aus der Vorschauantwort des Bots und ersetze im Beispiel nur `<sha256>`; der Befehl bleibt auf Englisch, und der Platzhalter darf nicht unverändert gesendet werden.

```text
/work approve <sha256>
```

Der Bot prüft den Benutzer, liest die Tabelle erneut und verlangt eine genaue Übereinstimmung mit der geprüften Kopie. Außerdem dürfen sich Quelle und Zieldatei im Repository seit der Vorschau nicht geändert haben. Eine geänderte Tabelle oder Zieldatei verlangt eine neue Vorschau. Eine geänderte Quelltabelle verlangt einen neuen Auftrag, wie unten beschrieben.

Bei Erfolg erstellt der Bot einen PR mit den geprüften Dateien. **Er führt ihn nicht zusammen.** `Approved` in der Tabelle oder ein Kommentar wie „Sieht gut aus“ ersetzt diesen Befehl nicht.

Ein Maintainer prüft den Diff und übernimmt den PR nach erfolgreichen Kontrollen. Bis dahin bleibt die Arbeit reserviert. Diskussionen über die vorgeschlagenen Dateien gehören in diesen PR.

Die vertrauenswürdige Prüfung `reviewed-sheet` vergleicht den PR mit seinem registrierten Auftrag und der freigegebenen Kopie. Sie liest PR-Dateien als Daten und führt ausschließlich vertrauenswürdigen Code vom Standardbranch aus. Manuelle Übersetzungs-PRs, nachträglich geänderte Lieferdateien und zusätzliche Dateien in einer Übersetzungslieferung werden abgewiesen. Eine Änderung am Bot-Branch kann den freigegebenen Text nicht ersetzen.

## 6. Den Auftrag abschließen oder die Reservierung aufheben

Nach dem Zusammenführen oder Schließen des PRs führt ein Maintainer Folgendes aus:

```text
/work sync
```

Ein übernommener PR schließt den Auftrag ab. Ein ohne Übernahme geschlossener PR gibt die Reservierung frei. Prüfe die Bot-Bestätigung, statt vom Issue-Status auf den Registerstand zu schließen.

Der Koordinator synchronisiert registrierte Bot-PRs auch automatisch beim GitHub-Ereignis zum Schließen. Nutze `/work sync`, wenn dieser Lauf nicht abgeschlossen wurde. Bei einem offenen PR fordert der Befehl außerdem dessen Prüfungen erneut an, etwa nach einem Fehler beim Start der Prüfungen.

Um einen Auftrag vor Erstellung eines PRs abzubrechen, kommentiert ein Maintainer:

```text
/work release
```

Ein offener PR muss vor Aufhebung der Reservierung geschlossen werden. So entstehen keine zwei aktiven Einreichungen für denselben Bereich.

## Befehlsübersicht

| Befehl | Wer darf ihn verwenden? | Ergebnis |
| --- | --- | --- |
| `/work assign` | Maintainer | Fixiert den Auftrag und reserviert die Schlüssel. |
| `/work preview` | Zugeteilter Übersetzer, zugeteilter Prüfer oder Maintainer | Prüft und speichert eine Vorschau. |
| `/work approve <sha256>` | Zugeteilter Prüfer | Prüft genau diese Kopie erneut und erstellt einen PR. |
| `/work release` | Maintainer | Hebt eine Reservierung ohne offenen PR auf. |
| `/work sync` | Maintainer | Gleicht PR und Register ab; bei einem offenen PR werden die Prüfungen erneut angefordert. |

## Wenn sich Spieltexte ändern

Lege nicht für jede Spielversion eine neue Google-Tabelle an. Stabile Quell-IDs erhalten vorhandene Übersetzungen bei normalen Aktualisierungen. Neue Zeilen werden über den Aktualisierungsprozess des Repositorys ergänzt; betroffene Übersetzungen werden zur Prüfung markiert. Siehe [Lokalisierung](../../localization/README.md).

Ein Auftrag fixiert den Stand der **gesamten Oberflächentabelle oder Sprecherrolle**. Ändert sich diese Quelle vor der Freigabe, stoppt der Import, auch wenn die reservierten Schlüssel unverändert sind. Ein Maintainer schließt offene Liefer-PRs, hebt die alte Reservierung auf, aktualisiert die Quellzeilen im Tabellenblatt und erstellt **ein neues Arbeits-Issue**. Bereits geschriebene Übersetzungen bleiben erhalten und werden mit der aktualisierten Quelle verglichen. Danach prüft der Prüfer eine neue Vorschau. Aufträge anderer Quelltabellen können weiterlaufen.

Eine Planungszeile ohne echte Quell-ID ist noch nicht importierbar. Sie bleibt in der Planung, bis der Entwickler den offiziellen Quelleintrag hinzufügt. Erfinde keine produktiven IDs und lade nicht wegen zukünftiger Inhalte ein ganzes Tabellenwerk hoch.

## Einrichtung und Grenzen für Maintainer

Aktiviere den Ablauf erst, nachdem Code und Issue-Formular im Standardbranch zusammengeführt wurden. Das Register liegt auf `community-work-state`; bearbeite es während laufender Befehle nicht manuell.

Der Ablauf verwendet das `GITHUB_TOKEN` des Repositorys mit Berechtigungen zum Schreiben des Registers und Bot-Branches, zum Kommentieren von Issues und zum Erstellen von PRs. Weder eine Google-OAuth-Verbindung noch ein persönliches Zugriffstoken ist nötig. Der Google-Zugriff beschränkt sich auf den öffentlichen CSV-Export.

Erlaube GitHub Actions in den Actions-Einstellungen das Erstellen von PRs. Bot-Identität und menschlicher Sprachprüfer bleiben getrennt.

Verlasse dich nicht darauf, dass ein Bot-PR automatisch gewöhnliche `pull_request`-Workflows startet. Der Importer prüft seine Dateien und startet ausdrücklich `check.yml` für den Bot-Branch und `delivery-policy.yml` vom vertrauenswürdigen Standardbranch für die betreffende PR-Nummer.

Schütze den Standardbranch durch die beiden erforderlichen Prüfungen `check` und den Commit-Status `reviewed-sheet`. Der Richtlinien-Workflow muss diesen Status veröffentlichen dürfen. Prüfe beide vor der Übernahme: Workflow-Dateien allein richten keinen Branchschutz ein.

Das Register verhindert überlappende Aufträge. Die verpflichtende Lieferprüfung verhindert, dass manuelle Übersetzungs-PRs diese Aufträge umgehen. Beide verwalten keine Google-Berechtigungen: Beschränke die Bearbeitungsrechte und schütze die Quellspalten.

Automatische Prüfungen erkennen Strukturfehler und veraltete Inhalte. Übersetzungsqualität, Kontext, Beitragsbedingungen und Eignung für das Spiel bleiben Aufgabe der menschlichen Prüfung.
