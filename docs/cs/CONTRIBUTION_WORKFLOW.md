# Jak pracovat na překladech

> **Odevzdání nahrávek:** viz [návod pro nahrávky v soukromém Drive (anglicky)](../VOICE_SUBMISSIONS.md). Po nahrání a zaškrtnutí políček jiná osoba soubory poslechne a schválí. Teprve poté vznikne PR obsahující pouze seznam odevzdaných souborů. Audio zůstává v Drive. Pokyny níže se týkají překladu textu.

Při rozdílech platí [anglický originál](../CONTRIBUTION_WORKFLOW.md). Uvítáme jazykové opravy od rodilých mluvčích. Příkazy, názvy polí, hlavičky CSV a hodnoty stavů zůstávají anglicky, protože je bot čte přesně.

Příkazy z této příručky pište jako komentáře do issue přiděleného úkolu na GitHubu. Anglický text příkazu ponechte přesně podle ukázky.

## Základní princip

Překlad se píše a kontroluje v Tabulkách Google. Pracovní úkol na GitHubu rezervuje rozsah, určuje odpovědné osoby a řídí vytvoření pull requestu (PR) ze schválené kopie.

**Úprava tabulky neaktualizuje repozitář ani hru.** Bot převede do PR přesnou zkontrolovanou kopii. Správce projektu musí PR ještě zkontrolovat a sloučit; vývojář pak přidá výsledek do sestavení hry.

Tento postup pokrývá existující texty rozhraní a písemné překlady scénářů pro dabing. Nahrávky, hlasové zkoušky, návrhy nových replik a text bez zdrojového ID se připravují samostatně. Komunitní překlady odevzdávejte přes bota. Ručně vytvořený překladový PR nemůže obejít rezervaci a schválení kopie.

## Kdo co dělá

- **Přispěvatel:** překládá přidělené řádky a požádá o náhled.
- **Recenzent:** ověří kontext, názvosloví, přirozenost a přesný náhled; schválí jeho kontrolní otisk ze svého účtu GitHub.
- **Správce projektu (maintainer):** domluví úkol, rezervuje rozsah, nastaví přístup do tabulky a zkontroluje a sloučí PR.

Přispěvatel a recenzent musí být různí uživatelé GitHubu. Bot kontroluje totožnost a strukturu souborů, nikoli přirozenost češtiny. Překládat lze výhradně v Tabulkách Google: není nutné instalovat Git, klonovat repozitář ani vytvářet vlastní PR. Schvalující recenzent potřebuje účet GitHub. Pokud přispěvatel potřebuje pomoc s komentáři, může za něj o náhled požádat správce.

## 1. Domluvte si malý úkol

Přihlaste se přes existující issue pro překladatele nebo ticket podpory na Discordu. Před začátkem se správcem domluvte jazyk, přispěvatele, recenzenta a rozsah. Soukromá tabulka zájemců je jen vstupní fronta, nikoli registr rezervací. Její obsah nekopírujte do veřejných issue.

Otevřete issue [Translation work order](https://github.com/Epheria/Ebbtide-Community/issues/new?template=work_order.yml). Anglické názvy polí ponechte beze změny:

| Pole | Co vyplnit |
| --- | --- |
| Kind | `ui` nebo `voice-text` |
| Locale | Kód jazyka v repozitáři, například `cs`, `ja` či `pt-BR` |
| Table or voice role | Název existující zdrojové tabulky nebo hlasové role, bez cesty a přípony `.csv` |
| Contributor | Jedno přihlašovací jméno GitHub bez `@` |
| Reviewer | Jiné přihlašovací jméno GitHub bez `@` |
| Spreadsheet URL | Adresu dokumentu Tabulek Google pro tento úkol |
| Sheet tab | Přesný název listu |
| First key | První existující zdrojový klíč, který chcete zahrnout |
| Last key | Poslední existující zdrojový klíč, který chcete zahrnout |

Rozsah zahrnuje oba krajní klíče a používá **pořadí v kanonickém zdrojovém souboru**, nikoli abecedu nebo aktuální pořadí řádků v tabulce. Nejvýše 200 klíčů. U hlasového textu je klíčem identifikátor `file` ze scénáře bez `.wav` nebo `.flac`.

Jeden úkol smí zahrnovat jeden jazyk a jednu tabulku rozhraní nebo hlasovou roli. Krátký rozsah se lépe kontroluje a při změnách hry způsobuje méně konfliktů.

## 2. Před překládáním rozsah rezervujte

Správce napíše do issue:

```text
/work assign
```

Počkejte na potvrzení bota. Vyplnění či uzavření issue ani zapsání jména do tabulky samo práci nerezervuje nebo neuvolňuje.

Bot uloží přidělení do `registry.json` ve větvi `community-work-state`. Zafixuje pole issue, přesné klíče i hash zdroje. Odmítne překryv s jiným aktivním úkolem stejného druhu, jazyka a tabulky nebo role. Různé jazyky mohou pracovat na stejných klíčích.

Pozdější úprava těla issue aktivní zadání nemění. Pokud se mění rozsah, dokument, přispěvatel nebo recenzent, požádejte správce o uvolnění a správnou novou rezervaci.

## 3. Pište v tabulce

Správce připraví aktuální zdrojové řádky a udělí úpravy přiděleným lidem. Bot musí dokument přečíst bez přihlášení ke Googlu; právo upravovat ale má patřit pouze účastníkům práce. Chraňte zdrojové klíče a angličtinu a zpřístupněte jen potřebné vstupní buňky. Nepovolujte úpravy komukoli s odkazem. Oprávnění a chráněné oblasti nastavuje správce ručně, nikoli bot GitHubu.

Pro rozhraní zachovejte čtyři sloupce:

```text
key,en,translation,status
```

List musí obsahovat řádky jediné tabulky rozhraní uvedené v zadání. Souhrnný seznam několika tabulek je pouze podklad, nikoli přímo importovatelný pracovní list. Bot kontroluje všechny vyplněné řádky vybraného listu proti dané zdrojové tabulce.

Upravujte `translation` a používejte stávající hodnoty `status`. Řádek rozhraní lze importovat jen s prázdným `status`. Hodnoty `review` a `outdated` import pozastaví. Prázdný stav není schválení: je třeba samostatná kontrola.

Písemné překlady scénářů mají přesně tyto hlavičky v tomto pořadí:

```text
Take file,English source,Translation,Review status,Notes,Role,Situation,Tone,Current voices,Source readiness,Source file,Source record
```

Stávající japonský, ruský a korejský list používají tento formát. Bot vybere řádky podle přesné hodnoty `Role`, například `carrier_jet_pilot`, a potom rezervované klíče `Take file`. Vyplňte `Translation` a u jazykově zkontrolovaných řádků nastavte `Review status` na `Approved`.

Schválený text se zapíše do `voice/translations/<locale>/<role>.csv` s hlavičkou `key,en,translation,status`. Jde pouze o písemné repliky; tento krok neschvaluje nahrávku ani nepotvrzuje zapojení návrhu repliky do hry.

Pro oba druhy práce platí:

- Zachovejte proměnné, požadované značky a zápis zalomení řádků.
- Klíč i anglický text musí přesně odpovídat přidělenému zdroji.
- Před náhledem vyplňte celý rezervovaný rozsah.
- Používejte textové hodnoty, nikoli vzorce pro získání nebo sestavení překladu.
- Do pracovního dokumentu ani issue nepatří soukromé kontakty, zprávy z ticketů a hlasové zkoušky.

Je-li úkol příliš velký, domluvte se správcem rozdělení nebo uvolnění. Nenechávejte nedokončenou práci rezervovanou neomezeně dlouho.

## 4. Vyžádejte a zkontrolujte náhled

Přidělený přispěvatel, přidělený recenzent nebo správce napíše:

```text
/work preview
```

Bot přečte rezervovaný rozsah z veřejného CSV exportu Tabulek Google. Ověří zafixovaný zdroj, stavy, neprázdné překlady a povinné proměnné. Zkontroluje také současný překlad v repozitáři, aby při pozdějším schvalování odhalil změny jiných lidí.

Uloží neměnnou kopii a zveřejní její otisk SHA-256 s odkazem ke kontrole. Recenzent musí číst **tuto kopii**, nikoli jen shrnutí issue nebo živou tabulku, která se může změnit. Kontroluje význam a kontext, přirozenost a slovník, délku textu rozhraní nebo mluvený projev, umístění proměnných, značky a zalomení.

Pokud jsou nutné úpravy, opravte tabulku a spusťte `/work preview` znovu. Použijte nový otisk. Odkaz na náhled slouží ke kontrole, ne jako povolení ke sloučení.

## 5. Schvalte přesnou kopii

Pouze přidělený recenzent napíše příkaz a zástupný text nahradí úplným otiskem o 64 znacích:

```text
/work approve <sha256>
```

Zkopírujte všech 64 znaků za `Digest:` v odpovědi bota s náhledem a nahraďte jimi pouze `<sha256>` v příkazu. Příkaz nepřekládejte a zástupný text `<sha256>` neposílejte doslova.

Bot ověří recenzenta a znovu načte tabulku: musí odpovídat schválené kopii. Ověří také, že se od náhledu nezměnil zdroj ani cílový obsah repozitáře. Změna tabulky nebo cílového souboru vyžaduje nový náhled. Změna kanonické zdrojové tabulky vyžaduje nové zadání podle pokynů níže.

Při úspěchu bot otevře PR s ověřenými soubory; **nesloučí jej**. Hodnota `Approved` v tabulce ani běžný souhlasný komentář příkaz nenahrazují. Práce zůstává rezervovaná, dokud správce nezkontroluje rozdíly a po úspěšných kontrolách PR nesloučí. Připomínky k navrženým souborům řešte v PR.

Důvěryhodná zásada `reviewed-sheet` porovnává PR s registrovaným úkolem a schválenou kopií. Čte soubory PR jako data a spouští důvěryhodný kód z výchozí větve. Odmítne ruční překladový PR, pozměněný odevzdaný soubor i další přibalené soubory. Úprava větve bota po schválení neumožňuje nahradit zkontrolovaný text jiným.

## 6. Dokončete nebo uvolněte rezervaci

Po sloučení nebo uzavření PR správce spustí:

```text
/work sync
```

Sloučený PR úkol dokončí; uzavřený nesloučený PR jej uvolní. Ověřte potvrzení bota, nespoléhejte jen na stav issue. Koordinátor stav sjednotí také při události uzavření zaznamenaného PR bota. Pokud automatické spuštění neskončilo, použijte příkaz ručně. Pro otevřený PR `/work sync` znovu vyžádá kontroly, pokud se je nepodařilo spustit po vytvoření PR.

Ke zrušení úkolu bez PR správce napíše:

```text
/work release
```

Otevřený PR je nutné nejprve uzavřít. Tím se zabrání dvěma aktivním podáním stejného rozsahu.

| Příkaz | Kdo jej může použít | Výsledek |
| --- | --- | --- |
| `/work assign` | Správce | Zafixuje zadání a rezervuje rozsah. |
| `/work preview` | Přidělený přispěvatel, recenzent nebo správce | Ověří a uloží kopii ke kontrole. |
| `/work approve <sha256>` | Přidělený recenzent | Znovu ověří přesnou kopii a otevře PR. |
| `/work release` | Správce | Zruší rezervaci, pokud není otevřený PR. |
| `/work sync` | Správce | Sjednotí stav PR s registrem. |

## Když se změní text hry

Nevytvářejte nový dokument pro každou verzi hry. Stálá zdrojová ID umožňují zachovat překlady. Nové řádky přidávejte postupem aktualizace zdrojů v repozitáři a změněné překlady označte ke kontrole podle [lokalizační příručky](../../localization/README.md).

Zadání používá zafixovanou kopii **celé tabulky rozhraní nebo celé hlasové role**. Změní-li se před schválením kanonická tabulka, bot import zastaví, i když se rezervované klíče nezměnily. Správce uzavře případný otevřený odevzdávací PR, uvolní starý úkol, aktualizuje zdrojové řádky v tabulce a otevře **novou issue s úkolem**. Překlad dobrovolníka zachovejte a porovnejte s novým zdrojem; recenzent pak zkontroluje nový náhled. Úkoly k jiným zdrojovým tabulkám mohou pokračovat.

Plánovaný řádek bez skutečného zdrojového ID do importu nepatří. Nechte jej v plánování, dokud vývojář nepřidá kanonický záznam. Nevymýšlejte produkční ID ani nenahrávejte celý dokument kvůli budoucímu obsahu.

## Nastavení a omezení pro správce

- Zapněte postup až po sloučení kódu a formuláře issue do výchozí větve. Během aktivních příkazů neupravujte registr `community-work-state` ručně.
- Postup používá `GITHUB_TOKEN` repozitáře s oprávněním zapisovat stav a větev bota, komentovat issue a vytvářet PR. Nepotřebuje Google OAuth ani osobní přístupový token. Google slouží jen ke čtení veřejného CSV.
- V nastavení Actions povolte vytváření PR pomocí GitHub Actions. Identita bota musí být oddělená od lidského recenzenta.
- Nespoléhejte na spuštění běžných postupů `pull_request` po vytvoření PR botem. Importér ověří soubory předem a výslovně spustí `check.yml` pro větev bota a `delivery-policy.yml` z důvěryhodné výchozí větve pro dané číslo PR.
- Chraňte výchozí větev oběma povinnými kontrolami: `check` a stavem commitu `reviewed-sheet`. Postup zásady musí mít právo tento stav zveřejnit. Před sloučením ověřte úspěch obou: samotné soubory postupů ochranu větve nenastavují.
- Registr brání překryvům úkolů a povinná zásada brání jejich obcházení ručními překladovými PR. Ani jedno nespravuje oprávnění Tabulek Google. Omezte úpravy a chraňte zdrojové sloupce.

Automatické kontroly odhalují strukturální chyby a zastaralý obsah. Za kvalitu překladu, kontext, podmínky přispívání a vhodnost do hry nadále odpovídají lidé.
