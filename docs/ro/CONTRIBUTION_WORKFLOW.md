# Cum lucrăm la traduceri

[Versiunea în engleză](../CONTRIBUTION_WORKFLOW.md) este referința în caz de diferențe. Corecturile propuse de vorbitori nativi de română sunt binevenite. Comenzile, numele câmpurilor, antetele CSV și valorile stărilor rămân în engleză: botul le citește exact.

Scrie comenzile din acest ghid sub formă de comentarii în issue-ul GitHub al sarcinii atribuite. Păstrează textul englezesc al comenzii exact ca în exemplu.

## Pe scurt

Traducerea se scrie și se verifică în Foi de calcul Google. O sarcină pe GitHub rezervă un anumit conținut, stabilește responsabilitățile și controlează transformarea unei copii aprobate într-un pull request (PR).

**Modificarea foii nu actualizează depozitul sau jocul.** Botul importă într-un PR o copie exactă, deja verificată. Un responsabil al proiectului trebuie să examineze și să integreze PR-ul; apoi dezvoltatorul adaugă rezultatul într-o versiune a jocului.

Acest proces acoperă textele existente ale interfeței și traducerile scrise ale scenariilor de voce. Înregistrările audio, audițiile, replicile noi în stadiu de propunere și textele fără ID sursă se pregătesc separat. Traducerile comunității se predau prin bot. Un PR de traducere deschis manual nu poate ocoli rezervarea și aprobarea copiei.

## Rolurile

- **Contributorul:** traduce rândurile atribuite și cere o previzualizare.
- **Revizorul:** verifică contextul, termenii, exprimarea firească și copia exactă; îi aprobă hash-ul din propriul cont GitHub.
- **Responsabilul proiectului (maintainer):** stabilește sarcina, rezervă intervalul, gestionează accesul la foaie și verifică și integrează PR-ul.

Contributorul și revizorul trebuie să fie utilizatori GitHub diferiți. Botul verifică identitatea și structura fișierelor, nu naturalețea traducerii. Pentru a traduce este suficient să lucrezi în Foi de calcul Google: nu trebuie să instalezi Git, să clonezi depozitul sau să deschizi singur un PR. Persoana care aprobă are nevoie de un cont GitHub. Dacă un contributor are nevoie de ajutor cu comentariile GitHub, un maintainer poate cere previzualizarea în numele lui.

## 1. Stabiliți o sarcină mică

Înscrie-te printr-un issue pentru traducători sau un tichet de asistență Discord. Înainte de lucru, un maintainer confirmă limba, contributorul, revizorul și conținutul. Foaia privată cu cereri este doar o listă de înscrieri, nu registrul rezervărilor. Nu copia informațiile ei în issue-uri publice.

Deschide un issue [Translation work order](https://github.com/Epheria/Ebbtide-Community/issues/new?template=work_order.yml). Păstrează numele englezești ale câmpurilor:

| Câmp | Ce completezi |
| --- | --- |
| Kind | `ui` sau `voice-text` |
| Locale | Codul limbii din depozit, de exemplu `ro`, `ja` sau `pt-BR` |
| Table or voice role | Numele unui tabel sursă sau al unui rol existent, fără cale și fără extensia `.csv` |
| Contributor | Un singur nume de utilizator GitHub, fără `@` |
| Reviewer | Un alt nume de utilizator GitHub, fără `@` |
| Spreadsheet URL | Adresa documentului Foi de calcul Google pentru această sarcină |
| Sheet tab | Numele exact al filei |
| First key | Prima cheie sursă existentă de inclus |
| Last key | Ultima cheie sursă existentă de inclus |

Intervalul include ambele capete și urmează **ordinea din fișierul sursă canonic**, nu ordinea alfabetică sau ordinea curentă din foaie. Sunt permise cel mult 200 de chei. Pentru textele de voce, cheia este identificatorul `file` din scenariu, fără `.wav` sau `.flac`.

Folosește o singură limbă și un singur tabel UI sau rol de voce pentru fiecare sarcină. Un interval scurt este mai ușor de verificat și produce mai puține conflicte când se schimbă jocul.

## 2. Rezervați conținutul înainte de traducere

Un maintainer adaugă comentariul:

```text
/work assign
```

Așteaptă confirmarea botului. Completarea sau închiderea unui issue ori scrierea unui nume în foaie nu rezervă și nu eliberează sarcina.

Botul înregistrează atribuirea în `registry.json` pe ramura `community-work-state`. Fixează câmpurile issue-ului, cheile exacte și hash-ul sursei. Respinge suprapunerea cu altă sarcină activă de același tip, limbă și tabel sau rol. Limbile diferite pot lucra pe aceleași chei.

Modificarea ulterioară a descrierii issue-ului nu schimbă atribuirea activă. Dacă trebuie schimbate intervalul, documentul, contributorul sau revizorul, cere unui maintainer să elibereze sarcina și să creeze o rezervare corectă.

## 3. Lucrați în foaie

Maintainerul pregătește rândurile sursă actuale și oferă drept de editare persoanelor atribuite. Botul trebuie să poată citi documentul fără autentificare Google, însă editarea trebuie limitată la participanții la acea sarcină. Protejează cheile și engleza și permite editarea doar în celulele necesare. Nu activa editarea pentru oricine are linkul. Permisiunile și intervalele protejate se configurează manual; botul GitHub nu gestionează permisiunile Google.

Pentru interfață păstrează cele patru coloane:

```text
key,en,translation,status
```

Fila trebuie să conțină rânduri dintr-un singur tabel UI, cel indicat în sarcină. O listă care combină mai multe tabele este un material de referință, nu o filă importabilă direct. Botul verifică toate rândurile completate din fila aleasă față de acel tabel sursă.

Editează `translation` și folosește valorile existente din `status`. Un rând UI poate fi importat doar când `status` este gol. `review` și `outdated` blochează importul. Starea goală nu înseamnă aprobare: este necesară verificarea separată.

Pentru traducerile scrise ale scenariilor, antetele și ordinea trebuie să fie exact:

```text
Take file,English source,Translation,Review status,Notes,Role,Situation,Tone,Current voices,Source readiness,Source file,Source record
```

Filele existente pentru japoneză, rusă și coreeană folosesc acest format. Botul filtrează după valoarea exactă `Role`, de exemplu `carrier_jet_pilot`, apoi alege cheile `Take file` rezervate. Completează `Translation` și setează `Review status` la `Approved` pentru rândurile verificate.

Textul aprobat este scris în `voice/translations/<locale>/<role>.csv` cu coloanele `key,en,translation,status`. Se importă doar replicile scrise; acest pas nu aprobă o înregistrare și nu confirmă că o replică propusă este implementată în joc.

Pentru ambele tipuri de sarcini:

- Păstrează variabilele, etichetele obligatorii și marcajele de rând nou.
- Cheia și engleza trebuie să rămână identice cu sursa atribuită.
- Completează toate traducerile din interval înainte de previzualizare.
- Folosește text, nu formule care descarcă sau compun traduceri.
- Nu pune date private de contact, mesaje din tichete sau audiții în documentul de lucru ori în issue.

Dacă sarcina este prea mare, stabilește cu un maintainer împărțirea sau eliberarea ei, în loc să lași pe termen nelimitat un interval rezervat și neterminat.

## 4. Cereți și verificați previzualizarea

Contributorul atribuit, revizorul atribuit sau un maintainer comentează:

```text
/work preview
```

Botul citește intervalul rezervat din exportul CSV public al documentului Google. Verifică sursa fixată, stările, faptul că traducerile nu sunt goale și variabilele obligatorii. Verifică și traducerea actuală din depozit, astfel încât aprobarea ulterioară să detecteze modificările altcuiva.

Salvează o copie care nu mai poate fi modificată și publică linkul ei împreună cu hash-ul SHA-256. Verifică **acea copie**, nu doar rezumatul issue-ului sau foaia curentă, care se poate schimba. Revizorul verifică sensul și contextul, exprimarea firească și glosarul, lungimea în interfață sau rostirea, poziția variabilelor, etichetele și rândurile noi.

Dacă sunt necesare corecturi, editează foaia și execută din nou `/work preview`. Folosește noul hash. Linkul este un material de verificat, nu o permisiune de integrare a PR-ului.

## 5. Aprobați copia exactă

Numai revizorul atribuit scrie comanda, înlocuind exemplul cu hash-ul complet de 64 de caractere din previzualizare:

```text
/work approve <sha256>
```

Copiază toate cele 64 de caractere de după `Digest:` din răspunsul botului cu previzualizarea și înlocuiește numai `<sha256>` din comandă. Nu traduce comanda și nu trimite textul `<sha256>` ca atare.

Botul verifică revizorul și recitește foaia, care trebuie să coincidă cu copia aprobată. Verifică și dacă sursa sau conținutul destinație din depozit s-au schimbat după previzualizare. O schimbare a foii sau a fișierului destinație cere o nouă previzualizare. O schimbare a tabelului sursă canonic cere o nouă sarcină, conform secțiunii de mai jos.

La succes, botul deschide un PR cu fișierele validate; **nu îl integrează**. Valoarea `Approved` din foaie sau un simplu comentariu de acord nu înlocuiesc comanda. Conținutul rămâne rezervat până când maintainerul examinează diferențele și integrează PR-ul după trecerea verificărilor. Discuțiile despre fișierele propuse se poartă în PR.

Politica de încredere `reviewed-sheet` compară PR-ul cu sarcina înregistrată și copia aprobată. Citește fișierele PR-ului ca date și rulează cod de încredere de pe ramura implicită. Respinge un PR manual de traducere, un fișier de predare modificat sau fișiere suplimentare adăugate în predare. Modificarea ramurii botului după aprobare nu poate înlocui textul verificat cu altul.

## 6. Încheiați sau eliberați rezervarea

După integrarea sau închiderea PR-ului, un maintainer execută:

```text
/work sync
```

Un PR integrat încheie sarcina; unul închis fără integrare o eliberează. Verifică răspunsul botului, nu presupune că starea issue-ului a schimbat rezervarea. Coordonatorul sincronizează și când GitHub trimite evenimentul de închidere pentru un PR înregistrat al botului. Dacă execuția automată nu s-a terminat, folosește comanda manual. Pentru un PR deschis, `/work sync` cere din nou verificările dacă lansarea lor a eșuat după crearea PR-ului.

Pentru anularea unei atribuiri fără PR, un maintainer comentează:

```text
/work release
```

Un PR deschis trebuie închis înainte de eliberare, ca să nu existe două predări active pentru același interval.

| Comandă | Cine o poate folosi | Rezultat |
| --- | --- | --- |
| `/work assign` | Maintainer | Fixează sarcina și rezervă intervalul. |
| `/work preview` | Contributorul atribuit, revizorul atribuit sau maintainerul | Validează și salvează o copie pentru verificare. |
| `/work approve <sha256>` | Revizorul atribuit | Reverifică exact copia și deschide un PR. |
| `/work release` | Maintainer | Anulează rezervarea dacă nu există un PR deschis. |
| `/work sync` | Maintainer | Aliniază starea PR-ului cu registrul. |

## Când se schimbă textul jocului

Nu crea un document nou pentru fiecare versiune a jocului. ID-urile stabile permit păstrarea traducerilor. Adaugă rândurile noi prin procesul de actualizare a sursei din depozit și marchează traducerile schimbate pentru revizuire, conform [ghidului de localizare](../../localization/README.md).

O sarcină fixează sursa **întregului tabel UI sau a întregului rol de voce**. Dacă acel tabel canonic se schimbă înainte de aprobare, botul oprește importul, chiar dacă cheile rezervate sunt neschimbate. Maintainerul închide eventualul PR de predare deschis, eliberează vechea sarcină, actualizează rândurile sursă din foaie și deschide **un issue de lucru nou**. Păstrează traducerea voluntarului și compar-o cu sursa actualizată; revizorul verifică apoi o nouă previzualizare. Sarcinile pentru alte tabele sursă pot continua.

Un rând planificat fără ID sursă real nu este pregătit pentru import. Lasă-l în planificare până când dezvoltatorul adaugă intrarea canonică. Nu inventa ID-uri de producție și nu încărca întregul document doar pentru a include conținut viitor.

## Configurare și limite pentru maintainers

- Activează procesul numai după integrarea codului și a formularului issue în ramura implicită. Nu modifica manual registrul `community-work-state` în timpul comenzilor active.
- Procesul folosește `GITHUB_TOKEN` al depozitului, cu permisiuni de scriere pentru stare și ramura botului, comentarii la issue-uri și creare de PR-uri. Nu cere Google OAuth sau un token personal. Accesul Google se limitează la citirea CSV-ului public.
- În setările Actions permite crearea PR-urilor de către GitHub Actions. Identitatea botului trebuie separată de cea a revizorului uman.
- Nu presupune că un PR al botului lansează fluxurile obișnuite `pull_request`. Importatorul validează fișierele înainte de crearea PR-ului și lansează explicit `check.yml` pentru ramura botului și `delivery-policy.yml` din ramura implicită de încredere pentru numărul respectiv de PR.
- Protejează ramura implicită cu ambele verificări obligatorii: `check` și starea de commit `reviewed-sheet`. Fluxul politicii trebuie să poată publica această stare. Verifică succesul ambelor înainte de integrare: fișierele fluxurilor nu configurează singure protecția ramurii.
- Registrul împiedică suprapunerea sarcinilor, iar politica obligatorie împiedică ocolirea lor prin PR-uri manuale de traducere. Niciuna nu gestionează permisiunile Google. Limitează editarea și protejează coloanele sursă.

Verificările automate găsesc probleme de structură și conținut învechit. Calitatea traducerii, contextul, condițiile de contribuție și potrivirea cu jocul rămân responsabilitatea oamenilor.
