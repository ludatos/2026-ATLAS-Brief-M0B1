"""Page 1 : Formulaire de Scoring de Credit (Baseline Regression Lineaire M0).

Starter Kit Apprenants - Brief 1 IA-TOS.
"""

import os
import requests
import streamlit as st

FASTAPI_URL = os.getenv("FASTAPI_BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Scoring Credit | Brief 1",
    page_icon="💳",
    layout="wide",
)

st.title("Page 1 : Formulaire Predictif de Scoring de Credit")
st.markdown("""
Cette page interroge le microservice de scoring de credit base sur une **Regression Lineaire Scikit-Learn** 
entrainee sur les 3 variables financieres neutres du dossier (`montant_demande`, `duree_mois`, `revenu_mensuel`).
""")

st.info("""
**Note d'architecture pedagogique (M0)** : Ce modele est restreint a 3 variables neutres. 
Le dataset complet contient des variables demographiques et contextuelles qui serviront au **Module 2** 
pour realiser l'audit d'equite algorithmique (Disparate Impact), l'anonymisation RGPD et la mitigation des biais.
""")

# ==============================================================================
# TODO (Apprenants) : Implémenter le formulaire Streamlit et l'appel API
#
# Étapes suggérées :
# 1. Créer un formulaire avec st.form("form_credit").
# 2. Ajouter les champs de saisie :
#    - montant_demande (st.number_input, ex: 1000 à 50000 €)
#    - duree_mois (st.slider, ex: 6 à 84 mois)
#    - revenu_mensuel (st.number_input, ex: 500 à 20000 €)
#    - bouton de soumission (st.form_submit_button)
# 3. Lors de la soumission du formulaire :
#    a. Émettre un POST vers f"{FASTAPI_URL}/predict/credit" avec le payload JSON :
#       {"montant_demande": float, "duree_mois": int, "revenu_mensuel": float}
#    b. Récupérer la réponse JSON (CreditPredictResponse) contenant :
#       - score (float entre 300 et 850)
#       - decision (str : 'Favorable', 'Ajourne / Examen Approfondi', 'Defavorable')
#       - seuil_recommande (float)
#       - model_version (str)
#    c. Restituer visuellement le score (ex: st.metric, jauge de progression, couleur de badge).
# ==============================================================================

with st.form("form_credit"):
    st.markdown("### Simulez votre demande de crédit")
    
    col1, col2 = st.columns(2)
    
    with col1:
        montant_demande = st.number_input(
            "Montant demandé (€)",
            min_value=1000.0,
            max_value=500000.0,
            value=10000.0,
            step=500.0,
            help="Entre 1 000 € et 500 000 €"
        )
    
    with col2:
        revenu_mensuel = st.number_input(
            "Revenu mensuel net (€)",
            min_value=500.0,
            max_value=100000.0,
            value=3500.0,
            step=100.0,
            help="Entre 500 € et 100 000 €"
        )
    
    duree_mois = st.slider(
        "Durée du prêt (mois)",
        min_value=6,
        max_value=360,
        value=24,
        step=6,
        help="Entre 6 mois et 30 ans"
    )
    
    submit_button = st.form_submit_button("Calculer le score", use_container_width=True)

if submit_button:
    try:
        with st.spinner("Scoring en cours..."):
            response = requests.post(
                f"{FASTAPI_URL}/predict/credit",
                json={
                    "montant_demande": float(montant_demande),
                    "duree_mois": int(duree_mois),
                    "revenu_mensuel": float(revenu_mensuel)
                },
                timeout=10
            )
        
        if response.status_code == 200:
            data = response.json()
            score = data["score"]
            decision = data["decision"]
            motif = data["motif"]
            
            st.divider()
            
            # Afficher le score avec une métrique
            st.metric(
                label="Score de Crédit",
                value=f"{score:.0f}/850",
                help="Score entre 300 et 850 (standard FICO)"
            )
            
            # Barre de progression
            progress_value = (score - 300) / (850 - 300)  # Normaliser entre 0 et 1
            st.progress(progress_value)
            
            # Badge de décision avec couleur
            if decision == "Favorable":
                st.success(f"✅ {decision}")
                st.balloons()
            elif decision == "Ajourne / Examen Approfondi":
                st.warning(f"⏳ {decision}")
            else:  # Défavorable
                st.error(f"❌ {decision}")
            
            # Afficher le motif
            st.info(f"**Motif** : {motif}")
            
            # Afficher les détails
            with st.expander("Détails du scoring"):
                st.json({
                    "score": score,
                    "decision": decision,
                    "montant_demande": montant_demande,
                    "duree_mois": duree_mois,
                    "revenu_mensuel": revenu_mensuel,
                    "type_modele": data.get("type_modele", "N/A")
                })
        
        elif response.status_code == 422:
            st.error("Erreur de validation : Vérifiez les valeurs saisies.")
        else:
            st.error(f"Erreur API : {response.status_code}")
    
    except requests.exceptions.Timeout:
        st.error("Timeout : Le serveur a pris trop de temps à répondre.")
    except Exception as e:
        st.error(f"Erreur : {str(e)}")
