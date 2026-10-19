# Contribuer

> **Traduction de l’interface et des répliques :** Suivez le [guide des tâches en français](CONTRIBUTION_WORKFLOW.md). Un responsable réserve les lignes et désigne un relecteur différent du traducteur. Rédigez dans la feuille attribuée ; le bot crée la PR après la relecture. Les étapes d’envoi manuel ci-dessous concernent les autres contributions ; les règles de format restent applicables.

*Cette page a été traduite avec l'aide de l'IA. Si le français est votre langue maternelle, aidez-nous à l'améliorer avec une pull request. La [version anglaise](../../CONTRIBUTING.md) fait référence.*

Merci de votre aide. Cette page explique les étapes concrètes. La partie juridique se trouve dans [CONTRIBUTOR_TERMS.md](../../CONTRIBUTOR_TERMS.md) (en anglais ; c'est le texte anglais qui fait foi).

## Avant de commencer

1. Ouvrez une issue pour ce que vous voulez faire ([traducteur](https://github.com/Epheria/Ebbtide-Community/issues/new?template=translator.yml), [comédien de doublage](https://github.com/Epheria/Ebbtide-Community/issues/new?template=voice_actor.yml)), pour éviter que deux personnes travaillent sur la même chose.
2. Attendez la réponse d'un mainteneur. Pour une nouvelle langue, c'est le mainteneur qui crée le dossier pour vous.

## Faire des modifications

Pas besoin de bien connaître Git. Deux options :

- **Dans le navigateur :** ouvrez un fichier sur GitHub, cliquez sur l'icône en forme de crayon, faites vos modifications, puis choisissez « Create a new branch and start a pull request ».
- **Sur votre ordinateur :** forkez le dépôt, clonez-le, faites vos modifications, poussez-les sur votre fork et ouvrez une pull request.

Limitez chaque pull request à une seule langue ou un seul rôle de doublage. Elle sera plus facile à relire.

## Checklist de la pull request

- [ ] Ce travail est le mien, et rien n'est généré par IA.
- [ ] J'accepte [CONTRIBUTOR_TERMS.md](../../CONTRIBUTOR_TERMS.md) (en anglais ; c'est le texte anglais qui fait foi).
- [ ] Traductions : j'ai seulement modifié les colonnes `translation` et `status`.
- [ ] Doublage : les noms de fichiers correspondent exactement au script du rôle.

## Relecture

- Les traductions sont relues par un locuteur natif de la langue, quand il y en a un de disponible. Le premier traducteur expérimenté d'une langue en devient généralement le relecteur.
- Un relecteur peut demander des modifications. Les discussions restent dans la pull request, pour que tout le monde puisse les suivre.
- Le travail fusionné arrive dans le jeu à la prochaine build, pas immédiatement.

## Crédits

Dites-nous dans votre première pull request comment vous voulez être crédité (nom ou pseudo, et un lien si vous le souhaitez). Vous pourrez le changer plus tard avec une autre pull request sur [CREDITS.md](../../CREDITS.md).
