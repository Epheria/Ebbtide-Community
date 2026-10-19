# Doublage

> **Traduction écrite des répliques :** Consultez le [guide des tâches en français](CONTRIBUTION_WORKFLOW.md). Il faut des lignes attribuées et un relecteur différent du traducteur ; le texte est rédigé dans la feuille attribuée et le bot crée la PR. Ce processus importe du texte, pas des enregistrements. Les instructions d’audition, de fichiers audio et de format ci-dessous restent celles du doublage.

*Cette page a été traduite avec l'aide de l'IA. Si le français est votre langue maternelle, aidez-nous à l'améliorer avec une pull request. La [version anglaise](../../voice/README.md) fait référence.*

Pour l'instant, toutes les répliques d'Ebbtide sont doublées par IA. Elles seront toutes remplacées par de vrais comédiens de doublage : pilotes, équipages d'hélicoptère, officiers de marine, équipages de véhicules et escouades d'infanterie.

Les chemins ci-dessous partent du dossier [`voice/`](../../voice/).

## Comment ça marche

1. **Audition.** Postez une courte prise dans le salon des soumissions du Discord, en lisant les répliques d'exemple épinglées là-bas.
2. **Casting.** Si votre voix colle à un rôle, un mainteneur vous contacte et ouvre un ticket privé.
3. **Script.** Le script complet de votre rôle est ajouté dans `scripts/<role>.csv` : nom de fichier, situation, ton et réplique.
4. **Livraison.** Déposez les prises dans votre dossier Drive privé et cochez `Ready to submit` dans votre feuille de travail. Un fichier par réplique, avec le nom exact du script. Suivez le [guide des enregistrements (en anglais)](../VOICE_SUBMISSIONS.md). N’ajoutez pas d’audio dans une PR publique.
5. **Validation.** On écoute, on demande de nouvelles prises si besoin, on fusionne, puis on intègre les répliques dans la prochaine build.

## Consignes d'enregistrement

Enregistrez une voix propre et sèche, sans traitement. Le jeu ajoute lui-même les effets radio.

- FLAC de préférence (plus léger), sinon WAV. Mono, 48 kHz, 24 bits (44,1 kHz / 16 bits, ça passe aussi).
- Pas de réverb, d'effets, de musique ni de filtre radio.
- Une pièce calme, sans écho ni bruit de fond.
- Les crêtes les plus fortes autour de -3 dB, sans jamais saturer.
- Une réplique par fichier, avec environ une demi-seconde de silence avant et après.

## Avant d'envoyer quoi que ce soit

Lisez [CONTRIBUTOR_TERMS.md](../../CONTRIBUTOR_TERMS.md) (en anglais ; c'est le texte anglais qui fait foi), surtout la partie sur les enregistrements vocaux. Si vous avez moins de 18 ans, un parent ou un tuteur légal doit donner son accord avec vous.
