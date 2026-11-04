"""Page 2 : Analyseur de Sentiment (Baseline Lexicale NLTK VADER M0).

Starter Kit Apprenants - Brief 1 IA-TOS.
"""

import os
import requests
import streamlit as st

FASTAPI_URL = os.getenv("FASTAPI_BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Analyse de Sentiment | Brief 1",
    page_icon="💬",
    layout="wide",
)

st.title("Page 2 : Analyseur de Sentiment des Retours Clients")
st.markdown("""
Cette page interroge le microservice NLP d'analyse de polarite base sur la methode lexicale 
**NLTK VADER** (`SentimentIntensityAnalyzer`).
""")

st.info("""
**Note d'architecture pedagogique (M0)** : Cette approche par dictionnaire lexical constitue notre 
baseline de depart. Elle sera confrontee puis remplacee dans les modules suivants par des modeles 
de Transformers pre-entraines en francais (**CamemBERT / RoBERTa**) et du Fine-Tuning LoRA (PEFT).
""")

# ==============================================================================
# TODO (Apprenants) : Implémenter la saisie textuelle et l'appel API
#
# Étapes suggérées :
# 1. Proposer une zone de saisie texte avec st.text_area().
# 2. Optionnel : Proposer des boutons de texte d'exemples (positif, négatif, neutre).
# 3. Ajouter un bouton d'action avec st.button("Analyser la polarité").
# 4. Lors du clic :
#    a. Émettre un POST vers f"{FASTAPI_URL}/predict/sentiment" avec le payload JSON :
#       {"texte": texte_saisi}
#    b. Récupérer la réponse JSON (SentimentPredictResponse) contenant :
#       - label (str : 'Positif', 'Neutre', 'Negatif')
#       - compound (float entre -1.0 et 1.0)
#       - details (dict avec 'pos', 'neu', 'neg')
#       - method (str)
#    c. Restituer le résultat avec des composants visuels adaptés (st.metric, st.progress, etc.).
# ==============================================================================

st.markdown("### Analysez la polarité d'un texte")

# Initialiser le session state pour le texte sentiment
if "texte_sentiment" not in st.session_state:
    st.session_state.texte_sentiment = ""


def set_texte(valeur: str) -> None:
    # Callback on_click : s'exécute avant l'instanciation du text_area
    st.session_state.texte_sentiment = valeur


# Zone de saisie texte (liée au session_state via key)
texte_saisie = st.text_area(
    "Entrez un avis ou un message client :",
    placeholder="Ex: Le service était excellent et le produit de très bonne qualité !",
    height=120,
    key="texte_sentiment"  # ← Clé pour lier au session_state
)

# Boutons d'exemples pré-remplis
st.markdown("**Exemples pré-remplis :**")
col1, col2, col3 = st.columns(3)

exemple_positif = "Ce produit est fantastic ! J'en suis très satisfait et je le recommande vivement."
exemple_negatif = "Très déçu par la qualité. Le service client est horrible et rien ne fonctionne correctement."
exemple_neutre = "Le produit a été livré hier. Le prix était de 50 euros. Nous avons commandé deux unités."

col1.button("📈 Positif", use_container_width=True, on_click=set_texte, args=(exemple_positif,))
col2.button("➡️ Neutre", use_container_width=True, on_click=set_texte, args=(exemple_neutre,))
col3.button("📉 Négatif", use_container_width=True, on_click=set_texte, args=(exemple_negatif,))

# Bouton d'analyse
if st.button("Analyser la polarité", type="primary", use_container_width=True):
    if not texte_saisie.strip():
        st.warning("Veuillez entrer un texte à analyser.")
    else:
        try:
            with st.spinner("Analyse en cours..."):
                response = requests.post(
                    f"{FASTAPI_URL}/predict/sentiment",
                    json={"texte": texte_saisie},
                    timeout=10
                )
            
            if response.status_code == 200:
                data = response.json()
                label = data["label"]
                compound = data["compound"]
                scores = data["scores"]  # {"neg": ..., "neu": ..., "pos": ..., "compound": ...}
                
                st.divider()
                st.markdown("### Résultats de l'analyse")
                
                # Badge de sentiment avec couleur
                if label == "Positif":
                    st.success(f"✅ {label} (Compound: {compound:.3f})")
                elif label == "Neutre":
                    st.info(f"➡️ {label} (Compound: {compound:.3f})")
                else:  # Négatif
                    st.error(f"❌ {label} (Compound: {compound:.3f})")
                
                # Afficher les scores en colonnes
                st.markdown("**Répartition des polarités :**")
                col_pos, col_neu, col_neg, col_comp = st.columns(4)
                
                with col_pos:
                    st.metric(
                        "Positif",
                        f"{scores.get('pos', 0):.1%}",
                        help="Proportion de positivité"
                    )
                
                with col_neu:
                    st.metric(
                        "Neutre",
                        f"{scores.get('neu', 0):.1%}",
                        help="Proportion de neutralité"
                    )
                
                with col_neg:
                    st.metric(
                        "Négatif",
                        f"{scores.get('neg', 0):.1%}",
                        help="Proportion de négativité"
                    )
                
                with col_comp:
                    st.metric(
                        "Compound",
                        f"{compound:.3f}",
                        help="Score global (-1 à 1)"
                    )
                
                # Barre de progression compound
                normalized_compound = (compound + 1) / 2  # Convertir -1..1 en 0..1
                st.progress(normalized_compound)
                
                # Détails
                with st.expander("Détails de l'analyse"):
                    st.json({
                        "texte": texte_saisie[:100] + "..." if len(texte_saisie) > 100 else texte_saisie,
                        "label": label,
                        "compound": compound,
                        "scores": {
                            "positif": scores.get('pos', 0),
                            "neutre": scores.get('neu', 0),
                            "negatif": scores.get('neg', 0)
                        },
                        "type_modele": data.get("type_modele", "N/A")
                    })
            
            elif response.status_code == 422:
                st.error("Erreur de validation : Texte vide ou invalide.")
            else:
                st.error(f"Erreur API : {response.status_code}")
        
        except requests.exceptions.Timeout:
            st.error("Timeout : Le serveur a pris trop de temps à répondre.")
        except Exception as e:
            st.error(f"Erreur : {str(e)}")
