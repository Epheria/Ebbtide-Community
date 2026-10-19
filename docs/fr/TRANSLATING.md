# Localisation

*Cette page a été traduite avec l'aide de l'IA. Si le français est votre langue maternelle, aidez-nous à l'améliorer avec une pull request. La [version anglaise](../../localization/README.md) fait référence.*

Les textes de l'interface d'Ebbtide, prêts à être traduits. Le jeu est écrit en coréen, et l'anglais sert de source pour toutes les autres langues.

Les chemins ci-dessous partent du dossier [`localization/`](../../localization/).

## Dossiers

| Chemin | Contenu |
| --- | --- |
| `source/strings/<Table>.csv` | Le texte actuel du jeu : `key`, `en`, `ko`. Ne pas modifier : il est régénéré à partir du jeu. |
| `source/SNAPSHOT` | Date et taille de l'instantané source actuel |
| `translations/<lang>/<Table>.csv` | Un dossier par langue : `key`, `en`, `translation`, `status` |
| `glossary.csv` | Les noms et les termes militaires, et comment les traiter |

Les dossiers de langue utilisent des codes comme `de`, `fr`, `pt-BR`, `ro`, `zh-Hans`.

## Comment traduire

1. Ouvrez une [issue traducteur](https://github.com/Epheria/Ebbtide-Community/issues/new?template=translator.yml) pour votre langue. Un mainteneur crée le dossier de la langue.
2. Modifiez les fichiers dans `translations/<lang>/` (pour le français : `translations/fr/`). Remplissez uniquement la colonne `translation`.
3. Gardez chaque variable exactement comme en anglais : `{0}`, `{1}`, les balises de texte enrichi comme `<b>`, et les retours à la ligne `\n`. Vous pouvez les déplacer dans la phrase.
4. Consultez `glossary.csv` pour les noms et les termes.
5. Ouvrez une pull request. Une vérification automatique signale les variables manquantes et les lignes cassées.

En cas de doute, laissez la `translation` de la ligne vide. Dans le jeu, une ligne vide s'affiche en anglais.

### Modifier les fichiers CSV

- L'éditeur web de GitHub suffit pour les petites modifications.
- Pour un plus gros travail, utilisez LibreOffice Calc ou Google Sheets. Importez en UTF-8 avec la virgule comme séparateur, puis réexportez en CSV UTF-8 avec les quatre mêmes colonnes.
- Évitez Microsoft Excel, sauf si vous enregistrez au format « CSV UTF-8 ». Les autres formats cassent les caractères non anglais, accents compris. (Attention : Excel en français peut aussi remplacer les virgules par des points-virgules. Le fichier doit garder des virgules.)

## La colonne `status`

| Valeur | Signification | Que faire |
| --- | --- | --- |
| (vide) | Tout va bien, ou pas encore traduit | Traduisez la ligne si elle est vide |
| `outdated` | Le texte anglais a changé après la traduction | Mettez la traduction à jour, puis videz le statut |
| `review` | Un relecteur veut y jeter un autre coup d'œil | Discutez-en dans la pull request |

## Quand le texte du jeu change

Le jeu est encore en développement : du texte anglais est souvent ajouté, modifié ou supprimé. Quand la source est mise à jour, un mainteneur lance `python tools/l10n.py update`, qui :

- ajoute les nouvelles lignes avec une traduction vide,
- marque comme `outdated` les lignes dont l'anglais a changé, en gardant votre ancienne traduction,
- supprime les lignes qui n'existent plus dans le jeu.

## Pour les mainteneurs

```bash
python tools/export_unity_strings.py --project <path to the Unity project>  # refresh the source (needs PyYAML)
python tools/l10n.py update                                                 # sync every language
python tools/l10n.py init <lang>                                            # open a new language
python tools/l10n.py check                                                  # the same check the pull requests run
python tools/l10n.py status                                                 # progress per language
```

Les scènes narratives (dialogues des cinématiques) ne sont pas encore incluses. Elles seront ajoutées une fois le script finalisé.
