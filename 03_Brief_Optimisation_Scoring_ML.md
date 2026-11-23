# **Optimisation du Scoring de Crédit IA-TOS**

## Compétition par Équipes, Feature Engineering, Pipelines Étanches & Tuning Optuna (Module 1\)

[Cadre du Brief Simplon : Optimisation du Scoring de Risque IA-TOS	2](#cadre-du-brief-simplon-:-optimisation-du-scoring-de-risque-ia-tos)

[Contexte Métier & Enjeu Industriel	2](#contexte-métier-&-enjeu-industriel)

[Compétences du Référentiel Officiel Atlas Visées	2](#compétences-du-référentiel-officiel-atlas-visées)

[Modalités Pédagogiques & Calendrier	2](#modalités-pédagogiques-&-calendrier)

[Section 2 : Le Jeu de Données et les Deux Défis Métiers	3](#section-2-:-le-jeu-de-données-et-les-deux-défis-métiers)

[Défi A : Régression sur le Score de Crédit (score\_credit)	3](#défi-a-:-régression-sur-le-score-de-crédit-\(score_credit\))

[Défi B : Classification sur la Décision d'Octroi (decision\_octroi)	3](#défi-b-:-classification-sur-la-décision-d'octroi-\(decision_octroi\))

[Section 3 : Démarche Méthodologique Pas à Pas	4](#section-3-:-démarche-méthodologique-pas-à-pas)

[Étape 1 : Exploration des Données et Diagnostic Qualité	4](#étape-1-:-exploration-des-données-et-diagnostic-qualité)

[Étape 2 : Feature Engineering Raisonné	4](#étape-2-:-feature-engineering-raisonné)

[Étape 3 : Construction du Pipeline Scikit-Learn Étanche	4](#étape-3-:-construction-du-pipeline-scikit-learn-étanche)

[Étape 4 : Validation Croisée K-Fold Stratifiée	4](#étape-4-:-validation-croisée-k-fold-stratifiée)

[Étape 5 : Optimisation Bayésienne avec Optuna	5](#étape-5-:-optimisation-bayésienne-avec-optuna)

[Section 4 : Livrables Attendus et Critères d'Évaluation	6](#section-4-:-livrables-attendus-et-critères-d'évaluation)

[Livrables Techniques Obligatoires	6](#livrables-techniques-obligatoires)

[Grille d'Évaluation & Classement de la Compétition	6](#grille-d'évaluation-&-classement-de-la-compétition)

# 

# **Cadre du Brief Simplon : Optimisation du Scoring de Risque IA-TOS** {#cadre-du-brief-simplon-:-optimisation-du-scoring-de-risque-ia-tos}

## **Contexte Métier & Enjeu Industriel** {#contexte-métier-&-enjeu-industriel}

Au cours du Module 0, vous avez déployé le socle applicatif complet d'IA-TOS Intellicenter (microservice FastAPI, interface multi-pages Streamlit, conteneurisation Docker et orchestration d'agents LangGraph). Cependant, le moteur algorithmique de prédiction actuel repose sur des modèles de base non optimisés. Dans un contexte bancaire réel soumis à l'EU AI Act et aux exigences de rentabilité financière, la direction des risques d'IA-TOS exige une refonte rigoureuse des modèles de scoring de crédit.

Ce Brief 3 prend la forme d'une compétition technique amicale par équipes de 2 ou 3 apprenants : votre mission consiste à maximiser la qualité des prédictions à la fois en régression (estimation du score de solvabilité) et en classification (décision d'octroi de prêt), tout en respectant une étanchéité absolue anti-fuite de données (Data Leakage) et en justifiant vos arbitrages par des métriques d'évaluation certifiées.

## **Compétences du Référentiel Officiel Atlas Visées** {#compétences-du-référentiel-officiel-atlas-visées}

* C5 (Niveau 1\) : Entraîner et optimiser un modèle de Machine Learning supervisé en sélectionnant les algorithmes appropriés, en construisant un pipeline de prétraitement robuste et en ajustant méthodiquement les hyperparamètres (Optuna).  
* C8 (Niveau 1\) : Mesurer la performance d'un système d'intelligence artificielle en sélectionnant des métriques adaptées aux contraintes métiers (R², MAE, RMSE pour la régression ; Matrice de confusion, Rappel, F1-Score et ROC-AUC pour la classification) et analyser les compromis statistiques et éthiques.

## **Modalités Pédagogiques & Calendrier** {#modalités-pédagogiques-&-calendrier}

* Format de travail : Équipes de 2 ou 3 apprenants (simulation d'une compétition de Data Science Kaggle-like en entreprise).  
* Durée estimée : 4 heures en autonomie accompagnée.  
* Environnement technique : Python 3.12, Scikit-Learn, Optuna, Pandas, Pytest, UV.

# **Section 2 : Le Jeu de Données et les Deux Défis Métiers** {#section-2-:-le-jeu-de-données-et-les-deux-défis-métiers}

Le fichier de données fourni dans votre starter-kit est credit\_risk\_dataset.csv (1 200 dossiers clients historiques, 17 variables). Il réunit à la fois des informations financières (revenu, épargne, montant demandé, mensualités), des caractéristiques contractuelles (type de contrat, logement, historique d'incidents) et des attributs socio-démographiques.

## **Défi A : Régression sur le Score de Crédit (score\_credit)** {#défi-a-:-régression-sur-le-score-de-crédit-(score_credit)}

La variable continue score\_credit (comprise entre 300 et 850 points) représente la note de solvabilité financière globale de l'emprunteur. Votre objectif est d'entraîner un régresseur capable d'estimer cette note avec la plus faible erreur possible.

* Métrique principale de classement : R² (Coefficient de détermination) sur le jeu de test.  
* Métrique métier complémentaire : MAE (Mean Absolute Error, erreur moyenne en points de score).

## **Défi B : Classification sur la Décision d'Octroi (decision\_octroi)** {#défi-b-:-classification-sur-la-décision-d'octroi-(decision_octroi)}

La variable binaire decision\_octroi (0 \= Refus du prêt, 1 \= Accord du prêt) traduit la décision finale du comité des risques. Votre objectif est d'entraîner un classifieur capable d'ordonner efficacement les risques et d'isoler les dossiers litigieux.

* Métrique principale de classement : ROC-AUC (Area Under the ROC Curve).  
* Métrique d'arbitrage opérationnel : F1-Score et Rappel (Recall) sur la classe minoritaire des dossiers refusés.

# 

# **Section 3 : Démarche Méthodologique Pas à Pas** {#section-3-:-démarche-méthodologique-pas-à-pas}

## **Étape 1 : Exploration des Données et Diagnostic Qualité** {#étape-1-:-exploration-des-données-et-diagnostic-qualité}

À l'aide de Pandas, inspectez les types de variables, quantifiez les valeurs manquantes et analysez la distribution de la cible decision\_octroi pour identifier l'éventuel déséquilibre de classes. Veillez à ne jamais supprimer arbitrairement des lignes sans justification documentée.

## **Étape 2 : Feature Engineering Raisonné** {#étape-2-:-feature-engineering-raisonné}

Les modèles linéaires et arborescents gagnent considérablement en précision lorsque l'on explicite des ratios financiers clés. Vous êtes invités à concevoir au moins deux variables dérivées métiers, par exemple :

* Ratio Reste à Vivre : Revenu mensuel diminué de la charge de crédit estimée.  
* Ratio Épargne / Emprunt : Épargne globale rapportée au montant total sollicité.

## **Étape 3 : Construction du Pipeline Scikit-Learn Étanche** {#étape-3-:-construction-du-pipeline-scikit-learn-étanche}

Pour éviter toute fuite d'information (Data Leakage) entre le train et le test, l'intégralité du prétraitement doit être encapsulée dans un ColumnTransformer standardisé :

* Branche numérique : Imputation par la médiane (SimpleImputer) suivie d'une standardisation (StandardScaler).  
* Branche catégorielle : Imputation par constante 'INCONNU' suivie d'un encodage OneHot (OneHotEncoder avec handle\_unknown='ignore').  
* Pipeline unifié : Assemblage du ColumnTransformer et de l'estimateur dans un objet Pipeline unique.

## **Étape 4 : Validation Croisée K-Fold Stratifiée** {#étape-4-:-validation-croisée-k-fold-stratifiée}

Il est formellement interdit d'ajuster vos hyperparamètres sur le jeu de test final. Vous devez configurer une validation croisée à 5 plis stratifiés (StratifiedKFold) sur vos données d'entraînement. Vos scores de comparaison intermédiaires doivent obligatoirement être présentés sous forme moyenne \+/- écart-type.

## **Étape 5 : Optimisation Bayésienne avec Optuna** {#étape-5-:-optimisation-bayésienne-avec-optuna}

Mettez en place une étude Optuna (Study) pour calibrer automatiquement les hyperparamètres clés de vos modèles (ex. nombre d'arbres n\_estimators, profondeur max\_depth, critère de division). Comparez au moins deux familles d'algorithmes (ex. Forêts Aléatoires vs Gradient Boosting / XGBoost).

# 

# **Section 4 : Livrables Attendus et Critères d'Évaluation** {#section-4-:-livrables-attendus-et-critères-d'évaluation}

## **Livrables Techniques Obligatoires** {#livrables-techniques-obligatoires}

* 1\. Un Notebook Jupyter propre et commenté traçant les expérimentations, les courbes de convergence Optuna et les matrices de confusion.  
* 2\. Deux artefacts de modèles sérialisés au format joblib prêts à l'inférence (best\_regressor\_pipeline.joblib et best\_classifier\_pipeline.joblib).  
* 3\. Un script de test Pytest vérifiant la validité des dimensions de sortie et la tolérance aux valeurs inconnues du pipeline final.  
* 4\. Une fiche de synthèse (1 page) présentant le tableau comparatif des scores obtenus par chaque modèle et l'analyse métier des compromis statistiques.

## **Grille d'Évaluation & Classement de la Compétition** {#grille-d'évaluation-&-classement-de-la-compétition}

* Rigueur méthodologique (40%) : Absence totale de Data Leakage, utilisation irréprochable de StratifiedKFold et Pipeline.  
* Performance des modèles (30%) : Score R² en régression et ROC-AUC en classification sur le jeu de test scellé.  
* Optimisation Optuna (20%) : Structuration de la fonction objectif, pertinence des espaces de recherche et efficacité de convergence.  
* Qualité logicielle & Tests (10%) : Clarté du code, tests unitaires Pytest passants et documentation des variables.

| \[Règle de Conduite de la Compétition\] L'esprit de cette compétition est l'émulation collective. Le partage des bonnes pratiques, des astuces de feature engineering et l'entraide entre groupes lors des débriefings font partie intégrante des compétences de travail collaboratif évaluées dans le parcours. |
| :---- |

