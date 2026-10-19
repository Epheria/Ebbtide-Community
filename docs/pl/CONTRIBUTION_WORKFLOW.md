# Zadania tłumaczeniowe

Ten przewodnik przetłumaczono z pomocą AI. Punktem odniesienia jest [wersja angielska](../CONTRIBUTION_WORKFLOW.md). Jeśli dobrze znasz polski, uwagi językowe są mile widziane. Nie przedstawiamy tej wersji jako sprawdzonej przez rodzimego użytkownika języka.

Arkusze Google służą do pisania i weryfikacji tłumaczeń. Zadanie w GitHubie rezerwuje zakres, wskazuje odpowiedzialne osoby i określa, kiedy sprawdzona kopia może trafić do pull requesta (PR).

**Zmiana w arkuszu nie aktualizuje repozytorium ani gry.** Bot przenosi dokładną kopię sprawdzonego tekstu do PR. Opiekun repozytorium nadal musi przejrzeć i scalić ten PR, a deweloper dodaje wynik do jednej z wersji gry.

Proces obejmuje istniejące teksty interfejsu (`ui`) i pisemne tłumaczenia kwestii do nagrań głosowych (`voice-text`). Nagrania, przesłuchania, nowe dialogi i teksty bez identyfikatora źródłowego wymagają osobnego przygotowania. Samo opublikowanie przewodnika nie przydziela zadań: przed rozpoczęciem poczekaj na potwierdzenie bota.

Tłumaczenia społeczności są dostarczane przez PR utworzony przez bota. Ręczne otwarcie PR z tłumaczeniem nie pozwala ominąć rezerwacji ani zatwierdzenia sprawdzonej kopii.

## Kto za co odpowiada

| Osoba | Odpowiedzialność |
| --- | --- |
| Tłumacz (`Contributor`) | Wpisuje przydzielone tłumaczenie w arkuszu i prosi o podgląd. |
| Weryfikator (`Reviewer`) | Sprawdza kontekst, terminy, naturalność i dokładną kopię tekstu. Zatwierdza jej skrót za pomocą własnego konta GitHub. |
| Opiekun repozytorium | Tworzy lub sprawdza zadanie, rezerwuje zakres, zarządza dostępem do arkusza, przegląda PR i go scala. |

Tłumacz i weryfikator muszą być **różnymi użytkownikami GitHuba**. Bot sprawdza tożsamość i strukturę plików; ocenę języka przeprowadzają ludzie.

Możesz pracować wyłącznie w Arkuszach Google, bez instalowania Gita, klonowania repozytorium i tworzenia własnego PR. Osoba zatwierdzająca podgląd potrzebuje konta GitHub. Jeśli potrzebujesz pomocy z komentarzami w GitHubie, opiekun może poprosić o podgląd w twoim imieniu.

## 1. Uzgodnij niewielkie zadanie

Zgłoś się przez istniejący formularz dla tłumaczy lub ticket pomocy na Discordzie. Przed rozpoczęciem opiekun uzgadnia język, tłumacza, weryfikatora i zakres.

Prywatny arkusz kandydatów służy tylko do obsługi zgłoszeń. Nie jest rejestrem rezerwacji, a jego zawartości nie należy kopiować do publicznych issues.

Otwórz issue przez formularz [Translation work order](https://github.com/Epheria/Ebbtide-Community/issues/new?template=work_order.yml). Zachowaj te nazwy pól:

| Pole | Co wpisać |
| --- | --- |
| Kind | `ui` lub `voice-text` |
| Locale | Kod języka używany w repozytorium, np. `ja`, `ru` lub `pt-BR` |
| Table or voice role | Nazwa istniejącej tabeli źródłowej lub roli głosowej, bez ścieżki i rozszerzenia `.csv` |
| Contributor | Jeden login GitHub, bez `@` |
| Reviewer | Login innego użytkownika GitHub, bez `@` |
| Spreadsheet URL | Link do pliku Arkuszy Google używanego w tym zadaniu |
| Sheet tab | Dokładna nazwa zakładki arkusza |
| First key | Pierwszy istniejący klucz źródłowy w zakresie |
| Last key | Ostatni istniejący klucz źródłowy w zakresie |

Zakres obejmuje **obie granice w kolejności pliku źródłowego w repozytorium**. Nie chodzi o kolejność alfabetyczną ani aktualną kolejność wierszy w arkuszu. Limit to **200 kluczy**. Dla kwestii głosowych kluczem jest identyfikator `file` ze skryptu, bez `.wav` lub `.flac`.

Jedno zadanie obejmuje jeden język oraz jedną tabelę interfejsu lub rolę głosową. Niewielkie zakresy łatwiej sprawdzić i rzadziej powodują konflikty po zmianach tekstu gry.

## 2. Zarezerwuj przed tłumaczeniem

Opiekun dodaje w issue komentarz:

```text
/work assign
```

Poczekaj na potwierdzenie rezerwacji przez bota. Wypełnienie lub zamknięcie issue ani wpisanie nazwiska w arkuszu nie rezerwuje i nie zwalnia pracy.

Bot zapisuje przydział w `registry.json` na gałęzi `community-work-state`. Utrwala pola issue, dokładny zestaw kluczy i skrót źródła. Odrzuca nakładanie się zakresów aktywnych zadań tego samego rodzaju, języka i tabeli lub roli. Różne języki mogą pracować na tych samych kluczach źródłowych.

Późniejsza edycja treści issue nie zmienia przydziału. Jeśli trzeba zmienić zakres, plik arkusza, tłumacza lub weryfikatora, poproś opiekuna o zwolnienie zadania i utworzenie nowej, poprawionej rezerwacji.

## 3. Pracuj w arkuszu

Opiekun udostępnia aktualne wiersze źródłowe i nadaje prawo edycji przydzielonym osobom. Bot musi móc odczytać plik bez logowania do Google, ale edytować powinny go wyłącznie osoby przy nim pracujące.

Chroń klucze i angielski tekst źródłowy. Udostępniaj do edycji tylko potrzebne komórki. Nie włączaj opcji „Każdy, kto ma link, może edytować”. Uprawnienia i chronione zakresy ustawia się ręcznie; bot GitHuba nie zarządza dostępem w Google.

Dla interfejsu zachowaj cztery kolumny CSV:

```text
key,en,translation,status
```

Zakładka powinna zawierać wiersze **jednej tabeli** wskazanej w zadaniu. Lista zbiorcza z kilku tabel służy jako materiał pomocniczy, ale nie nadaje się bezpośrednio do importu jako zakładka zadania. Bot porównuje wszystkie wypełnione wiersze zakładki z tą tabelą źródłową.

Edytuj `translation` i korzystaj z istniejących wartości `status`. Wiersz interfejsu jest gotowy do importu tylko wtedy, gdy `status` jest **pusty**. `review` i `outdated` wstrzymują import wiersza. Pusty status nie oznacza zatwierdzenia: osobna weryfikacja nadal jest wymagana.

Dla pisemnych tłumaczeń kwestii głosowych zachowaj dokładnie te nagłówki, w tej kolejności:

```text
Take file,English source,Translation,Review status,Notes,Role,Situation,Tone,Current voices,Source readiness,Source file,Source record
```

Ten układ mają istniejące zakładki japońska, rosyjska i koreańska. Bot filtruje wiersze według dokładnej wartości `Role`, np. `carrier_jet_pilot`, a następnie wybiera zarezerwowane klucze `Take file`. Wypełnij `Translation` i ustaw `Review status` na `Approved` dla sprawdzonych wierszy.

Zatwierdzony tekst trafia do `voice/translations/<locale>/<role>.csv` z kolumnami `key,en,translation,status`. Importowany jest **tylko tekst pisany**. Nie zatwierdza to nagrania ani nie potwierdza, że robocza kwestia została już zaimplementowana w grze.

W obu rodzajach zadań:

- Zachowaj zmienne, wymagane znaczniki i kody końca wiersza.
- Nie zmieniaj kluczy ani angielskiego tekstu przydzielonego źródła.
- Uzupełnij wszystkie tłumaczenia zarezerwowanego zakresu przed podglądem.
- Traktuj komórki jako tekst. Nie używaj formuł do pobierania lub generowania tłumaczeń.
- Nie umieszczaj prywatnych kontaktów, wiadomości z ticketów ani nagrań próbnych w arkuszu zadania lub publicznym issue.

Jeśli nie możesz skończyć zadania, uzgodnij z opiekunem jego podział lub zwolnienie. Nie pozostawiaj częściowo wykonanej pracy zarezerwowanej bez końca.

## 4. Poproś o podgląd i sprawdź go

Przydzielony tłumacz, przydzielony weryfikator lub opiekun dodaje komentarz:

```text
/work preview
```

Bot odczytuje zarezerwowany zakres z publicznego eksportu CSV Arkuszy Google. Sprawdza utrwalone źródło, stany, niepuste tłumaczenia i wymagane zmienne. Sprawdza też aktualne tłumaczenie w repozytorium, by przed zatwierdzeniem wykryć zmiany wprowadzone przez inne osoby.

Bot zapisuje niezmienną kopię i publikuje jej skrót SHA-256 wraz z linkiem do sprawdzenia. Weryfikuj **tę kopię**, a nie tylko podsumowanie issue lub aktualnie otwarty arkusz. Arkusz może się zmienić po utworzeniu podglądu.

Weryfikator sprawdza:

- Znaczenie i kontekst w odniesieniu do angielskiego źródła.
- Naturalność i zgodność terminów z glosariuszem.
- Długość w interfejsie lub brzmienie wypowiadanej kwestii, zależnie od zadania.
- Położenie zmiennych, znaczniki i podziały wierszy.

Jeśli potrzebna jest poprawka, zmień arkusz i ponownie uruchom `/work preview`. Użyj nowego skrótu. Link do podglądu służy weryfikacji; nie jest pozwoleniem na scalenie.

## 5. Zatwierdź dokładną kopię

**Tylko przydzielony weryfikator** dodaje komentarz, zastępując `<sha256>` pełnym skrótem z podglądu:

Komendy publikuj jako komentarze w issue przydzielonego zadania na GitHubie. Aby zatwierdzić, skopiuj wszystkie 64 znaki po `Digest:` z odpowiedzi bota z podglądem i zastąp w przykładzie tylko `<sha256>`; pozostaw komendę po angielsku i nie wysyłaj tego znacznika dosłownie.

```text
/work approve <sha256>
```

Bot sprawdza tożsamość weryfikatora, ponownie pobiera arkusz i wymaga zgodności z zatwierdzaną kopią. Kontroluje też, czy źródło i plik docelowy repozytorium nie zmieniły się od podglądu. Zmiana arkusza lub pliku docelowego wymaga nowego podglądu. Zmiana tabeli źródłowej wymaga nowego przydziału, zgodnie z opisem poniżej.

Po pomyślnej kontroli bot otwiera PR ze sprawdzonymi plikami. **Nie scala go.** Wartość `Approved` w arkuszu ani komentarz „wygląda dobrze” nie zastępują tej komendy.

Opiekun przegląda różnice i scala PR po przejściu kontroli. Do tego czasu zakres pozostaje zarezerwowany. Dyskusje o proponowanych plikach prowadźcie w tym PR.

Zaufana kontrola `reviewed-sheet` porównuje PR z zapisanym zadaniem i zatwierdzoną kopią. Odczytuje pliki PR jako dane i wykonuje zaufany kod z gałęzi domyślnej. Odrzuca ręczne PR z tłumaczeniami, zmieniony plik dostawy i dodatkowe pliki dołączone do zatwierdzonego tłumaczenia. Edycja gałęzi bota nie pozwala podmienić sprawdzonego tekstu.

## 6. Zakończ lub zwolnij rezerwację

Po scaleniu albo zamknięciu PR opiekun uruchamia:

```text
/work sync
```

Scalony PR kończy zadanie; zamknięty bez scalenia zwalnia rezerwację. Sprawdź potwierdzenie bota, zamiast zakładać, że stan issue zmienił rejestr.

Koordynator synchronizuje też zarejestrowane PR bota po otrzymaniu zdarzenia zamknięcia z GitHuba. Użyj `/work sync`, jeśli automatyczne wykonanie nie dobiegło końca. Dla otwartego PR komenda ponownie zleca kontrole, np. gdy ich uruchomienie nie powiodło się po utworzeniu PR.

Aby anulować przydział, zanim powstanie PR, opiekun dodaje komentarz:

```text
/work release
```

Przed zwolnieniem rezerwacji trzeba zamknąć otwarty PR. Dzięki temu nie powstaną dwie aktywne dostawy tego samego zakresu.

## Lista komend

| Komenda | Kto może użyć | Wynik |
| --- | --- | --- |
| `/work assign` | Opiekun | Utrwala zadanie i rezerwuje klucze. |
| `/work preview` | Przydzielony tłumacz, weryfikator lub opiekun | Sprawdza i zapisuje kopię do weryfikacji. |
| `/work approve <sha256>` | Przydzielony weryfikator | Ponownie sprawdza tę kopię i otwiera PR. |
| `/work release` | Opiekun | Anuluje rezerwację bez otwartego PR. |
| `/work sync` | Opiekun | Uzgadnia PR z rejestrem; dla otwartego PR ponawia kontrole. |

## Gdy zmienia się tekst gry

Nie twórz nowego pliku arkusza dla każdej wersji gry. Stałe identyfikatory źródłowe pozwalają zachować tłumaczenia przy zwykłych aktualizacjach. Nowe wiersze dodawaj przez proces aktualizacji repozytorium, a zmienione tłumaczenia oznaczaj do sprawdzenia, zgodnie z [dokumentacją lokalizacji](../../localization/README.md).

Przydział utrwala kopię **całej tabeli interfejsu lub roli głosowej**. Jeśli ta tabela zmieni się przed zatwierdzeniem, import zatrzyma się, nawet gdy zarezerwowane klucze pozostaną bez zmian. Opiekun zamyka otwarty PR dostawy, zwalnia stare zadanie, aktualizuje wiersze źródłowe w arkuszu i tworzy **nowe issue zadania**. Zachowaj już napisane tłumaczenie i porównaj je z odświeżonym źródłem; potem weryfikator sprawdza nowy podgląd. Zadania innych tabel mogą być kontynuowane.

Wiersz planowania bez prawdziwego identyfikatora źródłowego nie nadaje się jeszcze do importu. Pozostaw go w planowaniu, aż deweloper doda właściwy wpis źródłowy. Nie wymyślaj produkcyjnych identyfikatorów i nie przesyłaj całego arkusza tylko po to, by dodać przyszłe treści.

## Konfiguracja i ograniczenia dla opiekunów

Włącz proces dopiero po scaleniu jego kodu i formularza issue do gałęzi domyślnej. Rejestr znajduje się na `community-work-state`; nie edytuj go ręcznie podczas wykonywania komend.

Proces korzysta z `GITHUB_TOKEN` repozytorium z uprawnieniami do zapisu stanu i gałęzi bota, komentowania issues i tworzenia PR. Nie wymaga połączenia Google OAuth ani osobistego tokena dostępu. Dostęp do Google ogranicza się do odczytu publicznego eksportu CSV.

W ustawieniach Actions repozytorium zezwól GitHub Actions na tworzenie PR. Zachowaj rozdział tożsamości bota i człowieka weryfikującego język.

Nie zakładaj, że PR bota automatycznie uruchomi zwykłe procesy `pull_request`. Importer sprawdza pliki, a następnie jawnie uruchamia `check.yml` dla gałęzi bota oraz `delivery-policy.yml` z zaufanej gałęzi domyślnej dla wskazanego numeru PR.

Chroń gałąź domyślną, wymagając `check` oraz statusu commita `reviewed-sheet`. Proces kontroli musi móc opublikować ten status. Sprawdź oba przed scaleniem: samo dodanie plików automatyzacji nie konfiguruje ochrony gałęzi.

Rejestr zapobiega nakładaniu się przydziałów, a obowiązkowa kontrola dostawy uniemożliwia ich omijanie przez ręczne PR z tłumaczeniami. Żaden z tych mechanizmów nie zarządza dostępem do Arkuszy Google: ogranicz edycję i chroń kolumny źródłowe.

Automatyczne kontrole wykrywają błędy struktury i nieaktualną zawartość. Jakość, kontekst, warunki współpracy i przydatność tekstu w grze nadal wymagają oceny człowieka.
