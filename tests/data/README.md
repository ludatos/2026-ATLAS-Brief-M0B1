# Images de demonstration Vision CLIP

Ces images servent aux essais manuels et aux essais reels du modele, pas aux tests
automatises par defaut. Ceux-ci generent leurs propres images en memoire et simulent CLIP.
Ne pas ajouter de pieces personnelles dans ce dossier.

## Carte d'identite francaise : specimen

- Fichier local attendu : `specimen_identity_fr.png`.
- Source : [fiche Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Carte_identit%C3%A9_%C3%A9lectronique_fran%C3%A7aise_(2021,_recto).png).
- Auteur indique : Ministere de l'Interieur.
- Attribution de l'image indiquee sur la fiche : © European Union, 1998 - 2026.
- La fiche indique une reutilisation avec attribution pour l'image, le domaine public
  pour le document dans son ensemble et un statut distinct pour la photo d'identite.
  Consulter ces conditions detaillees avant toute redistribution.
- Image originale sans modification : 4626 x 2946 pixels, environ 3,92 Mo.
- Recherche proposee pendant la formation : [specimens Wikimedia](https://commons.wikimedia.org/w/index.php?search=Specimens_of_identity_documents&title=Special%3AMediaSearch&type=image).

## Recuperer le specimen depuis la racine du projet

```powershell
curl.exe --fail --location --output tests/data/specimen_identity_fr.png "https://upload.wikimedia.org/wikipedia/commons/4/49/Carte_identit%C3%A9_%C3%A9lectronique_fran%C3%A7aise_%282021%2C_recto%29.png"
```

## Envoyer une image au backend local

```powershell
curl.exe --fail-with-body "http://localhost:8000/vision/classify-document" -F "file=@tests/data/specimen_identity_fr.png" -F "labels=identity card" -F "labels=bank statement" -F "labels=bank check" -F "labels=blank paper"
```

Le resultat n'est ni une preuve d'authenticite ni une validation administrative.