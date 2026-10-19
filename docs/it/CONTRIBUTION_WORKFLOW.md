# Come lavorare alle traduzioni

L'[originale inglese](../CONTRIBUTION_WORKFLOW.md) è il riferimento in caso di differenze. Le correzioni di chi parla italiano come lingua madre sono benvenute. Comandi, nomi dei campi, intestazioni CSV e stati restano in inglese: il bot li legge esattamente come sono scritti.

Scrivi i comandi di questa guida come commenti nell'issue GitHub dell'incarico assegnato. Mantieni il comando in inglese esattamente come indicato.

## In breve

La traduzione si scrive e si rivede in Google Sheets. Un incarico su GitHub riserva l'ambito del lavoro, indica chi se ne occupa e permette di trasformare una copia approvata in una pull request (PR).

**Modificare il foglio non aggiorna il repository né il gioco.** Il bot importa una copia precisa già esaminata. Un responsabile del progetto deve ancora controllare e unire la PR; lo sviluppatore integra poi il risultato in una versione del gioco.

Questo flusso riguarda le stringhe dell'interfaccia già esistenti e le traduzioni scritte dei copioni vocali. Registrazioni, provini, nuove battute in bozza e testi senza ID sorgente seguono una preparazione separata. Le traduzioni della community devono essere consegnate tramite il bot: una PR manuale non può aggirare prenotazione e approvazione.

## Chi fa cosa

- **Collaboratore:** traduce le righe assegnate e chiede un'anteprima.
- **Revisore:** controlla contesto, terminologia, naturalezza e anteprima esatta; approva il suo digest dal proprio account GitHub.
- **Responsabile del progetto (maintainer):** concorda l'incarico, riserva le righe, gestisce gli accessi al foglio e controlla e unisce la PR.

Collaboratore e revisore devono essere utenti GitHub diversi. Il bot verifica identità e struttura dei file, non la qualità della lingua. Per tradurre basta Google Sheets: non occorre installare Git, clonare il repository o aprire personalmente una PR. Chi approva deve avere un account GitHub. Un maintainer può chiedere l'anteprima per chi ha bisogno di aiuto con i commenti GitHub.

## 1. Concordare un incarico piccolo

Candidati tramite l'issue per traduttori o un ticket Discord. Prima di iniziare, un maintainer concorda lingua, collaboratore, revisore e ambito. Il foglio privato delle candidature serve a raccogliere richieste: non riserva lavoro e i suoi contenuti non vanno copiati nelle issue pubbliche.

Apri un'issue [Translation work order](https://github.com/Epheria/Ebbtide-Community/issues/new?template=work_order.yml) con questi campi, lasciando invariati i nomi inglesi:

| Campo | Cosa inserire |
| --- | --- |
| Kind | `ui` oppure `voice-text` |
| Locale | Codice della lingua nel repository, per esempio `it`, `ja` o `pt-BR` |
| Table or voice role | Nome di una tabella o di un ruolo esistente, senza percorso né estensione `.csv` |
| Contributor | Un nome utente GitHub, senza `@` |
| Reviewer | Un altro nome utente GitHub, senza `@` |
| Spreadsheet URL | Indirizzo del documento Google Sheets usato per l'incarico |
| Sheet tab | Nome esatto della scheda |
| First key | Prima chiave sorgente esistente da includere |
| Last key | Ultima chiave sorgente esistente da includere |

L'intervallo comprende entrambi gli estremi e segue **l'ordine del file sorgente canonico**, non l'ordine alfabetico né quello attuale del foglio. Massimo 200 chiavi. Per i copioni, la chiave è l'identificatore `file`, senza `.wav` o `.flac`. Ogni incarico copre una sola lingua e una sola tabella UI o un solo ruolo vocale. Un ambito breve è più facile da rivedere e meno esposto ai cambiamenti del gioco.

## 2. Riservare il lavoro prima di tradurre

Un maintainer scrive nell'issue:

```text
/work assign
```

Aspetta la conferma del bot. Compilare o chiudere un'issue, oppure scrivere un nome nel foglio, non riserva né libera il lavoro.

Il bot registra l'incarico in `registry.json` sul branch `community-work-state` e fissa campi dell'issue, chiavi esatte e hash del sorgente. Rifiuta sovrapposizioni con incarichi attivi dello stesso tipo, lingua e tabella o ruolo. Lingue diverse possono lavorare sulle stesse chiavi.

Modificare il testo dell'issue non cambia un incarico attivo. Se cambiano ambito, documento, collaboratore o revisore, chiedi a un maintainer di liberarlo e creare una prenotazione corretta.

## 3. Scrivere nel foglio

Il maintainer prepara le righe sorgente aggiornate e concede la modifica alle persone assegnate. Il documento deve essere leggibile dal bot senza accesso Google, ma la modifica deve restare limitata alle persone coinvolte. Proteggi chiavi e inglese; concedi accesso solo alle celle necessarie. Non attivare la modifica per chiunque abbia il link. Accessi e protezioni si impostano manualmente: il bot GitHub non gestisce i permessi Google.

Per l'interfaccia conserva queste quattro colonne:

```text
key,en,translation,status
```

La scheda deve contenere righe di una sola tabella UI, quella dell'incarico. Un elenco che unisce più tabelle è un riferimento, non una scheda importabile direttamente. Il bot controlla tutte le righe compilate della scheda rispetto alla tabella sorgente.

Modifica `translation` e usa gli stati esistenti. Una riga UI può essere importata solo con `status` vuoto; `review` e `outdated` la bloccano. Lo stato vuoto non è un'approvazione: serve la revisione separata.

Per le traduzioni scritte dei copioni conserva esattamente queste intestazioni e questo ordine:

```text
Take file,English source,Translation,Review status,Notes,Role,Situation,Tone,Current voices,Source readiness,Source file,Source record
```

Le schede giapponese, russa e coreana esistenti usano questo formato. Il bot filtra il valore esatto di `Role`, per esempio `carrier_jet_pilot`, poi seleziona le chiavi `Take file` riservate. Compila `Translation` e, dopo la revisione del testo, imposta `Review status` su `Approved`.

Il testo approvato viene scritto in `voice/translations/<locale>/<role>.csv` con `key,en,translation,status`. Si importano solo battute scritte: questo non approva una registrazione né dimostra che una battuta in bozza sia già presente nel gioco.

In entrambi i casi:

- Conserva segnaposto, tag obbligatori e simboli di interruzione di riga.
- Non modificare chiavi o inglese rispetto al sorgente assegnato.
- Completa tutte le traduzioni riservate prima dell'anteprima.
- Tratta le celle come testo; non usare formule per recuperare o costruire traduzioni.
- Non inserire contatti privati, messaggi dei ticket o provini nel documento o nell'issue.

Se l'incarico è troppo grande, concorda una suddivisione o il rilascio con un maintainer invece di lasciarlo riservato a tempo indefinito.

## 4. Chiedere e controllare l'anteprima

Il collaboratore assegnato, il revisore assegnato o un maintainer commenta:

```text
/work preview
```

Il bot legge l'ambito riservato dall'esportazione CSV pubblica di Google Sheets. Controlla sorgente fissato, stati, traduzioni non vuote e variabili obbligatorie; registra anche la traduzione attuale nel repository, così l'approvazione potrà rilevare modifiche di altre persone.

Salva una copia immutabile e pubblica un link con il suo digest SHA-256. Il revisore deve leggere **quella copia**, non soltanto il riepilogo dell'issue o il foglio che può cambiare. Controlla significato e contesto, naturalezza e glossario, lunghezza UI o resa parlata, segnaposto, tag e a capo.

Se occorre correggere, modifica il foglio e ripeti `/work preview`. Usa il nuovo digest. Il link dell'anteprima permette di esaminare i contenuti, non autorizza l'unione della PR.

## 5. Approvare la copia esatta

Solo il revisore assegnato scrive questo comando, sostituendo il segnaposto con il digest completo di 64 caratteri dell'anteprima:

```text
/work approve <sha256>
```

Copia tutti i 64 caratteri dopo `Digest:` nella risposta del bot e sostituisci solo `<sha256>` nel comando. Non tradurre il comando e non inviare il segnaposto letterale.

Il bot verifica il revisore e rilegge il foglio, che deve coincidere con la copia approvata. Verifica anche che sorgente e contenuto di destinazione nel repository non siano cambiati. Se cambia il foglio o il file di destinazione, serve una nuova anteprima. Se cambia la tabella sorgente canonica, serve un nuovo incarico, come spiegato sotto.

Se tutto è valido, il bot apre una PR con i file controllati; **non la unisce**. Un valore `Approved` nel foglio o un semplice commento di assenso non sostituiscono il comando. Il lavoro resta riservato finché il maintainer non controlla il diff e unisce la PR dopo il superamento dei controlli. Discuti i file proposti nella PR.

La regola attendibile `reviewed-sheet` confronta la PR con l'incarico e la copia approvata. Legge i file della PR come dati ed esegue codice del branch predefinito. Rifiuta PR manuali di traduzione, file di consegna modificati e file aggiuntivi. Cambiare il branch del bot dopo l'approvazione non permette di sostituire il testo esaminato.

## 6. Completare o liberare la prenotazione

Dopo l'unione o la chiusura della PR, un maintainer esegue:

```text
/work sync
```

Una PR unita completa l'incarico; una PR chiusa senza unione lo libera. Controlla la conferma del bot: lo stato dell'issue da solo non basta. Il coordinatore sincronizza anche quando GitHub invia l'evento di chiusura di una PR registrata del bot. Se l'esecuzione automatica non termina, usa il comando manualmente. Per una PR aperta, `/work sync` richiede nuovamente i controlli se il loro avvio non è riuscito.

Per annullare un incarico senza PR, un maintainer commenta:

```text
/work release
```

Una PR aperta va chiusa prima del rilascio, per evitare due consegne attive dello stesso intervallo.

| Comando | Chi può usarlo | Risultato |
| --- | --- | --- |
| `/work assign` | Maintainer | Fissa l'incarico e riserva le chiavi. |
| `/work preview` | Collaboratore assegnato, revisore assegnato o maintainer | Controlla e salva una copia da rivedere. |
| `/work approve <sha256>` | Revisore assegnato | Ricontrolla la copia esatta e apre una PR. |
| `/work release` | Maintainer | Libera l'incarico se non esiste una PR aperta. |
| `/work sync` | Maintainer | Allinea il registro allo stato della PR. |

## Quando cambia il testo del gioco

Non creare un nuovo documento a ogni versione del gioco. Gli ID stabili permettono di conservare le traduzioni. Aggiungi nuove righe tramite l'aggiornamento dei sorgenti del repository e segnala i testi cambiati come descritto in [Localizzazione](../../localization/README.md).

L'incarico fissa l'intera tabella UI o l'intero ruolo vocale. Se quel sorgente canonico cambia prima dell'approvazione, il bot ferma l'importazione **anche se le chiavi riservate sono invariate**. Il maintainer chiude eventuali PR di consegna aperte, libera il vecchio incarico, aggiorna le righe sorgente nel foglio e apre **una nuova issue di lavoro**. Conserva la traduzione del volontario e controllala contro il nuovo sorgente; il revisore esamina poi una nuova anteprima. Gli incarichi su altre tabelle possono proseguire.

Una riga di pianificazione senza ID reale non è importabile. Aspetta che lo sviluppatore aggiunga la voce canonica: non inventare ID di produzione e non caricare un intero foglio per includere contenuti futuri.

## Configurazione e limiti per i maintainer

- Abilita il flusso solo dopo che codice e modulo dell'issue sono nel branch predefinito. Non modificare manualmente `community-work-state` durante l'esecuzione dei comandi.
- Il flusso usa `GITHUB_TOKEN` del repository con permessi per scrivere stato e branch del bot, commentare issue e creare PR. Non serve Google OAuth né un token personale; di Google viene letta solo l'esportazione CSV pubblica.
- Nelle impostazioni Actions consenti a GitHub Actions di creare PR. Il bot e il revisore umano devono restare identità separate.
- Non presumere che una PR del bot avvii i normali flussi `pull_request`. L'importatore convalida i file prima di aprirla e avvia esplicitamente `check.yml` sul branch del bot e `delivery-policy.yml` dal branch predefinito attendibile per il numero di PR.
- Proteggi il branch predefinito con entrambi i controlli obbligatori: `check` e lo stato commit `reviewed-sheet`. Il flusso della regola deve poter pubblicare questo stato. Controlla che entrambi abbiano successo prima dell'unione: creare i file del flusso non configura da solo la protezione del branch.
- Il registro blocca le assegnazioni sovrapposte e la regola obbligatoria impedisce alle PR manuali di aggirarle. Nessuno dei due gestisce i permessi dei fogli: limita la modifica e proteggi le colonne sorgente.

I controlli automatici rilevano errori di struttura e contenuti non aggiornati. Qualità della traduzione, contesto, condizioni di partecipazione e adeguatezza al gioco restano responsabilità della revisione umana.
