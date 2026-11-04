# 📚 FORMATION - Socle Applicatif IA-TOS (Module 0)

## 🎯 Résumé de la Session

Cette session a couvert l'implémentation complète des **4 routes FastAPI** du backend IA-TOS :
- ✅ `/health` - Endpoint de supervision
- ✅ `/chat` - Agent conversationnel LangGraph
- ✅ `/predict/credit` - Scoring de crédit
- ✅ `/predict/sentiment` - Analyse de sentiment NLTK VADER

---

## 🤔 Interrogations Principales

### 1️⃣ **"Qu'est-ce que LangGraph ReAct ?"**

#### Question Posée
> "De ce que je comprends c'est un outil qui permet d'appeler l'API Ollama pour interroger le modèle. Est-ce que cela fait des choses en plus comme de la mise en cache, de la sécurité ou tout autre chose ?"

#### Explication Donnée
**LangGraph ReAct n'est pas qu'un simple wrapper d'Ollama**, c'est un orchestrateur intelligent qui :

- **Pattern ReAct** : Reasoning + Acting
  - L'LLM **raisonne** s'il doit appeler un outil
  - L'agent **agit** en exécutant l'outil
  - L'LLM **reçoit le feedback** et formule une réponse

- **Historique Conversationnel** : Gère le contexte complet
  - Chaque message de l'historique est converti en `LangChain Message`
  - L'LLM a accès à toute la conversation

- **Traçabilité des Outils** : Capture tous les outils appelés
  - Retourne `tool_called` (boolean)
  - Retourne `tool_results` (liste complète des résultats)
  - Permet à Streamlit d'afficher des expanders avec la trace technique

- **Logging Intelligent** : Gestion d'erreurs robuste
  - Logs détaillés avec Loguru
  - Messages user-friendly avec diagnostic technique
  - Pas de crash de l'API

- **Ce qui N'est PAS inclus** :
  - ❌ Caching des réponses LLM
  - ❌ Validation de sécurité du prompt (inlection)
  - ❌ Rate limiting (géré au niveau FastAPI)
  - ❌ Fallback sur modèle alternatif

**Source** : [src/iatos_core/agent/graph.py](src/iatos_core/agent/graph.py)

---

### 2️⃣ **"Comment implémenter le TODO du `/chat` endpoint ?"**

#### Actions Expliquées
Le TODO avait 4 étapes :

**ÉTAPE 1 : Convertir l'Historique Pydantic en Dictionnaires**
```python
# Input : List[ChatMessage] objects (Pydantic)
payload.history = [
    ChatMessage(role="user", content="Combien fait 15 + 27 ?"),
    ChatMessage(role="assistant", content="Je vais calculer..."),
]

# Output : List[Dict] (attendu par run_agent_message)
history_dicts = [
    {"role": msg.role, "content": msg.content}
    for msg in payload.history
]
```
**Raison** : `run_agent_message()` prend une `List[Dict[str, str]]`, pas des Pydantic objects

**ÉTAPE 2 : Appeler run_agent_message()**
```python
result = run_agent_message(
    user_message=payload.message,
    history=history_dicts
)
# Retourne : {
#     "success": True,
#     "response": "Le résultat est 42",
#     "tool_called": True,
#     "tool_results": ["Le résultat de 15 + 27 est 42"]
# }
```

**ÉTAPE 3 : Construire la Réponse Pydantic**
```python
return ChatResponse(
    success=result["success"],
    response=result["response"],
    tool_called=result["tool_called"],
    tool_results=result["tool_results"]
)
```

**ÉTAPE 4 : Gestion des Exceptions**
```python
except Exception as exc:
    logger.error("Erreur : {error}", error=str(exc))
    raise HTTPException(status_code=500, detail=f"Erreur : {str(exc)}")
```

**Résultat** : ✅ Implémenté et testé avec succès

**Source** : [backend/main.py (lignes 83-137)](backend/main.py)

---

### 3️⃣ **"Comment tester cette première implémentation ?"**

#### Problèmes Rencontrés & Solutions

**Problème 1 : NLTK nécessite le téléchargement du lexique**
```
LookupError: Resource 'vader_lexicon' not found
```
**Solution** :
```powershell
$env:NLTK_ALLOW_PROXIED_URLOPEN=1
.venv\Scripts\python -c "import nltk; nltk.download('vader_lexicon')"
```

**Problème 2 : Ollama conteneur Docker vs Ollama natif**
- D'abord un conteneur `iatos_ollama` tournait en Docker
- Il a été supprimé pour utiliser l'instance native
- **Règle à retenir** : Dans Docker, Ollama écoute sur `http://host.docker.internal:11434`

**Problème 3 : Le modèle était téléchargé mais pas visible**
- `ollama list` montrait `qwen2.5:7b` ✅
- Mais `requests.get('http://localhost:11434/api/tags')` retournait une liste vide ❌
- **Cause** : Les conteneurs Docker avaient besoin d'être relancés

#### Commandes de Test

**Test Health Check**
```powershell
curl http://127.0.0.1:8000/health
```
✅ Réponse : `{"status": "ok", "version": "0.1.0", "service": "iatos-api"}`

**Test Chat avec Calcul Arithmétique**
```powershell
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Combien fait 42 + 8 ?", "history": []}'
```
✅ Réponse : Génère une réponse et appelle le tool arithmétique

**Test Pytest**
```powershell
uv run pytest tests/test_fastapi_endpoints.py -v
```
✅ Tous les tests passent

---

### 4️⃣ **"Dois-je lancer Ollama avec `nv` ?"**

#### Clarification
Vous aviez demandé si le backend devait être lancé avec `nv` (que j'ai interprété comme `uv`).

#### Réponse
**Oui**, utilisez `uv` pour tout lancer :

```powershell
# Démarrer le serveur
uv run python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000

# Lancer les tests
uv run pytest tests/ -v

# Lancer un script simple
uv run python test_chat_simple.py
```

**Raison** : `uv` gère automatiquement l'environnement virtuel et les dépendances

---

### 5️⃣ **"Pourquoi les tests Pytest n'affichaient rien ?"**

#### Explication
Le fichier `tests/test_fastapi_endpoints.py` contient des **tests Pytest**, pas un script Python classique.

**Différence** :
- Scripts Python : Exécution directe avec sortie texte
- Tests Pytest : Exécution via le runner pytest avec rapport structuré

**Bonne Commande** :
```powershell
uv run pytest tests/test_fastapi_endpoints.py -v
```

**Mauvaise Commande** :
```powershell
uv run python tests/test_fastapi_endpoints.py  # Ne montre rien
```

---

## ✅ Ce Qui a Été Fait

### Phase 1️⃣ : Préparation ✅

| Étape | Statut | Notes |
|-------|--------|-------|
| Lire le brief technique | ✅ | 178 lignes résumées |
| Installer dépendances avec `uv sync` | ✅ | 82 packages installés |
| Télécharger modèle Qwen 2.5 | ✅ | 4.7 GB via Ollama |
| Télécharger lexique NLTK VADER | ✅ | `vader_lexicon` configuré |

### Phase 2️⃣ : Implémentation Backend ✅

| Endpoint | Statut | Implémenté | Tests |
|----------|--------|-----------|-------|
| `/health` | ✅ | Oui | PASS |
| `/chat` | ✅ | Oui (LangGraph ReAct) | PASS |
| `/predict/credit` | ✅ | Oui (Scikit-Learn) | PASS |
| `/predict/sentiment` | ✅ | Oui (NLTK VADER) | PASS |

### Phase 3️⃣ : Pattern Lifespan ✅

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialisation au démarrage
    scoring_predictor = CreditScoringPredictor()
    sentiment_analyzer = SentimentAnalyzer()
    yield
    # Nettoyage à l'arrêt
```

✅ Les modèles ML sont **chargés une seule fois en mémoire**

### Phase 4️⃣ : Contrat Pydantic ✅

Tous les endpoints respectent le **contrat imposé** :
- ✅ `ChatRequest` / `ChatResponse`
- ✅ `CreditPredictRequest` / `CreditPredictResponse`
- ✅ `SentimentPredictRequest` / `SentimentPredictResponse`
- ✅ `HealthResponse`

### Phase 5️⃣ : Tests Backend ✅

```powershell
uv run pytest tests/ -v
```

Résultats :
- ✅ `test_endpoint_health` - PASS
- ✅ `test_endpoint_predict_credit_success` - PASS
- ✅ `test_endpoint_predict_credit_validation_error` - PASS
- ✅ `test_endpoint_predict_sentiment_success` - PASS
- ✅ `test_endpoint_chat_with_mocked_agent` - PASS

### Phase 6️⃣ : Implémentation Frontend Streamlit ✅

| Page | Fichier | Statut | Composants |
|------|---------|--------|-----------|
| **Page 0** | `frontend/app.py` | ✅ | Chat conversationnel + Expander trace tool |
| **Page 1** | `frontend/pages/01_Credit_Scoring.py` | ✅ | Formulaire + Métrique + Barre progress |
| **Page 2** | `frontend/pages/02_Sentiment.py` | ✅ | Text area + Boutons exemples + 4 colonnes |

---

## 🎨 **Frontend : Détails d'Implémentation**

### **Page 0 : Chatbot Conversationnel (app.py)**

#### Architecture

```
User Input (st.chat_input)
    ↓
Session State (messages history)
    ↓
POST /chat (avec history)
    ↓
LangGraph (Ollama Qwen 2.5)
    ↓
Response JSON (success, response, tool_called, tool_results)
    ↓
Afficher message assistant
    ↓
Si tool_called=true : afficher st.expander avec trace
```

#### Code Clé

```python
# Initialiser le historique
if "messages" not in st.session_state:
    st.session_state.messages = []

# Afficher les anciens messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Récupérer la saisie
user_input = st.chat_input("Posez une question...")

if user_input:
    # Ajouter et afficher le message utilisateur
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Préparer l'historique pour l'API
    history_payload = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in st.session_state.messages[:-1]
    ]
    
    # Appeler l'endpoint /chat
    response = requests.post(
        f"{FASTAPI_URL}/chat",
        json={"message": user_input, "history": history_payload},
        timeout=30
    )
    
    data = response.json()
    
    # Afficher la réponse
    with st.chat_message("assistant"):
        st.markdown(data["response"])
        
        # Afficher la trace si outil appelé
        if data.get("tool_called"):
            with st.expander("🔧 Trace technique"):
                for tool_result in data.get("tool_results", []):
                    st.code(tool_result)
```

#### Exemple d'Utilisation

```
User: "Combien fait 42 + 8 ?"
    ↓
Agent: "Le résultat de 42 + 8 est 50."
    ↓
Expander: "Le résultat de 42.0 + 8.0 est 50.0"
```

---

### **Page 1 : Formulaire Scoring Crédit (01_Credit_Scoring.py)**

#### Architecture

```
st.form (montant, durée, revenu)
    ↓
Submit button
    ↓
POST /predict/credit (avec les 3 paramètres)
    ↓
CreditScoringPredictor (Scikit-Learn)
    ↓
Response JSON (score, decision, motif, features_utilisees)
    ↓
Afficher métrique + barre progress + badge couleur
```

#### Code Clé

```python
with st.form("form_credit"):
    montant_demande = st.number_input(
        "Montant demandé (€)",
        min_value=1000.0,
        max_value=500000.0,
        value=10000.0
    )
    
    duree_mois = st.slider(
        "Durée du prêt (mois)",
        min_value=6,
        max_value=360,
        value=24
    )
    
    revenu_mensuel = st.number_input(
        "Revenu mensuel net (€)",
        min_value=500.0,
        max_value=100000.0,
        value=3500.0
    )
    
    submit_button = st.form_submit_button("Calculer le score")

if submit_button:
    response = requests.post(
        f"{FASTAPI_URL}/predict/credit",
        json={
            "montant_demande": montant_demande,
            "duree_mois": duree_mois,
            "revenu_mensuel": revenu_mensuel
        }
    )
    
    data = response.json()
    
    # Afficher le score
    st.metric("Score de Crédit", f"{data['score']:.0f}/850")
    
    # Barre de progression
    progress = (data['score'] - 300) / (850 - 300)
    st.progress(progress)
    
    # Badge de décision
    if data['decision'] == "Favorable":
        st.success(f"✅ {data['decision']}")
        st.balloons()
    elif data['decision'] == "Ajourne / Examen Approfondi":
        st.warning(f"⏳ {data['decision']}")
    else:
        st.error(f"❌ {data['decision']}")
    
    # Motif
    st.info(f"**Motif** : {data['motif']}")
```

#### Règles de Décision

| Score | Décision | Badge |
|-------|----------|-------|
| ≥ 650 | Favorable | ✅ Vert (balloons) |
| 550-649 | Ajourne | ⏳ Orange |
| < 550 | Défavorable | ❌ Rouge |

---

### **Page 2 : Analyseur Sentiment (02_Sentiment.py)**

#### Architecture

```
st.text_area (saisie texte)
    ↓
Boutons exemples (positif/neutre/négatif)
    ↓
st.button ("Analyser")
    ↓
POST /predict/sentiment (avec texte)
    ↓
SentimentAnalyzer (NLTK VADER)
    ↓
Response JSON (label, compound, scores)
    ↓
Afficher 4 colonnes (pos, neu, neg, compound)
```

#### Code Clé

```python
if "texte_sentiment" not in st.session_state:
    st.session_state.texte_sentiment = ""

def set_texte(valeur: str) -> None:
    # Callback on_click : exécuté AVANT l'instanciation du text_area
    st.session_state.texte_sentiment = valeur

texte_saisie = st.text_area(
    "Entrez un avis client :",
    placeholder="Ex: Le produit est excellent !",
    height=120,
    key="texte_sentiment",  # lie le widget au session_state
)

# Boutons exemples (callbacks on_click, pas de st.rerun())
col1, col2, col3 = st.columns(3)
col1.button("📈 Positif", on_click=set_texte, args=("Ce produit est fantastique !",))
col2.button("➡️ Neutre", on_click=set_texte, args=("Le produit a été livré hier.",))
col3.button("📉 Négatif", on_click=set_texte, args=("Très déçu par ce produit.",))

if st.button("Analyser la polarité"):
    response = requests.post(
        f"{FASTAPI_URL}/predict/sentiment",
        json={"texte": texte_saisie}
    )
    
    data = response.json()
    label = data["label"]
    compound = data["compound"]
    scores = data["scores"]
    
    # Badge de sentiment
    if label == "Positif":
        st.success(f"✅ {label} (Compound: {compound:.3f})")
    elif label == "Neutre":
        st.info(f"➡️ {label} (Compound: {compound:.3f})")
    else:
        st.error(f"❌ {label} (Compound: {compound:.3f})")
    
    # 4 colonnes de métriques
    col_pos, col_neu, col_neg, col_comp = st.columns(4)
    
    with col_pos:
        st.metric("Positif", f"{scores['pos']:.1%}")
    with col_neu:
        st.metric("Neutre", f"{scores['neu']:.1%}")
    with col_neg:
        st.metric("Négatif", f"{scores['neg']:.1%}")
    with col_comp:
        st.metric("Compound", f"{compound:.3f}")
    
    # Barre de progression
    normalized = (compound + 1) / 2  # -1..1 → 0..1
    st.progress(normalized)
```

#### Règles de Décision (VADER)

| Compound | Label | Seuil |
|----------|-------|-------|
| ≥ 0.05 | Positif | Threshold haut |
| -0.05 à 0.05 | Neutre | Zone intermédiaire |
| ≤ -0.05 | Négatif | Threshold bas |

---

## 🔧 **Commandes de Test Frontend**

### **Démarrer le frontend**

```powershell
$env:NLTK_ALLOW_PROXIED_URLOPEN=1
cd c:\GIT\formation-AI\2026-ATLAS-Brief-M0B1
uv run streamlit run frontend/app.py --server.port 8501
```

### **Accéder à l'interface**

```
http://localhost:8501
```

### **Menu de navigation (automatique)**

Streamlit détecte automatiquement :
- `frontend/app.py` → Page d'accueil + Page 0
- `frontend/pages/01_*.py` → Page 1
- `frontend/pages/02_*.py` → Page 2

---

## ✅ **Vérifier que Tout Fonctionne**

### **Étape 1 : Vérifier Ollama**

```powershell
# Port 11434 ouvert ?
Test-NetConnection -ComputerName localhost -Port 11434

# Modèle présent ?
ollama list

# API accessible ?
uv run python -c "import requests; print(requests.get('http://localhost:11434/api/tags').json())"
```

### **Étape 2 : Vérifier le Backend**

```powershell
# Tests Pytest
uv run pytest tests/ -v

# Ou test health
curl http://127.0.0.1:8000/health
```

### **Étape 3 : Tester le Frontend**

1. Ouvrir `http://localhost:8501`
2. Vérifier le statut de l'API dans la sidebar (doit être "En ligne")
3. Tester Page 0 : poser une question de calcul
4. Tester Page 1 : entrer des valeurs de crédit
5. Tester Page 2 : analyser un texte

---

## 📊 **Architecture Finale Implémentée**

```
┌──────────────────────────────────────────────┐
│     Frontend Streamlit (Port 8501)           │
│  ┌────────┬──────────┬────────────────────┐  │
│  │ Page 0 │ Page 1   │ Page 2             │  │
│  │ Chatbot│ Crédit   │ Sentiment          │  │
│  └────┬───┴────┬─────┴──────┬─────────────┘  │
└───────┼────────┼────────────┼────────────────┘
        │        │            │
        ▼        ▼            ▼
┌──────────────────────────────────────────────┐
│    Backend FastAPI (Port 8000)               │
│  ┌──────┬──────────┬──────────┬────────────┐ │
│  │Health│ /chat    │ /predict │ /predict   │ │
│  │      │          │ /credit  │ /sentiment │ │
│  └──┬───┴────┬─────┴────┬─────┴──────┬─────┘ │
└─────┼────────┼──────────┼────────────┼───────┘
      │        │          │            │
   ┌──▼──┐ ┌──▼──┐   ┌───▼──┐    ┌───▼──┐
   │Check│ │Lang │   │Score │    │Sent  │
   │Status
   │Graph│   │ML   │    │Analysis
   └─────┘ └─────┘   └──────┘    └──────┘
      │        │          │            │
      └────────┴──────────┴────────────┘
             │
             ▼
      ┌──────────────────┐
      │ Ollama (11434)   │
      │ Qwen 2.5 (7B)    │
      └──────────────────┘
```

---

## 🔑 **Concepts Clés du Frontend**

### 1. **Session State (st.session_state)**
- Persiste les variables entre les re-runs
- Utilisé pour l'historique des messages (`st.session_state.messages`)
- Un widget lié via `key="x"` stocke sa valeur dans `st.session_state.x`

#### ⚠️ Piège rencontré : boutons d'exemples de la page Sentiment
1. **Symptôme 1** : cliquer sur « Positif / Neutre / Négatif » ne mettait pas à jour le `st.text_area`.
   - Cause : `texte_saisie = "..."` modifie une variable locale, réinitialisée à chaque re-run.
2. **Symptôme 2** (après un premier correctif) : `StreamlitWidgetAlreadyInstantiatedError`.
   - Cause : on modifiait `st.session_state.texte_sentiment` après la création du widget portant cette clé, ce que Streamlit interdit.
3. **Solution** : modifier le session_state dans un callback `on_click`, qui s'exécute avant l'instanciation des widgets au re-run suivant. `st.rerun()` devient inutile.

### 2. **Formulaires Streamlit (st.form)**
- Groupe les inputs et les soumet ensemble
- Évite les re-runs à chaque modification

### 3. **Chat UI (st.chat_message, st.chat_input)**
- Interface naturelle de conversation
- Distinction visuelle user/assistant

### 4. **Expanders (st.expander)**
- Affiche du contenu technique replié
- Utilisé pour la trace des outils LangGraph

### 5. **Métriques Visuelles (st.metric, st.progress, balloons)**
- Rend les résultats lisibles et engageants
- Feedback immédiat à l'utilisateur

### 6. **Variable d'Environnement (FASTAPI_BACKEND_URL)**
- Permet Docker compose de rediriger vers le backend interne
- Local : `http://localhost:8000`
- Docker : `http://backend:8000`

---

## 📝 **Prochaines Étapes (Module 0 - Phase 3)**

### Orchestration Docker
- [ ] Vérifier `backend/Dockerfile` (si pas fourni)
- [ ] Vérifier `frontend/Dockerfile` (si pas fourni)
- [ ] Tester avec `docker compose up --build`
- [ ] Vérifier :
  - ✅ Swagger : http://localhost:8000/docs
  - ✅ Streamlit : http://localhost:8501
  - ✅ Logs : `logs/iatos_service.log`

### Tests d'Intégration
- [ ] Tester le flux complet (Backend + Frontend)
- [ ] Tester avec Docker Compose
- [ ] Valider la performance Ollama

### Modules Suivants
- [ ] Module 1 : Audit d'équité algorithmique
- [ ] Module 2 : Fine-tuning et optimisation
- [ ] Module 3 : Déploiement production

---

## 🔑 Concepts Clés Apris

### 1. **Pattern Lifespan (Context Manager)**
- Initialiser les ressources lourdes **une seule fois**
- Les variables globales persistent pendant toute la durée de vie de l'app

### 2. **Contrat d'Interface (Contract-First)**
- Les schémas Pydantic sont **figés** par l'équipe Architecture & Data Governance
- Jamais les modifier
- Pydantic valide automatiquement les erreurs 422

### 3. **Conversion Pydantic ↔ Dicts**
- Pydantic objects → Dicts : `{"role": msg.role, "content": msg.content}`
- Dicts → Pydantic : `ChatResponse(success=..., response=...)`

### 4. **Logging Structuré (Loguru)**
- `logger.info()` - Informations standard
- `logger.success()` - Opérations réussies
- `logger.error()` - Erreurs à catcher
- Format : `{timestamp} | {LEVEL} | {module}:{function}:{line} - {message}`

### 5. **Exception Handling**
- Toujours wrapper dans un `try/except`
- Logger l'erreur complète
- Retourner HTTP 500 avec message user-friendly

### 6. **Historique Conversationnel**
- Format : `[{"role": "user"|"assistant", "content": "..."}]`
- Convertir les `ChatMessage` Pydantic en dicts
- Passer à `run_agent_message()` pour garder le contexte

---

## 📝 Prochaines Étapes (Module 0 - Phase 2)

### Frontend Streamlit
- [ ] Implémenter `frontend/app.py` (Page 0 - Chatbot)
- [ ] Implémenter `frontend/pages/01_Credit_Scoring.py` (Page 1)
- [ ] Implémenter `frontend/pages/02_Sentiment.py` (Page 2)
- [ ] Variable d'environnement : `FASTAPI_BACKEND_URL`

### Orchestration Docker
- [ ] Créer `backend/Dockerfile` (si pas fourni)
- [ ] Créer `frontend/Dockerfile` (si pas fourni)
- [ ] Tester avec `docker compose up --build`
- [ ] Vérifier :
  - ✅ Swagger : http://localhost:8000/docs
  - ✅ Streamlit : http://localhost:8501
  - ✅ Logs : `logs/iatos_service.log`

### Tests Complets
- [ ] Tester l'intégration complète (Backend + Frontend)
- [ ] Tester avec Docker Compose
- [ ] Valider la performance Ollama

---

## 🔧 Commandes Utiles

### Démarrage
```powershell
# Vérifier Ollama
ollama list

# Démarrer le serveur
$env:NLTK_ALLOW_PROXIED_URLOPEN=1
uv run python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

### Tests
```powershell
# Tous les tests
uv run pytest tests/ -v

# Test spécifique
uv run pytest tests/test_fastapi_endpoints.py::test_endpoint_health -v

# Avec coverage
uv run pytest tests/ --cov=backend
```

### Accès à l'API
```powershell
# Swagger UI
http://127.0.0.1:8000/docs

# Health check
curl http://127.0.0.1:8000/health

# Chat
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Bonjour", "history": []}'
```

---

## 📚 Ressources Consultées

| Ressource | Lien |
|-----------|------|
| Brief technique | `/01_Brief_Socle_Applicatif_IA_TOS.md` |
| Package iatos_core | `/src/iatos_core/` |
| Schemas Pydantic | `/backend/schemas.py` |
| Graph LangGraph | `/src/iatos_core/agent/graph.py` |
| Scoring ML | `/src/iatos_core/ml/scoring.py` |
| Sentiment NLTK | `/src/iatos_core/ml/sentiment.py` |
| Tests Pytest | `/tests/test_fastapi_endpoints.py` |
| Configuration | `/pyproject.toml` |

---

## 💡 Points à Retenir

1. ✅ **Tous les TODOs du backend sont implémentés**
2. ✅ **Tous les tests Pytest passent**
3. ✅ **Le contrat Pydantic est respecté**
4. ✅ **Les modèles ML sont en mémoire (Lifespan)**
5. ✅ **LangGraph gère la logique d'agent intelligente**
6. ✅ **Frontend Streamlit 100% fonctionnel**
7. ✅ **Orchestration Docker : Dockerfiles rédigés, `docker compose up --build` validé**

---

## 🐳 Phase 7 : Conteneurisation Docker

### Ce qui a été fait
- `backend/Dockerfile` : `python:3.11-slim`, `pip install -e .` (installation *editable* car `config.py` calcule `BASE_DIR` depuis l'emplacement du package pour retrouver `models/` et `logs/`), téléchargement de `vader_lexicon` **au build** (`NLTK_DATA=/usr/local/share/nltk_data`), copie de `models/` et `backend/`.
- `frontend/Dockerfile` : `python:3.11-slim`, uniquement `streamlit` + `requests`, copie de `frontend/`.
- `.dockerignore` : exclut `.venv`, `.git`, `logs`, `docs`, `tests`, caches.
- Pas de `CMD` : les commandes de démarrage sont déjà définies dans `docker-compose.yml`.

### Interrogation : le lexique NLTK et le proxy
- VADER est un **dictionnaire de mots** non livré avec `nltk` : il est téléchargé au premier usage (`_ensure_lexicon`).
- Derrière un proxy d'entreprise, NLTK refuse le téléchargement sauf si `NLTK_ALLOW_PROXIED_URLOPEN=1` ; `quiet=True` masque l'erreur qui réapparaît ensuite en `LookupError`.
- Choix : téléchargement **au build** pour que le démarrage du conteneur ne dépende pas du réseau. Test réalisé sans proxy : OK.

### Validation
| Vérification | Résultat |
|---|---|
| `docker compose build` | ✅ |
| `GET /health` (localhost:8000) | ✅ |
| Streamlit (localhost:8501) | ✅ HTTP 200 |
| `POST /predict/credit` | ✅ score 615.3 |
| `POST /predict/sentiment` | ✅ |
| `POST /chat` (12 * 7) | ✅ `tool_called: true`, résultat 84 |
| frontend → `http://backend:8000` | ✅ |
| backend → `host.docker.internal:11434` (Ollama) | ✅ |

### Interrogation : le conteneur `moby/buildkit:buildx-stable-1`
- Ce conteneur (`buildx_buildkit_default`) n'appartient **pas** à l'application : c'est le **moteur de build de Docker**.
- **BuildKit** exécute les `docker build` / `docker compose build` (lecture des Dockerfiles, cache des couches) ; **buildx** est le plugin CLI qui le pilote.
- Il est créé automatiquement au premier build avec le driver `docker-container` et conserve le cache de build.
- Inoffensif : on peut le laisser. `docker rm -f buildx_buildkit_default` le supprime (recréé au prochain build, cache perdu). `docker compose down` ne l'arrête pas.

### Pièges rencontrés
- Le `uvicorn` lancé en local occupait le port 8000 : il faut l'arrêter avant `docker compose up`.
- VADER est un lexique **anglais** : un texte français comme « Ce produit est fantastique ! » renvoie `Neutre` (compound 0.0). C'est la limite attendue de la baseline M0, remplacée plus tard par CamemBERT/RoBERTa.

---

**Date** : 2026-11-04
**Durée** : ~2h
**Status** : ✅ COMPLÉTÉ - Backend + Frontend 100%
