# Tâches de traduction

Ce guide a été traduit avec l’aide de l’IA. La [version anglaise](../CONTRIBUTION_WORKFLOW.md) fait référence. Les corrections de personnes maîtrisant le français sont les bienvenues ; cette version n’est pas présentée comme relue par une personne de langue maternelle française.

Google Sheets sert à rédiger et à relire les traductions. Une tâche GitHub réserve les lignes, désigne les responsables et détermine quand une copie validée peut devenir une pull request (PR).

**Modifier une feuille ne met à jour ni le dépôt ni le jeu.** Le bot importe une copie exacte du texte relu dans une PR. Un responsable du dépôt examine encore cette PR et la fusionne, puis le développeur intègre le résultat dans une version du jeu.

Ce processus concerne les textes d’interface existants (`ui`) et les traductions écrites des répliques de doublage (`voice-text`). Les enregistrements, auditions, nouvelles répliques et textes sans identifiant source suivent leur propre préparation. La publication de ce guide n’attribue aucune tâche : attendez la confirmation du bot avant de commencer.

Les traductions de la communauté sont livrées par la PR créée par le bot. Une PR de traduction ouverte manuellement ne peut pas contourner la réservation et la validation de la copie relue.

## Les rôles

| Personne | Responsabilité |
| --- | --- |
| Traducteur (`Contributor`) | Rédige le texte attribué dans la feuille et demande un aperçu. |
| Relecteur (`Reviewer`) | Vérifie le contexte, les termes, le naturel du texte et la copie exacte. Approuve son empreinte avec son propre compte GitHub. |
| Responsable du dépôt | Prépare ou vérifie la tâche, réserve les lignes, gère l’accès à la feuille, examine la PR et la fusionne. |

Le traducteur et le relecteur doivent être **deux utilisateurs GitHub différents**. Le bot contrôle l’identité et la structure des fichiers ; la qualité de la traduction reste une affaire de relecture humaine.

Vous pouvez traduire entièrement dans Google Sheets, sans installer Git, cloner le dépôt ni créer votre propre PR. La personne qui approuve l’aperçu a besoin d’un compte GitHub. Si les commentaires GitHub vous posent problème, un responsable peut demander l’aperçu pour vous.

## 1. Définir une petite tâche

Proposez votre aide dans l’issue de candidature à la traduction ou dans un ticket de support Discord. Un responsable convient de la langue, du traducteur, du relecteur et des lignes concernées avant le début du travail.

La feuille privée des candidatures sert uniquement à leur suivi. Elle ne constitue pas le registre des réservations et son contenu ne doit pas être copié dans des issues publiques.

Ouvrez une issue avec le formulaire [Translation work order](https://github.com/Epheria/Ebbtide-Community/issues/new?template=work_order.yml). Conservez ces noms de champs :

| Champ | Contenu |
| --- | --- |
| Kind | `ui` ou `voice-text` |
| Locale | Code de langue du dépôt, par exemple `ja`, `ru` ou `pt-BR` |
| Table or voice role | Nom d’une table ou d’un rôle vocal existant, sans chemin ni extension `.csv` |
| Contributor | Un identifiant GitHub, sans `@` |
| Reviewer | L’identifiant d’un autre utilisateur GitHub, sans `@` |
| Spreadsheet URL | Lien vers le classeur Google Sheets de cette tâche |
| Sheet tab | Nom exact de l’onglet |
| First key | Première clé source existante à inclure |
| Last key | Dernière clé source existante à inclure |

La plage inclut **les deux bornes, dans l’ordre du fichier source du dépôt**. Il ne s’agit ni de l’ordre alphabétique ni de l’ordre actuel des lignes de la feuille. La limite est de **200 clés**. Pour les répliques, la clé est l’identifiant `file` du script, sans `.wav` ni `.flac`.

Une tâche porte sur une seule langue et une seule table d’interface ou un seul rôle vocal. Une petite plage est plus facile à relire et crée moins de conflits quand le texte du jeu change.

## 2. Réserver avant de traduire

Un responsable ajoute ce commentaire dans l’issue :

```text
/work assign
```

Attendez la confirmation de réservation du bot. Remplir ou fermer une issue, ou inscrire un nom dans une feuille, ne réserve ni ne libère le travail.

Le bot enregistre l’attribution dans `registry.json`, sur la branche `community-work-state`. Il fige les champs de l’issue, les clés précises et l’empreinte de la source. Il refuse tout chevauchement avec une tâche active du même type, de la même langue et de la même table ou du même rôle. Des langues différentes peuvent travailler sur les mêmes clés.

Modifier ensuite le corps de l’issue ne change pas l’attribution. Si la plage, le classeur, le traducteur ou le relecteur doit changer, demandez à un responsable de libérer la tâche et de créer une nouvelle réservation corrigée.

## 3. Rédiger dans la feuille

Un responsable fournit les lignes source actuelles et accorde le droit de modification aux personnes désignées. Le bot doit pouvoir lire le classeur sans connexion Google, mais seules les personnes qui y travaillent doivent pouvoir le modifier.

Protégez les clés et le texte anglais. N’accordez l’accès qu’aux cellules nécessaires. N’activez pas « Tous les utilisateurs disposant du lien peuvent modifier ». Les autorisations et plages protégées se configurent manuellement ; le bot GitHub ne gère pas les droits Google.

Pour l’interface, gardez ces quatre colonnes CSV :

```text
key,en,translation,status
```

L’onglet doit contenir les lignes de **la seule table** indiquée dans la tâche. Une liste générale regroupant plusieurs tables sert de référence, mais ne s’importe pas directement comme onglet de travail. Le bot compare toutes les lignes remplies de l’onglet à cette table source.

Modifiez `translation` et utilisez les valeurs existantes de `status`. Une ligne d’interface n’est importable que si `status` est **vide**. Les valeurs `review` et `outdated` la bloquent. Un état vide ne vaut pas approbation : la relecture indépendante reste nécessaire.

Pour les traductions écrites de répliques, conservez exactement ces en-têtes et cet ordre :

```text
Take file,English source,Translation,Review status,Notes,Role,Situation,Tone,Current voices,Source readiness,Source file,Source record
```

Les onglets japonais, russe et coréen existants utilisent ce format. Le bot filtre selon la valeur exacte de `Role`, comme `carrier_jet_pilot`, puis sélectionne les clés `Take file` réservées. Remplissez `Translation` et indiquez `Approved` dans `Review status` pour les lignes relues.

Le texte approuvé est enregistré dans `voice/translations/<locale>/<role>.csv`, avec les colonnes `key,en,translation,status`. Seul le **texte écrit** est importé. Cela ne valide pas un enregistrement et ne prouve pas qu’une réplique provisoire existe déjà dans le jeu.

Dans les deux cas :

- Conservez les variables, balises requises et codes de saut de ligne.
- Gardez les clés et l’anglais strictement identiques à la source attribuée.
- Complétez toutes les traductions de la plage avant de demander un aperçu.
- Traitez les cellules comme du texte. N’utilisez pas de formules pour récupérer ou produire une traduction.
- N’incluez ni coordonnées privées, ni messages de tickets, ni auditions dans le classeur ou l’issue publique.

Si une tâche est trop grande pour être terminée, convenez de sa division ou de sa libération avec un responsable, plutôt que de garder indéfiniment une réservation partielle.

## 4. Demander et relire un aperçu

Le traducteur désigné, le relecteur désigné ou un responsable commente :

```text
/work preview
```

Le bot lit la plage réservée par l’export CSV public de Google Sheets. Il contrôle la source figée, les états, les traductions non vides et les variables requises. Il vérifie aussi la traduction actuelle du dépôt pour détecter les changements d’une autre personne avant l’approbation.

Le bot conserve une copie immuable et publie son empreinte SHA-256 avec un lien de relecture. Relisez **cette copie**, pas seulement le résumé de l’issue ou la feuille en direct. La feuille peut changer après la création de l’aperçu.

Le relecteur vérifie :

- Le sens et le contexte par rapport à l’anglais.
- Le naturel du texte et la cohérence avec le glossaire.
- La longueur à l’écran ou la manière de prononcer la réplique, selon le cas.
- La place des variables, les balises et les sauts de ligne.

Si une correction est nécessaire, modifiez la feuille et relancez `/work preview`. Utilisez la nouvelle empreinte. Un lien d’aperçu permet de relire ; il n’autorise pas la fusion.

## 5. Approuver la copie exacte

**Seul le relecteur désigné** commente, en remplaçant `<sha256>` par l’empreinte complète de l’aperçu :

Publiez les commandes dans les commentaires de l’issue GitHub attribuée à cette tâche. Pour approuver, copiez les 64 caractères après `Digest:` dans la réponse du bot à la demande d’aperçu et remplacez uniquement `<sha256>` dans l’exemple ; gardez la commande en anglais et n’envoyez pas ce marqueur tel quel.

```text
/work approve <sha256>
```

Le bot vérifie l’identité du relecteur, relit la feuille et exige qu’elle corresponde à la copie approuvée. Il contrôle également que la source et le fichier de destination du dépôt n’ont pas changé. Une modification de la feuille ou de la destination demande un nouvel aperçu. Une modification de la table source demande une nouvelle attribution, comme expliqué plus bas.

Si tout est correct, le bot ouvre une PR avec les fichiers validés. **Il ne la fusionne pas.** La valeur `Approved` dans la feuille ou un commentaire tel que « c’est bon » ne remplace pas cette commande.

Un responsable examine les changements et fusionne la PR après la réussite des contrôles. La réservation reste active jusque-là. Les échanges concernant les fichiers proposés se déroulent dans cette PR.

La politique de confiance `reviewed-sheet` compare la PR à sa réservation et à sa copie approuvée. Elle lit les fichiers de la PR comme des données et exécute le code de confiance de la branche par défaut. Elle refuse les PR de traduction manuelles, les livraisons modifiées et les fichiers supplémentaires ajoutés à une traduction approuvée. Modifier une branche du bot ne permet pas de remplacer le texte relu.

## 6. Terminer ou libérer la réservation

Après la fusion ou la fermeture de la PR, un responsable exécute :

```text
/work sync
```

Une PR fusionnée termine la tâche ; une PR fermée sans fusion libère la réservation. Vérifiez la confirmation du bot au lieu de supposer que l’état de l’issue a modifié le registre.

Le coordinateur synchronise aussi les PR enregistrées du bot quand GitHub signale leur fermeture. Utilisez `/work sync` si cette exécution automatique n’a pas abouti. Pour une PR ouverte, cette commande redemande également les contrôles, notamment si leur lancement a échoué après la création de la PR.

Pour annuler une attribution avant qu’une PR existe, un responsable commente :

```text
/work release
```

Une PR ouverte doit être fermée avant de libérer la réservation. Cela évite deux livraisons actives pour la même plage.

## Tableau des commandes

| Commande | Qui peut l’utiliser | Résultat |
| --- | --- | --- |
| `/work assign` | Responsable | Fige la tâche et réserve les clés. |
| `/work preview` | Traducteur désigné, relecteur désigné ou responsable | Valide et conserve une copie à relire. |
| `/work approve <sha256>` | Relecteur désigné | Revérifie cette copie et ouvre une PR. |
| `/work release` | Responsable | Annule une réservation sans PR ouverte. |
| `/work sync` | Responsable | Synchronise le registre avec la PR ; si elle est ouverte, redemande ses contrôles. |

## Quand le texte du jeu change

Ne créez pas un nouveau classeur pour chaque version du jeu. Les identifiants source stables permettent de conserver les traductions lors des mises à jour. Ajoutez les lignes par le processus de mise à jour du dépôt et marquez les traductions touchées pour relecture, comme indiqué dans [Localisation](../../localization/README.md).

L’attribution fige une copie de **toute la table d’interface ou de tout le rôle vocal**. Si cette source change avant l’approbation, l’import s’arrête, même si les clés réservées sont inchangées. Un responsable ferme toute PR de livraison ouverte, libère l’ancienne tâche, actualise les lignes source de la feuille et ouvre **une nouvelle issue de travail**. Conservez la traduction déjà rédigée et comparez-la à la nouvelle source ; le relecteur examine ensuite un nouvel aperçu. Les tâches portant sur d’autres tables peuvent continuer.

Une ligne de préparation sans véritable identifiant source ne peut pas être importée. Gardez-la en préparation jusqu’à l’ajout de l’entrée source par le développeur. N’inventez pas d’identifiants de production et n’importez pas un classeur entier pour inclure du contenu futur.

## Configuration et limites pour les responsables

Activez ce processus seulement après la fusion de son code et du formulaire dans la branche par défaut. Le registre se trouve sur `community-work-state` ; ne le modifiez pas manuellement pendant l’exécution de commandes.

Le processus utilise le `GITHUB_TOKEN` du dépôt, avec les autorisations pour écrire l’état et la branche du bot, commenter les issues et créer des PR. Il ne demande ni connexion Google OAuth ni jeton d’accès personnel. L’accès à Google se limite à la lecture de l’export CSV public.

Dans les paramètres Actions du dépôt, autorisez GitHub Actions à créer des PR. L’identité du bot reste distincte de celle de la personne qui relit la langue.

Ne comptez pas sur une PR du bot pour déclencher automatiquement les processus `pull_request`. L’importateur valide les fichiers et lance explicitement `check.yml` sur la branche du bot et `delivery-policy.yml` depuis la branche par défaut de confiance pour le numéro de PR concerné.

Protégez la branche par défaut en exigeant `check` et le statut de commit `reviewed-sheet`. Le processus de politique doit pouvoir publier ce statut. Vérifiez les deux avant la fusion : ajouter les fichiers d’automatisation ne configure pas à lui seul la protection des branches.

Le registre empêche les attributions qui se chevauchent, et la politique obligatoire empêche de les contourner avec des PR manuelles. Aucun des deux ne gère les autorisations Google Sheets : limitez la modification et protégez les colonnes source.

Les contrôles automatiques détectent les problèmes de structure et les contenus périmés. La qualité, le contexte, les conditions de contribution et l’adéquation au jeu restent soumis à une relecture humaine.
