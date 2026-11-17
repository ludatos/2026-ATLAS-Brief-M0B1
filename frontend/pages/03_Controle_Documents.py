"""Controle indicatif du type de piece justificative avec CLIP."""

from hashlib import sha256
from io import BytesIO
import os
import warnings

from PIL import Image, UnidentifiedImageError
import pandas as pd
import requests
import streamlit as st


FASTAPI_URL = os.getenv("FASTAPI_BACKEND_URL", "http://localhost:8000")
CATEGORIES = {
    "identity card": "Carte d'identite",
    "bank statement": "Releve bancaire",
    "bank check": "Cheque bancaire",
    "blank paper": "Page blanche",
}

st.set_page_config(page_title="Controle des documents | IA-TOS", page_icon=":material/description:", layout="wide")
st.title("Controle des pieces justificatives")
st.caption("Classement indicatif du type de document. L'authenticite et la validite administrative ne sont pas verifiees.")

with st.sidebar:
    st.subheader("Criteres de revue")
    minimum_score = st.slider("Score minimal indicatif", 0.0, 1.0, 0.60, 0.05)
    minimum_margin = st.slider("Ecart minimal entre les deux premiers scores", 0.0, 1.0, 0.15, 0.05)

input_column, result_column = st.columns(2, gap="large")

with input_column:
    expected = st.selectbox("Piece attendue", list(CATEGORIES), format_func=CATEGORIES.get)
    labels = st.multiselect(
        "Categories candidates", list(CATEGORIES), default=list(CATEGORIES), format_func=CATEGORIES.get,
    )
    uploaded = st.file_uploader("Piece justificative", type=["jpg", "jpeg", "png"])
    content = uploaded.getvalue() if uploaded is not None else b""
    valid_image = False
    if uploaded is not None:
        if not content or len(content) > 5 * 1024 * 1024:
            st.error("Le fichier doit contenir entre 1 octet et 5 Mio.")
        else:
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("error", Image.DecompressionBombWarning)
                    with Image.open(BytesIO(content)) as image:
                        if image.format not in {"JPEG", "PNG"} or image.width * image.height > 16_000_000:
                            raise ValueError("Format ou dimensions invalides.")
                        image.verify()
                st.image(content, caption=uploaded.name, width="stretch")
                valid_image = True
            except (UnidentifiedImageError, OSError, SyntaxError, ValueError,
                    Image.DecompressionBombError, Image.DecompressionBombWarning):
                st.error("Image JPEG/PNG illisible ou depassant 16 millions de pixels.")

    valid_categories = len(labels) >= 2 and expected in labels
    if not valid_categories:
        st.warning("Au moins deux categories, dont la piece attendue, sont necessaires.")
    fingerprint = (sha256(content).hexdigest(), tuple(labels))
    if st.button(
        "Analyser la piece", icon=":material/document_scanner:", type="primary",
        disabled=not (valid_image and valid_categories),
    ):
        st.session_state.pop("vision_result", None)
        try:
            with st.spinner("Analyse du document..."):
                response = requests.post(
                    f"{FASTAPI_URL}/vision/classify-document",
                    files={"file": (uploaded.name, content, uploaded.type or "application/octet-stream")},
                    data={"labels": labels},
                    timeout=(5, 120),
                )
            if response.status_code == 200:
                st.session_state.vision_result = (fingerprint, response.json())
            elif response.status_code == 422:
                st.error("Le fichier ou les categories ont ete refuses par l'API.")
            elif response.status_code == 503:
                st.warning("Le modele n'est pas disponible.")
            else:
                st.error(f"Erreur du service de classification ({response.status_code}).")
        except requests.Timeout:
            st.error("Le delai d'attente de classification est depasse.")
        except requests.ConnectionError:
            st.error("Backend inaccessible. Il peut etre encore en cours de chargement.")
        except (requests.RequestException, ValueError):
            st.error("La reponse du service de classification est invalide.")

with result_column:
    st.subheader("Resultat du controle")
    stored = st.session_state.get("vision_result")
    if stored is not None and stored[0] == fingerprint and valid_categories and valid_image:
        result = stored[1]
        candidates = result["candidates"]
        confidence = result["confidence"]
        margin = confidence - candidates[1]["score"]
        if confidence < minimum_score or margin < minimum_margin:
            st.warning("A verifier - classement incertain")
        elif result["detected_document"] == expected:
            st.success("Categorie attendue detectee - authenticite non verifiee")
        else:
            st.error("La categorie detectee ne correspond pas a la piece attendue")
        st.metric("Document detecte", CATEGORIES.get(result["detected_document"], result["detected_document"]))
        st.metric("Score relatif CLIP", f"{confidence:.1%}")
        st.progress(confidence)
        chart = pd.DataFrame([
            {"Categorie": CATEGORIES.get(item["label"], item["label"]), "Score": item["score"]}
            for item in candidates
        ]).set_index("Categorie")
        st.bar_chart(chart, horizontal=True)
        with st.expander("Reponse API"):
            st.json(result)