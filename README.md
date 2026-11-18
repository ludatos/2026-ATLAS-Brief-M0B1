# Plateforme IA-TOS - Starter Kit Apprenants (Brief 1 / Module 0)

Bienvenue dans le starter kit du **Brief 1 - Module 0 (Socle Applicatif & Microservices IA)** du projet **IA-TOS (Intellicenter)** pour la promotion OPCO Atlas (Simplon & Atos 2026).

---

## Brief 3 - Optimisation du scoring ML

Le [notebook d'expérimentation](notebooks/03_Optimisation_Scoring_ML.ipynb) contient
le diagnostic, les variables métier, les références naïves, Random Forest,
Gradient Boosting, la validation à cinq plis et deux études Optuna de 20 essais.
La sélection utilise uniquement le train ; le test final est évalué ensuite.
L'exécution complète exporte les deux pipelines dans `models/` et une
[synthèse imprimable](notebooks/synthese_scoring_ml.html).
Les fonctions partagées sont dans `src/iatos_core/ml/credit_training.py` pour
permettre le rechargement joblib depuis un processus neuf.

```powershell
uv sync --extra dev --extra ml
```

Ouvrir le notebook dans VS Code et sélectionner le noyau Python de `.venv`
(Python 3.12 attendu par le brief). Le notebook utilise le CSV de `data/` et
ne remplace pas le modèle de l'application existante.

Tests ciblés : `uv run pytest tests/test_credit_training.py -q`.

---

## 1. Contexte du Projet

L'entreprise **TOS** modernise son architecture décisionnelle et opérationnelle à travers la création d'une plateforme unifiée d'intelligence artificielle : **IA-TOS**.

Dans ce premier sprint de **5 heures**, votre objectif est d'intégrer les briques d'IA et de Machine Learning développées par l'équipe Data Science dans une architecture microservices robuste, documentée et testable.

```
                          ┌────────────────────────┐
                          │   Frontend Streamlit   │
                          │   (Multi-Pages UI)     │
                          └───────────┬────────────┘
                                      │ HTTP (JSON)
                                      ▼
                          ┌────────────────────────┐
                          │     Backend FastAPI    │
                          │  (/health, /chat, ...) │
                          └───────────┬────────────┘
                                      │ In-Memory Call
                                      ▼
       ┌──────────────────────────────────────────────────────────────┐
       │                 Package Métier : iatos_core                  │
       │                                                              │
       │  ┌────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
       │  │ LangGraph +    │  │ Scikit-Learn     │  │ NLTK VADER   │  │
       │  │ Ollama (Agent) │  │ (Credit Scoring) │  │ (Sentiment)  │  │
       │  └────────────────┘  └──────────────────┘  └──────────────┘  │
       └──────────────────────────────────────────────────────────────┘
```

---

## 2. Répartition du Code : Ce qui est Fourni vs Ce que vous devez Coder

### Fourni clé en main (Socle Métier & Infrastructure)
- **Package Python Métier `iatos_core`** (`src/iatos_core/`) :
  - `agent/` : Graphe agentique LangGraph ReAct avec outil arithmétique déterministe.
  - `ml/scoring.py` : Prédicteur de score de crédit (Scikit-Learn).
  - `ml/sentiment.py` : Analyseur lexical de polarité de sentiment (NLTK VADER).
  - `tools/math_tool.py` : Outil de calcul arithmétique pour l'agent.
  - `logger.py` & `config.py` : Journalisation Loguru centralisée et configuration.
- **Documentation Sphinx complète** (`docs/`) :
  - Code source `.rst` et site HTML statique prêt à l'emploi (`docs/_build/html/index.html`).
- **Données & Modèle Pré-entraîné** :
  - `data/credit_risk_dataset.csv` : Dataset de 1 200 dossiers clients (17 variables).
  - `models/credit_linear_model.joblib` : Modèle de régression linéaire baseline M0 pré-entraîné.
- **Contrats d'Interface Pydantic v2** (`backend/schemas.py`) :
  - Schémas stricts imposés par l'équipe d'architecture pour garantir l'interopérabilité.
- **Suite de Tests d'Intégration** (`tests/`) :
  - Tests unitaires de `iatos_core` et tests d'intégration des endpoints FastAPI.
- **Orchestration Docker** :
  - `docker-compose.yml` préconfiguré pour orchestrer les conteneurs backend et frontend.

### À développer par vous (Votre Mission)
1. **Le Backend FastAPI (`backend/main.py`)** :
   - Initialiser l'application avec la gestion du cycle de vie (`lifespan`).
   - Implémenter les 4 endpoints REST :
     - `GET /health` (Supervision)
     - `POST /chat` (Agent conversationnel outillé)
     - `POST /predict/credit` (Scoring crédit)
     - `POST /predict/sentiment` (Analyse de sentiment)
2. **Le Frontend Streamlit Multi-Pages (`frontend/`)** :
   - `frontend/app.py` : Page d'accueil & Page 0 (Chatbot LangGraph avec restitution des traces d'outils).
   - `frontend/pages/01_Credit_Scoring.py` : Page 1 (Formulaire prédictif pour le scoring de crédit).
   - `frontend/pages/02_Sentiment.py` : Page 2 (Analyseur de sentiment textuel).
3. **La Conteneurisation Docker (`backend/Dockerfile` & `frontend/Dockerfile`)** :
   - `backend/Dockerfile` (actuellement vide) : Rédiger l'image Docker pour le backend FastAPI en installant les dépendances avec `uv` ou `pip`.
   - `frontend/Dockerfile` (actuellement vide) : Rédiger l'image Docker pour le frontend Streamlit.
   - Valider l'orchestration complète avec `docker compose up --build`.

---

## 3. Guide de Démarrage Rapide avec UV

Le projet est entièrement géré avec le gestionnaire de paquets ultra-rapide **uv**.

### Étape 1 : Synchroniser l'environnement virtuel avec UV
À la racine du dépôt :
```bash
uv sync --extra dev
```
> Cette commande unique crée automatiquement l'environnement virtuel `.venv`, installe toutes les dépendances verrouillées dans `uv.lock` et monte le package `iatos_core` en mode éditable !

### Étape 2 : Télécharger le modèle LLM local (Ollama)
Si vous ne l'avez pas encore fait, installez Ollama et récupérez le modèle Qwen 2.5 :
```bash
ollama run qwen2.5:7b
```

### Étape 3 : Lancer les tests unitaires
Les tests sur le package métier `iatos_core` doivent passer immédiatement au vert :
```bash
uv run pytest tests/test_math_tool.py tests/test_ml_models.py -v
```
Au fur et à mesure que vous implémentez `backend/main.py`, vous validerez les tests d'intégration :
```bash
uv run pytest tests/test_fastapi_endpoints.py -v
```
Pour exécuter l'ensemble de la suite de tests :
```bash
uv run pytest -v
```

---

## 4. Lancement des Services en Local

### Lancement du Backend FastAPI (Port 8000)
```bash
uv run uvicorn backend.main:app --reload --port 8000
```
- Documentation Swagger interactive : [http://localhost:8000/docs](http://localhost:8000/docs)
- Documentation ReDoc : [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Lancement du Frontend Streamlit (Port 8501)
Dans un second terminal :
```bash
uv run streamlit run frontend/app.py
```
- Interface Web : [http://localhost:8501](http://localhost:8501)

### Lancement via Docker Compose (Conteneurisation)
Une fois vos fichiers `backend/Dockerfile` et `frontend/Dockerfile` complétés :
```bash
docker compose up --build
```
Le fichier `docker-compose.yml` est déjà configuré pour pointer vers chacun des deux Dockerfiles (`backend/Dockerfile` et `frontend/Dockerfile`).

---

## 5. Consulter la Documentation Sphinx

La documentation complète de l'API et du package `iatos_core` est disponible en HTML statique. Pour la consulter :
- Ouvrez simplement dans votre navigateur : `docs/_build/html/index.html`

Pour recompiler la documentation après modification des docstrings :
```bash
sphinx-build -b html docs docs/_build/html
```

---

## 6. Structure Complète du Dépôt

```text
2026-ATLAS-Brief-M0B1/
├── pyproject.toml                  # Configuration du package iatos_core et dependances
├── uv.lock                         # Fichier de verrouillage des versions UV
├── docker-compose.yml              # Orchestration conteneurs (backend + frontend)
├── BRIEF_1_SIMPLONLINE.md          # Sujet detaille du brief
├── README.md                       # Guide de demarrage et consignes
│
├── data/
│   ├── credit_risk_dataset.csv     # Dataset Credit Risk (1 200 lignes, 17 colonnes)
│   ├── generate_dataset.py         # Script de generation du dataset
│   └── train_baseline.py           # Script d'entrainement de la baseline de regression
│
├── models/
│   └── credit_linear_model.joblib  # Modele baseline serialise
│
├── docs/                           # Documentation Sphinx
│   ├── conf.py                     # Configuration Sphinx & Theme Furo
│   ├── index.rst                   # Sommaire principal
│   └── _build/html/index.html      # Site de documentation compile
│
├── src/
│   └── iatos_core/                 # Package Python metier ("fourni cle en main")
│       ├── __init__.py
│       ├── config.py               # Constantes et variables d'environnement
│       ├── logger.py               # Journalisation centralisee Loguru
│       ├── tools/math_tool.py      # Outil de calcul arithmetique LangGraph
│       ├── agent/                  # Graphe agentique LangGraph ReAct
│       └── ml/                     # Wrappers ML (Scoring credit) et NLP (Sentiment)
│
├── backend/
│   ├── __init__.py
│   ├── schemas.py                  # Contrats Pydantic v2 fixes (NE PAS MODIFIER)
│   ├── main.py                     # A COMPLETER : Application FastAPI & Routes REST
│   └── Dockerfile                  # A COMPLETER : Image conteneur Backend FastAPI
│
├── frontend/
│   ├── app.py                      # A COMPLETER : Page d'accueil & Page 0 (Chatbot)
│   ├── Dockerfile                  # A COMPLETER : Image conteneur Frontend Streamlit
│   └── pages/
│       ├── 01_Credit_Scoring.py    # A COMPLETER : Page 1 (Scoring de credit)
│       └── 02_Sentiment.py         # A COMPLETER : Page 2 (Analyse de sentiment)
│
└── tests/                          # Suite de tests Pytest automatisee
    ├── __init__.py
    ├── conftest.py                 # Fixtures TestClient FastAPI
    ├── test_math_tool.py           # Tests unitaires de l'outil arithmetique
    ├── test_ml_models.py           # Tests unitaires du scoring et sentiment
    └── test_fastapi_endpoints.py   # Tests d'integration FastAPI
```

Bon développement sur le socle IA-TOS !
