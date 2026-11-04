"""Point d'entree principal de l'API FastAPI - Starter Kit Apprenants.

Ce fichier est le coeur de votre mission pour le backend de la plateforme IA-TOS.
Vous devez completer les routes ci-dessous en vous appuyant sur :
- Le package metier : iatos_core (agents, scoring, sentiment, logger, config)
- Le contrat d'interface : backend.schemas (Pydantic v2)
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from iatos_core import __version__
from iatos_core.logger import logger
from iatos_core.ml.scoring import CreditScoringPredictor
from iatos_core.ml.sentiment import SentimentAnalyzer
from iatos_core.agent.graph import run_agent_message

from backend.schemas import (
    ChatRequest,
    ChatResponse,
    CreditPredictRequest,
    CreditPredictResponse,
    HealthResponse,
    SentimentPredictRequest,
    SentimentPredictResponse,
)

# Services partages (Singletons en memoire)
scoring_predictor: CreditScoringPredictor = None
sentiment_analyzer: SentimentAnalyzer = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Cycle de vie de l'application FastAPI.
    
    Initialise les modeles ML au demarrage et les libere a l'arret.
    """
    global scoring_predictor, sentiment_analyzer
    logger.info("Demarrage des services FastAPI IA-TOS...")
    
    # Initialiser les modeles une seule fois
    scoring_predictor = CreditScoringPredictor()
    sentiment_analyzer = SentimentAnalyzer()
    logger.success("Services initialises : CreditScoringPredictor + SentimentAnalyzer")
    
    yield
    logger.info("Arret des services FastAPI IA-TOS.")


# Instanciation de l'application FastAPI
app = FastAPI(
    title="Plateforme IA-TOS - API Multi-Services",
    description="API exposant l'agent conversationnel LangGraph, le scoring de credit et l'analyse de sentiment.",
    version=__version__,
    lifespan=lifespan,
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse, tags=["Supervision"])
def health_check():
    """Endpoint de surveillance (Healthcheck) pour Uptime Kuma ou Docker.
    
    Returns:
        HealthResponse avec status, version et service.
    """
    return HealthResponse(
        status="ok",
        version=__version__,
        service="iatos-api"
    )


@app.post("/chat", response_model=ChatResponse, tags=["Agent Conversationnel"])
def chat_endpoint(payload: ChatRequest):
    """Endpoint conversationnel interrogeant l'agent LangGraph outille.
    
    TODO (Apprenants) :
    1. Convertir l'historique Pydantic (payload.history) en liste de dictionnaires [{'role': ..., 'content': ...}].
    2. Appeler run_agent_message(user_message=payload.message, history=history_dicts).
    3. Retourner une instance de ChatResponse avec :
       - success (bool)
       - response (str)
       - tool_called (bool)
       - tool_results (list[str])
    4. Gerer les exceptions potentielles avec un logger.error et un HTTPException(500).
    """
    # TODO: Remplacer par votre implementation
    try:
        history_dicts = []
        for msg in payload.history:
            history_dicts.append({
                "role": msg.role,
                "content": msg.content
            })

        logger.info(
            "Message recu: {msg}, historique: {n} messages",
            msg=payload.message,
            n=len(history_dicts)
        )
        agent_result = run_agent_message(
            user_message=payload.message,
            history=history_dicts
        )
        logger.info(
            "Agent response: success={s}, tool_called={t}",
            s=agent_result["success"],
            t=agent_result["tool_called"]
        )

        return ChatResponse(
            success=agent_result["success"],
            response=agent_result["response"],
            tool_called=agent_result["tool_called"],
            tool_results=agent_result["tool_results"]
        )
    except Exception as e:
        logger.error(
            "Erreur dans /chat endpoint: {error_type} - {error_msg}",
            error_type=type(e).__name__,
            error_msg=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Erreur serveur : {str(e)}"
        )


@app.post("/predict/credit", response_model=CreditPredictResponse, tags=["Scoring Tabulaire"])
def predict_credit(payload: CreditPredictRequest):
    """Endpoint de prediction du score de credit (baseline Scikit-Learn M0).
    
    Args:
        payload: CreditPredictRequest contenant montant, duree et revenu
        
    Returns:
        CreditPredictResponse avec score, decision, motif et metadonnees
        
    Raises:
        HTTPException(500): En cas d'erreur serveur
    """
    try:
        global scoring_predictor
        
        # ÉTAPE 1: Vérifier que le prédicteur est chargé
        if scoring_predictor is None:
            logger.warning("scoring_predictor non charge, initialisation...")
            scoring_predictor = CreditScoringPredictor()
        
        logger.info(
            "Requete scoring credit : montant={m}E, duree={d}m, revenu={r}E",
            m=payload.montant_demande,
            d=payload.duree_mois,
            r=payload.revenu_mensuel
        )
        
        # ÉTAPE 2: Appeler le prédicteur avec les paramètres du payload
        result = scoring_predictor.predict(
            montant_demande=payload.montant_demande,
            duree_mois=payload.duree_mois,
            revenu_mensuel=payload.revenu_mensuel
        )
        
        # ÉTAPE 3: Construire et retourner la réponse Pydantic
        logger.info(
            "Scoring termine : score={s}, decision={d}",
            s=result["score"],
            d=result["decision"]
        )
        
        return CreditPredictResponse(
            score=result["score"],
            decision=result["decision"],
            motif=result["motif"],
            features_utilisees=result["features_utilisees"],
            type_modele=result["type_modele"]
        )
    
    except Exception as exc:
        # ÉTAPE 4: Gerer les exceptions
        logger.error(
            "Erreur dans /predict/credit endpoint: {error_type} - {error_msg}",
            error_type=type(exc).__name__,
            error_msg=str(exc)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Erreur serveur lors du scoring de credit : {str(exc)}"
        )


@app.post("/predict/sentiment", response_model=SentimentPredictResponse, tags=["Traitement NLP"])
def predict_sentiment(payload: SentimentPredictRequest):
    """Endpoint d'analyse de polarite de sentiment (baseline NLTK VADER M0).
    
    Args:
        payload: SentimentPredictRequest contenant le texte a analyser
        
    Returns:
        SentimentPredictResponse avec compound, label, scores et metadonnees
        
    Raises:
        HTTPException(500): En cas d'erreur serveur
    """
    try:
        global sentiment_analyzer
        
        # ÉTAPE 1: Vérifier que l'analyseur est chargé
        if sentiment_analyzer is None:
            logger.warning("sentiment_analyzer non charge, initialisation...")
            sentiment_analyzer = SentimentAnalyzer()
        
        logger.info(
            "Requete analyse sentiment : texte='{t}...'",
            t=payload.texte[:50]
        )
        
        # ÉTAPE 2: Appeler l'analyseur avec le texte du payload
        result = sentiment_analyzer.analyze(payload.texte)
        
        # ÉTAPE 3: Construire et retourner la réponse Pydantic
        logger.info(
            "Analyse terminee : label={l}, compound={c}",
            l=result["label"],
            c=result["compound"]
        )
        
        return SentimentPredictResponse(
            texte=result["texte"],
            compound=result["compound"],
            label=result["label"],
            scores=result["scores"],
            type_modele=result["type_modele"]
        )
    
    except Exception as exc:
        # ÉTAPE 4: Gerer les exceptions
        logger.error(
            "Erreur dans /predict/sentiment endpoint: {error_type} - {error_msg}",
            error_type=type(exc).__name__,
            error_msg=str(exc)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Erreur serveur lors de l'analyse de sentiment : {str(exc)}"
        )
