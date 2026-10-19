# Głosy

*Ta strona została przetłumaczona z pomocą AI. Jeśli polski to twój język ojczysty, pomóż ją poprawić przez pull request. Punktem odniesienia jest [wersja angielska](../../voice/README.md).*

Obecnie wszystkie kwestie głosowe w Ebbtide mają głosy AI. Każdą z nich mają zastąpić prawdziwi aktorzy głosowi: piloci, załogi śmigłowców, oficerowie okrętowi, załogi pojazdów i drużyny piechoty. Ścieżki poniżej są w folderze [`voice/`](../../voice/).

## Jak to działa

1. **Przesłuchanie.** Wrzuć krótkie nagranie na kanał zgłoszeń na Discordzie. Przeczytaj w nim przykładowe kwestie przypięte na tym kanale.
2. **Obsada.** Jeśli twój głos pasuje do roli, opiekun projektu skontaktuje się z tobą i otworzy prywatny ticket.
3. **Skrypt.** Pełny skrypt twojej roli trafia do [`scripts/<role>.csv`](../../voice/scripts/): nazwa pliku, sytuacja, ton i kwestia.
4. **Wysyłka.** Otwórz pull request, który dodaje twoje nagrania (take'i) do `takes/<role>/<your name>/`. Jeden plik na kwestię, nazwany dokładnie tak jak w skrypcie.
5. **Sprawdzenie.** Odsłuchujemy, w razie potrzeby prosimy o ponowne nagranie, scalamy i dodajemy kwestie do następnego buildu.

## Wymagania nagrań

Nagrywaj czysto i „na sucho”. Gra sama dodaje efekty radiowe.

- Najlepiej FLAC (mniejsze pliki), ewentualnie WAV. Mono, 48 kHz, 24 bity (44,1 kHz / 16 bitów też jest w porządku).
- Bez pogłosu, efektów, muzyki i filtra radiowego.
- Ciche pomieszczenie, bez echa i hałasu w tle.
- Najgłośniejsze szczyty w okolicy -3 dB, nigdy z przesterem (clippingiem).
- Jedna kwestia na plik, z mniej więcej pół sekundy ciszy przed i po.

## Zanim cokolwiek wyślesz

Przeczytaj [CONTRIBUTOR_TERMS.md](../../CONTRIBUTOR_TERMS.md) (dokument jest tylko po angielsku; oficjalną wersją jest tekst angielski), zwłaszcza część o nagraniach głosu. Jeśli masz mniej niż 18 lat, zgodę razem z tobą musi wyrazić rodzic lub opiekun prawny.
