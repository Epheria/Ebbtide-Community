# Localization

Ebbtide's interface text, ready to translate. The game is written in Korean, and English is the source for every other language.

## Folders

| Path | What it holds |
| --- | --- |
| `source/strings/<Table>.csv` | Current game text: `key`, `en`, `ko`. Do not edit; it is regenerated from the game. |
| `source/SNAPSHOT` | Date and size of the current source snapshot |
| `translations/<lang>/<Table>.csv` | One folder per language: `key`, `en`, `translation`, `status` |
| `glossary.csv` | Names and military terms, and how to handle them |

Language folders use codes like `de`, `fr`, `pt-BR`, `ro`, `zh-Hans`.

## How to translate

1. Open a [translator issue](../../../issues/new?template=translator.yml) for your language. A maintainer creates the language folder.
2. Edit the files in `translations/<lang>/`. Fill only the `translation` column.
3. Keep every placeholder exactly as in English: `{0}`, `{1}`, rich-text tags such as `<b>`, and `\n` line breaks. You may move them within the sentence.
4. Check `glossary.csv` for names and terms.
5. Open a pull request. An automatic check reports missing placeholders or broken rows.

Leave a row's `translation` empty if you are unsure; an empty row falls back to English in the game.

### Editing CSV files

- GitHub's web editor works for small changes.
- For larger work, use LibreOffice Calc or Google Sheets. Import as UTF-8 with comma separators, and export back to CSV in UTF-8 with the same four columns.
- Avoid Microsoft Excel unless you save as "CSV UTF-8"; other formats break non-English characters.

## The `status` column

| Value | Meaning | What to do |
| --- | --- | --- |
| (empty) | Fine, or not translated yet | Translate it if it is empty |
| `outdated` | The English text changed after it was translated | Update the translation, then clear the status |
| `review` | A reviewer wants another look | Discuss in the pull request |

## When the game text changes

The game is still in development, so English text is added, changed and removed often. When the source updates, a maintainer runs `python tools/l10n.py update`, which:

- adds new rows with an empty translation,
- marks rows whose English changed as `outdated`, keeping your old translation,
- removes rows that no longer exist in the game.

## For maintainers

```bash
python tools/export_unity_strings.py --project <path to the Unity project>  # refresh the source (needs PyYAML)
python tools/l10n.py update                                                 # sync every language
python tools/l10n.py init <lang>                                            # open a new language
python tools/l10n.py check                                                  # the same check the pull requests run
python tools/l10n.py status                                                 # progress per language
```

Story scenes (cutscene dialogue) are not included yet. They will be added once the script is final.
