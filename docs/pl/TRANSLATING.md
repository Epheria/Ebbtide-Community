# Lokalizacja

> **Przesyłanie tłumaczeń:** Aktualny proces opisuje [polski przewodnik po zadaniach](CONTRIBUTION_WORKFLOW.md). Opiekun rezerwuje zakres, piszesz w przydzielonym arkuszu, a inna osoba sprawdza tekst, zanim bot utworzy PR. Poniższe kroki edycji i ręcznego przesyłania służą jako opis formatów i prac utrzymaniowych; nie zastępują rezerwacji ani zatwierdzenia.

*Ta strona została przetłumaczona z pomocą AI. Jeśli polski to twój język ojczysty, pomóż ją poprawić przez pull request. Punktem odniesienia jest [wersja angielska](../../localization/README.md).*

Tekst interfejsu Ebbtide, gotowy do tłumaczenia. Gra jest pisana po koreańsku, a angielski jest źródłem dla wszystkich pozostałych języków. Wszystkie ścieżki poniżej są w folderze [`localization/`](../../localization/).

## Foldery

| Ścieżka | Co zawiera |
| --- | --- |
| `source/strings/<Table>.csv` | Aktualny tekst gry: `key`, `en`, `ko`. Nie edytuj; ten plik jest generowany na nowo z gry. |
| `source/SNAPSHOT` | Data i rozmiar aktualnej migawki źródła |
| `translations/<lang>/<Table>.csv` | Jeden folder na język: `key`, `en`, `translation`, `status` |
| `glossary.csv` | Nazwy i terminy wojskowe oraz wskazówki, jak je tłumaczyć |

Foldery języków mają kody takie jak `de`, `fr`, `pt-BR`, `ro`, `zh-Hans`. Polski to `pl`.

## Jak tłumaczyć

1. Otwórz [issue dla tłumaczy](https://github.com/Epheria/Ebbtide-Community/issues/new?template=translator.yml) dla swojego języka. Opiekun projektu utworzy folder języka.
2. Edytuj pliki w `translations/<lang>/`. Wypełniaj tylko kolumnę `translation`.
3. Zachowaj każdy placeholder dokładnie tak jak w angielskim: `{0}`, `{1}`, tagi formatowania (rich text), np. `<b>`, oraz łamania wiersza `\n`. Możesz je przesuwać w obrębie zdania.
4. Nazwy i terminy sprawdzaj w `glossary.csv`.
5. Otwórz pull request. Automatyczne sprawdzenie zgłosi brakujące placeholdery albo uszkodzone wiersze.

Jeśli nie masz pewności, zostaw `translation` w danym wierszu puste. Pusty wiersz w grze pokaże tekst angielski.

### Edycja plików CSV

- Do małych zmian wystarczy edytor w przeglądarce na GitHubie.
- Przy większej pracy użyj LibreOffice Calc albo Arkuszy Google. Importuj jako UTF-8 z przecinkiem jako separatorem, a potem eksportuj z powrotem do CSV w UTF-8, z tymi samymi czterema kolumnami.
- Unikaj Microsoft Excel, chyba że zapisujesz jako „CSV UTF-8”. Inne formaty psują znaki spoza alfabetu angielskiego, w tym polskie litery (ą, ę, ł).

## Kolumna `status`

| Wartość | Znaczenie | Co zrobić |
| --- | --- | --- |
| (puste) | Wszystko w porządku albo jeszcze nie przetłumaczono | Przetłumacz, jeśli tłumaczenie jest puste |
| `outdated` | Angielski tekst zmienił się po przetłumaczeniu | Popraw tłumaczenie, potem wyczyść status |
| `review` | Recenzent chce jeszcze raz na to spojrzeć | Omów to w pull requeście |

## Gdy tekst gry się zmienia

Gra wciąż powstaje, więc angielski tekst często jest dodawany, zmieniany i usuwany. Gdy źródło się zmieni, opiekun projektu uruchamia `python tools/l10n.py update`. To polecenie:

- dodaje nowe wiersze z pustym tłumaczeniem,
- oznacza wiersze, w których zmienił się angielski tekst, jako `outdated` i zachowuje twoje stare tłumaczenie,
- usuwa wiersze, których nie ma już w grze.

## Dla opiekunów projektu

```bash
python tools/export_unity_strings.py --project <path to the Unity project>  # refresh the source (needs PyYAML)
python tools/l10n.py update                                                 # sync every language
python tools/l10n.py init <lang>                                            # open a new language
python tools/l10n.py check                                                  # the same check the pull requests run
python tools/l10n.py status                                                 # progress per language
```

Sceny fabularne (dialogi z przerywników filmowych) nie są jeszcze dodane. Pojawią się, gdy scenariusz będzie ostateczny.
