from pathlib import Path
import re
import zipfile

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt


ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / ".github" / "skills" / "atos-brand-assets" / "assets"
OUTPUT = ROOT / "Presentation_Vision_CLIP_IA-TOS.pptx"
SPECIMEN = ROOT / "tests" / "data" / "specimen_identity_fr.png"

# Values copied from atos-tokens.css, the official 2026 token source.
DEEP = "00005C"
BLUE = "0073E6"
LIGHT = "3DC7FF"
WHITE = "FFFFFF"
DEEP_70 = "4D4D8D"
DEEP_20 = "CCCCDE"
DEEP_10 = "E6E6EF"
BLUE_10 = "E6F1FD"
BLUE_20 = "CCE3FA"
LIGHT_10 = "ECF9FF"
LIGHT_20 = "D8F4FF"
ORANGE_20 = "FDE1CC"

SW = 13.333
SH = 7.5
LOGO_BLUE = ASSETS / "logos" / "atos-logo-blue.svg"
LOGO_WHITE = ASSETS / "logos" / "atos-logo-white.svg"
CURVE_COVER = ASSETS / "curves" / "background-deepblue-1280x720.svg"


def rgb(value: str) -> RGBColor:
    return RGBColor.from_string(value)


def rect(slide, x, y, w, h, fill, border=None, border_width=0.8):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = rgb(fill)
    if border:
        shape.line.color.rgb = rgb(border)
        shape.line.width = Pt(border_width)
    else:
        shape.line.fill.background()
    return shape


def txt(slide, value, x, y, w, h, size=16, fill=DEEP, bold=False, font="Raleway",
        align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.MIDDLE, margin=0.02, italic=False):
    shape = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = shape.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.margin_left = Inches(margin)
    frame.margin_right = Inches(margin)
    frame.margin_top = Inches(margin)
    frame.margin_bottom = Inches(margin)
    frame.vertical_anchor = valign
    for index, chunk in enumerate(value.split("\n")):
        paragraph = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
        paragraph.alignment = align
        paragraph.space_before = Pt(0)
        paragraph.space_after = Pt(2 if index < len(value.split("\n")) - 1 else 0)
        paragraph.line_spacing = 1.0
        run = paragraph.add_run()
        run.text = chunk
        run.font.name = font
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.italic = italic
        run.font.color.rgb = rgb(fill)
    return shape


def add_logo(slide, white=False, x=11.54, y=0.38, width=1.04):
    path = LOGO_WHITE if white else LOGO_BLUE
    return slide.shapes.add_picture(str(path), Inches(x), Inches(y), width=Inches(width))


def accent_rule(slide, x, y):
    rect(slide, x, y, 0.78, 0.045, BLUE)
    rect(slide, x + 0.84, y, 0.34, 0.045, LIGHT)


def footer(slide, number, dark=False):
    ink = DEEP_20 if dark else DEEP_70
    line_y = 7.07
    separator = DEEP_70 if dark else DEEP_20
    connector = slide.shapes.add_connector(
        MSO_CONNECTOR.STRAIGHT, Inches(0.73), Inches(line_y), Inches(12.60), Inches(line_y)
    )
    connector.line.color.rgb = rgb(separator)
    connector.line.width = Pt(0.8)
    txt(slide, "Brief 2  ·  Vision CLIP", 0.74, 7.15, 5.2, 0.20, 8, ink, True)
    txt(slide, f"{number:02d} / 10", 11.57, 7.15, 1.02, 0.20, 8, ink, True, align=PP_ALIGN.RIGHT)


def content_slide(title, chapter, number):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = rgb(WHITE)
    txt(slide, chapter, 0.75, 0.34, 3.2, 0.28, 10, BLUE, True)
    add_logo(slide, white=False)
    txt(slide, title, 0.75, 0.82, 11.7, 0.72, 26, DEEP, True)
    accent_rule(slide, 0.76, 1.63)
    footer(slide, number)
    return slide


def chevron(slide, x, y, w=0.24, h=0.46, fill=BLUE):
    shape = slide.shapes.add_shape(MSO_SHAPE.CHEVRON, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = rgb(fill)
    shape.line.fill.background()
    shape.adjustments[0] = 0.25
    return shape


def square_bullet(slide, value, x, y, w, size=14, fill=DEEP, dot=BLUE, h=0.50):
    rect(slide, x, y + 0.12, 0.09, 0.09, dot)
    txt(slide, value, x + 0.22, y, w - 0.22, h, size, fill, valign=MSO_ANCHOR.TOP)


def notes(slide, duration, body):
    slide.notes_slide.notes_text_frame.text = f"DURÉE : {duration}\n\n{body.strip()}"


prs = Presentation()
prs.slide_width = Inches(SW)
prs.slide_height = Inches(SH)
prs.core_properties.title = "Vision CLIP dans IA-TOS | Brief 2"
prs.core_properties.subject = "Présentation technique de 10 minutes aux couleurs Atos"
prs.core_properties.author = "Formation IA-TOS"
prs.core_properties.keywords = "Atos, Vision CLIP, Transformers, FastAPI, Docker"


# 1. Cover: official Deep Blue and Curves of Progress composition.
slide = prs.slides.add_slide(prs.slide_layouts[6])
slide.shapes.add_picture(str(CURVE_COVER), 0, 0, width=Inches(SW), height=Inches(SH))
add_logo(slide, white=True, x=0.80, y=0.58, width=1.20)
txt(slide, "BRIEF 2  /  SUJET 4", 0.84, 1.58, 3.2, 0.30, 11, LIGHT, True)
txt(slide, "Du document\nau classement", 0.80, 2.08, 7.10, 1.58, 36, WHITE, True, valign=MSO_ANCHOR.TOP)
txt(slide, "Intégrer Vision CLIP dans la plateforme", 0.84, 4.02, 6.6, 0.42, 18, WHITE, True)
txt(slide, "API  ·  Transformers  ·  Docker", 0.84, 4.60, 6.2, 0.34, 14, LIGHT)
txt(slide, "Présentation technique  /  10 minutes", 0.84, 6.47, 5.2, 0.28, 10, WHITE)
notes(slide, "0:30", "Présenter le sujet : intégrer une classification zero-shot de pièces justificatives dans la plateforme. Annoncer le parcours : rappeler l'API existante, expliquer précisément le chargement du modèle avec Transformers, puis montrer l'organisation Docker. Indiquer dès le début que l'application et le modèle ont été essayés en local, mais que l'image Docker n'a pas encore été construite.")


# 2. API architecture recap.
slide = content_slide("Le socle applicatif sépare l'interface du modèle", "01  /  RAPPEL API", 2)
txt(slide, "Une seule API relie les pages Streamlit aux services métier.", 0.80, 1.92, 9.0, 0.42, 17, DEEP, True)
blocks = [
    (0.84, BLUE_10, "Interface", "Streamlit", "Upload et restitution"),
    (4.72, LIGHT_10, "Contrat HTTP", "FastAPI", "Validation et orchestration"),
    (8.60, WHITE, "Services métier", "iatos_core", "Scoring · Sentiment · Vision"),
]
for x, fill, eyebrow, heading, body in blocks:
    rect(slide, x, 2.70, 3.12, 1.68, fill, border=DEEP_20 if fill == WHITE else None)
    txt(slide, eyebrow, x + 0.22, 2.91, 2.60, 0.26, 10, BLUE, True)
    txt(slide, heading, x + 0.22, 3.28, 2.68, 0.42, 21, DEEP, True)
    txt(slide, body, x + 0.22, 3.82, 2.70, 0.30, 11, DEEP_70)
chevron(slide, 4.13, 3.31)
chevron(slide, 8.00, 3.31)
rect(slide, 0.85, 4.90, 11.15, 0.96, DEEP)
txt(slide, "POST", 1.10, 5.12, 0.72, 0.30, 13, LIGHT, True, font="Consolas")
txt(slide, "/vision/classify-document", 1.95, 5.10, 4.12, 0.34, 14, WHITE, True, font="Consolas")
txt(slide, "multipart/form-data  →  réponse Pydantic", 6.35, 5.13, 5.25, 0.28, 12, WHITE)
txt(slide, "Streamlit ne charge pas CLIP : il transmet l'image au backend.", 0.87, 6.19, 9.2, 0.34, 13, DEEP_70)
notes(slide, "1:15", "Rappeler le premier travail. Streamlit présente l'interface et envoie des requêtes HTTP. FastAPI porte les routes et les contrats Pydantic. Les algorithmes et modèles sont regroupés dans iatos_core. Le nouvel endpoint reste dans le backend : le front ne connaît ni Transformers ni le modèle. Le fichier image est envoyé en multipart/form-data, puis la réponse JSON typée revient à Streamlit.")


# 3. Request/response contract and validation.
slide = content_slide("L'endpoint reçoit un fichier et renvoie un classement", "01  /  CONTRAT HTTP", 3)
rect(slide, 0.84, 2.05, 5.36, 3.64, DEEP)
txt(slide, "ENTRÉE  /  multipart/form-data", 1.12, 2.29, 4.8, 0.30, 10, LIGHT, True)
txt(slide, "file: UploadFile\nlabels: list[str]", 1.12, 2.83, 4.7, 0.90, 18, WHITE, True, font="Consolas", valign=MSO_ANCHOR.TOP)
txt(slide, "JPEG / PNG  ·  5 Mio maximum\n2 à 20 catégories distinctes\n16 millions de pixels maximum", 1.12, 4.12, 4.63, 1.02, 13, DEEP_10, valign=MSO_ANCHOR.TOP)
rect(slide, 6.70, 2.05, 5.50, 3.64, BLUE_10)
txt(slide, "SORTIE  /  200", 6.98, 2.29, 4.8, 0.30, 10, BLUE, True)
txt(slide, '{\n  "filename": "specimen_identity_fr.png",\n  "detected_document": "identity card",\n  "confidence": 0.994,\n  "candidates": [...]\n}',
    6.98, 2.78, 4.88, 2.20, 11, DEEP, font="Consolas", valign=MSO_ANCHOR.TOP)
rect(slide, 6.98, 5.16, 2.14, 0.34, WHITE, border=DEEP_20)
txt(slide, "Entrée invalide : 422", 7.10, 5.18, 1.92, 0.28, 10, DEEP, True)
txt(slide, "Le type MIME annoncé ne suffit pas : Pillow vérifie aussi le contenu réel.", 0.88, 6.10, 11.0, 0.36, 12, DEEP_70)
notes(slide, "1:00", "Présenter le contrat sans lire chaque champ. La route accepte le fichier et les libellés en multipart. Les schémas de réponse exposent le label principal, le score et la distribution complète. Le service vérifie le contenu réellement décodé, la taille et les dimensions, et renvoie un 422 si l'entrée est invalide. Les libellés sont transmis individuellement, y compris depuis Swagger grâce à l'encodage OpenAPI configuré.")


# 4. CLIP zero-shot concept.
slide = content_slide("CLIP compare une image aux libellés proposés", "02  /  VISION CLIP", 4)
txt(slide, "Un modèle vision-langage préentraîné. Aucun entraînement supplémentaire.", 0.83, 1.93, 10.3, 0.38, 15, DEEP_70, True)
rect(slide, 0.87, 2.66, 3.15, 2.66, WHITE, border=DEEP_20)
if SPECIMEN.exists():
    slide.shapes.add_picture(str(SPECIMEN), Inches(1.11), Inches(2.94), width=Inches(2.66), height=Inches(1.69))
txt(slide, "Image d'un spécimen", 1.10, 4.82, 2.68, 0.28, 10, DEEP_70, True)
chevron(slide, 4.24, 3.64, 0.34, 0.54)
rect(slide, 4.81, 2.66, 3.20, 2.66, DEEP)
txt(slide, "CLIP", 5.18, 3.03, 2.50, 0.50, 27, WHITE, True, align=PP_ALIGN.CENTER)
txt(slide, "Encodeur image\n+ encodeur texte", 5.18, 3.77, 2.50, 0.76, 17, LIGHT, True, align=PP_ALIGN.CENTER)
txt(slide, "similarité sémantique", 5.17, 4.74, 2.53, 0.30, 11, DEEP_10, align=PP_ALIGN.CENTER)
chevron(slide, 8.22, 3.64, 0.34, 0.54)
txt(slide, "Candidats", 8.96, 2.72, 2.8, 0.34, 12, BLUE, True)
for i, candidate in enumerate(["identity card", "bank statement", "bank check", "blank paper"]):
    yy = 3.18 + i * 0.51
    rect(slide, 8.96, yy, 2.96, 0.37, LIGHT_10 if i == 0 else WHITE, border=DEEP_20 if i else None)
    txt(slide, candidate, 9.12, yy + 0.035, 2.62, 0.29, 11, DEEP, i == 0)
rect(slide, 0.87, 5.78, 11.05, 0.55, LIGHT_10)
txt(slide, "Classement de type de document. Pas d'OCR, d'authentification ou de validation administrative.",
    1.08, 5.88, 10.61, 0.32, 12, DEEP, True, align=PP_ALIGN.CENTER)
notes(slide, "1:05", "Expliquer le zero-shot. CLIP rapproche les représentations de l'image et des descriptions candidates. On choisit les catégories au moment de la requête, sans réentraîner. Il n'extrait pas le texte de la pièce et ne vérifie pas son authenticité. La famille de catégories et le wording des libellés influencent le classement.")


# 5. Hidden loading path in Transformers.
slide = content_slide("Le constructeur déclenche le chargement via pipeline", "02  /  TRANSFORMERS", 5)
rect(slide, 0.85, 2.06, 5.10, 3.78, DEEP)
txt(slide, "DocumentClassifier.__init__", 1.10, 2.31, 4.54, 0.34, 13, LIGHT, True, font="Consolas")
txt(slide, 'pipeline(\n  "zero-shot-image-classification",\n  model="openai/clip-vit-base-patch32",\n  device=-1\n)',
    1.10, 2.87, 4.56, 1.78, 12, WHITE, font="Consolas", valign=MSO_ANCHOR.TOP)
txt(slide, "L'appel existe, le téléchargement est délégué.", 1.10, 5.18, 4.48, 0.40, 12, LIGHT, True)
txt(slide, "CHAÎNE INTERNE", 6.48, 2.12, 2.25, 0.28, 10, BLUE, True)
steps = [
    (2.57, "pipeline(...)", "fabrique le pipeline"),
    (3.31, "model_class.from_pretrained(...)", "charge les poids et la configuration"),
    (4.05, "AutoImageProcessor.from_pretrained(...)", "charge le préprocesseur image"),
]
for i, (yy, title, detail) in enumerate(steps):
    rect(slide, 6.47, yy, 5.27, 0.57, BLUE_10 if i != 1 else LIGHT_10)
    txt(slide, title, 6.68, yy + 0.07, 4.84, 0.24, 10, DEEP, True, font="Consolas")
    txt(slide, detail, 6.68, yy + 0.33, 4.84, 0.19, 9, DEEP_70)
    if i < 2:
        rect(slide, 6.73, yy + 0.60, 0.035, 0.14, BLUE)
rect(slide, 6.47, 5.14, 5.27, 0.68, DEEP)
txt(slide, "Cache présent : lecture locale", 6.69, 5.25, 4.84, 0.22, 11, WHITE, True)
txt(slide, "Cache absent : Hugging Face Hub", 6.69, 5.51, 4.84, 0.20, 10, LIGHT)
notes(slide, "1:20", "C'est le point clé pour expliquer le téléchargement. Le constructeur n'appelle pas une méthode nommée download. `pipeline` est une fonction fabrique de Transformers. Dans la version installée, elle résout la configuration et appelle indirectement `model_class.from_pretrained`, puis `AutoImageProcessor.from_pretrained`. Ces méthodes consultent le cache et téléchargent les fichiers manquants du Hub. L'objet pipeline complet est ensuite stocké dans `self._classifier`. Lors d'un cache hit, les poids ne sont pas téléchargés de nouveau.")


# 6. Lifecycle and observed model output.
slide = content_slide("Une instance en mémoire, des résultats qui varient selon l'image", "02  /  CHARGEMENT ET RÉSULTATS", 6)
rect(slide, 0.87, 2.10, 3.24, 3.62, DEEP)
txt(slide, "Au démarrage", 1.14, 2.40, 2.60, 0.34, 16, WHITE, True)
txt(slide, "lifespan\n  → DocumentClassifier()\n  → pipeline en RAM", 1.14, 2.98, 2.62, 1.32, 12, LIGHT, font="Consolas", valign=MSO_ANCHOR.TOP)
txt(slide, "Une instance par processus FastAPI.", 1.14, 4.76, 2.60, 0.57, 11, WHITE, True)
txt(slide, "Essais CPU observés", 4.59, 2.12, 3.5, 0.34, 15, DEEP, True)
txt(slide, "Spécimen de carte d'identité", 4.59, 2.67, 5.3, 0.26, 10, DEEP_70, True)

def score_row(slide, y, label, score, fill=BLUE):
    txt(slide, label, 4.61, y, 1.67, 0.25, 10, DEEP)
    rect(slide, 6.36, y + 0.035, 2.65, 0.15, DEEP_10)
    if score > 0:
        rect(slide, 6.36, y + 0.035, max(0.04, 2.65 * score), 0.15, fill, border=WHITE, border_width=0.5)
    txt(slide, f"{score:.1%}", 9.18, y - 0.01, 0.83, 0.26, 10, DEEP, True)

score_row(slide, 3.02, "identity card", 0.9939, DEEP)
score_row(slide, 3.39, "bank check", 0.0054, BLUE)
txt(slide, "Page blanche synthétique", 4.59, 4.10, 5.3, 0.26, 10, DEEP_70, True)
score_row(slide, 4.47, "blank paper", 0.4748, DEEP)
score_row(slide, 4.84, "bank statement", 0.4192, BLUE)
rect(slide, 10.20, 2.72, 2.18, 2.55, ORANGE_20)
txt(slide, "À vérifier", 10.43, 3.01, 1.72, 0.35, 16, DEEP, True)
txt(slide, "Les deux meilleurs scores sont proches. Le classement reste relatif.",
    10.43, 3.55, 1.70, 1.12, 10, DEEP, valign=MSO_ANCHOR.TOP)
txt(slide, "0,38 s observé sur une image 400 × 500. Un essai, pas un benchmark.",
    4.61, 5.58, 7.44, 0.30, 10, DEEP_70)
notes(slide, "1:15", "Présenter le cycle de vie. Le lifespan instancie le service une fois au démarrage ; chaque requête réutilise le pipeline en mémoire. Un processus supplémentaire ferait sa propre copie. Sur le spécimen Wikimedia, identity card ressort à 99,4 %. Sur une image blanche, blank paper et bank statement sont proches, environ 47,5 % et 41,9 %. Ce contraste montre qu'un bon exemple ne démontre pas une fiabilité générale. Le temps de 0,38 seconde est une seule mesure CPU.")


# 7. Limits, model age and alternatives.
slide = content_slide("Un score élevé n'est pas une preuve de fiabilité", "02  /  LIMITES ET ALTERNATIVES", 7)
rect(slide, 0.87, 2.10, 3.03, 2.68, DEEP)
txt(slide, "Janvier 2021", 1.16, 2.44, 2.42, 0.44, 21, WHITE, True)
txt(slide, "CLIP ViT-B/32", 1.16, 3.08, 2.42, 0.38, 15, LIGHT, True)
txt(slide, "Modèle généraliste, non validé pour nos pièces.", 1.16, 3.73, 2.33, 0.66, 12, WHITE)
rect(slide, 4.30, 2.10, 3.35, 2.68, BLUE_10)
txt(slide, "Février 2025", 4.60, 2.44, 2.72, 0.40, 19, DEEP, True)
txt(slide, "SigLIP 2 Base", 4.60, 3.08, 2.72, 0.36, 15, BLUE, True)
txt(slide, "Alternative à comparer, pas un gain démontré sur ces documents.",
    4.60, 3.66, 2.72, 0.70, 11, DEEP)
txt(slide, "Scores différents", 8.14, 2.15, 3.40, 0.36, 16, DEEP, True)
square_bullet(slide, "CLIP : softmax, somme des candidats = 1.", 8.16, 2.79, 4.20, 12, DEEP, BLUE, 0.48)
square_bullet(slide, "SigLIP 2 : sigmoid, somme non contrainte.", 8.16, 3.48, 4.20, 12, DEEP, LIGHT, 0.48)
square_bullet(slide, "Seuils à réévaluer après tout changement de modèle.", 8.16, 4.17, 4.20, 12, DEEP, BLUE, 0.60)
rect(slide, 0.88, 5.25, 11.32, 0.65, LIGHT_10)
txt(slide, "Fiabilité métier : à mesurer sur un jeu représentatif, pas à déduire du score CLIP.",
    1.10, 5.38, 10.88, 0.34, 12, DEEP, True, align=PP_ALIGN.CENTER)
notes(slide, "1:00", "CLIP ViT-B/32 est daté de janvier 2021. SigLIP 2 est plus récent, mais nous ne l'avons pas testé sur nos spécimens. Il ne faut pas le qualifier de plus fiable pour nos pièces sans une comparaison dédiée. Attention aussi à la sémantique : CLIP normalise avec softmax ; SigLIP utilise des scores sigmoid. Leurs seuils ne se transfèrent pas automatiquement. La fiche du modèle demande de tester le contexte cible.")


# 8. Docker timing, cache and control.
slide = content_slide("Docker installe les bibliothèques au build, CLIP au démarrage", "03  /  DOCKER", 8)
phases = [
    (0.88, "Build de l'image", "uv sync --locked --no-dev\nNLTK VADER", BLUE_10),
    (4.67, "Démarrage du conteneur", "FastAPI lifespan\nDocumentClassifier → pipeline", LIGHT_10),
    (8.46, "Volume persistant", "HF_HOME\n/app/.cache/huggingface", WHITE),
]
for x, heading, body, fill in phases:
    rect(slide, x, 2.28, 3.25, 1.64, fill, border=DEEP_20 if fill == WHITE else None)
    txt(slide, heading, x + 0.22, 2.51, 2.78, 0.38, 14, DEEP, True)
    txt(slide, body, x + 0.22, 3.05, 2.78, 0.66, 11, DEEP, font="Consolas", valign=MSO_ANCHOR.TOP)
chevron(slide, 4.22, 2.87, 0.27, 0.48)
chevron(slide, 8.02, 2.87, 0.27, 0.48)
txt(slide, "Cache vide", 4.93, 4.28, 1.50, 0.28, 10, BLUE, True)
txt(slide, "→ Hub Hugging Face", 6.42, 4.28, 2.10, 0.28, 10, DEEP)
txt(slide, "Cache présent", 4.93, 4.74, 1.50, 0.28, 10, BLUE, True)
txt(slide, "→ lecture locale, puis RAM", 6.42, 4.74, 2.70, 0.28, 10, DEEP)
rect(slide, 9.35, 4.19, 2.30, 0.94, BLUE_10)
txt(slide, "Révision et\nmode hors ligne", 9.56, 4.36, 1.92, 0.54, 11, DEEP, True)
txt(slide, "Configurables, mais non activés actuellement.", 9.35, 5.21, 2.82, 0.34, 9, DEEP_70)
rect(slide, 0.88, 5.74, 11.26, 0.62, ORANGE_20)
txt(slide, "Compose validé. Build Docker non vérifié : moteur Docker indisponible lors des essais.",
    1.08, 5.88, 10.85, 0.33, 11, DEEP, True, align=PP_ALIGN.CENTER)
notes(slide, "1:15", "Distinguer ce qui est téléchargé et à quel moment. Au build, uv installe Transformers et PyTorch CPU ; le Dockerfile télécharge le lexique NLTK. Au démarrage, le lifespan appelle pipeline. Si le volume Hugging Face est vide, le Hub fournit les poids et le processeur. Le volume nommé persiste le cache entre recréations. HF_HOME et le stockage sont configurés ; la révision n'est pas épinglée et le mode local_files_only n'est pas activé. Docker Compose a été analysé, mais aucun build réel n'a été exécuté faute de daemon.")


# 9. Hexagonal architecture: proposal only.
slide = content_slide("Le prochain découplage peut suivre l'architecture hexagonale", "04  /  ÉVOLUTION PROPOSÉE", 9)
txt(slide, "Aujourd'hui, la route Vision référence directement DocumentClassifier.", 0.88, 1.94, 10.2, 0.35, 14, DEEP_70)
rect(slide, 0.91, 2.72, 2.70, 1.24, BLUE_10)
txt(slide, "Adaptateur entrant", 1.13, 2.94, 2.25, 0.29, 11, BLUE, True)
txt(slide, "Route FastAPI", 1.13, 3.35, 2.25, 0.30, 15, DEEP, True)
chevron(slide, 3.80, 3.12, 0.27, 0.46)
rect(slide, 4.22, 2.72, 2.72, 1.24, DEEP)
txt(slide, "Application", 4.45, 2.94, 2.25, 0.29, 11, LIGHT, True)
txt(slide, "Cas d'usage", 4.45, 3.35, 2.25, 0.30, 15, WHITE, True)
chevron(slide, 7.08, 3.12, 0.27, 0.46)
rect(slide, 7.51, 2.72, 2.12, 1.24, LIGHT_10)
txt(slide, "Port", 7.73, 2.94, 1.68, 0.29, 11, BLUE, True)
txt(slide, "Protocol", 7.73, 3.35, 1.68, 0.30, 15, DEEP, True)
rect(slide, 10.14, 2.72, 2.18, 1.24, WHITE, border=DEEP_20)
txt(slide, "Adaptateur sortant", 10.35, 2.94, 1.72, 0.29, 10, BLUE, True)
txt(slide, "Transformers", 10.35, 3.35, 1.72, 0.30, 13, DEEP, True)
line = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(9.68), Inches(3.35), Inches(10.08), Inches(3.35))
line.line.color.rgb = rgb(BLUE)
line.line.width = Pt(1.5)
rect(slide, 0.92, 4.55, 5.52, 1.08, WHITE, border=DEEP_20)
txt(slide, "Portefeuille de tests", 1.18, 4.75, 2.45, 0.26, 10, BLUE, True)
txt(slide, "Cas d'usage testé avec un faux port, sans FastAPI ni modèle.",
    1.18, 5.10, 4.95, 0.32, 11, DEEP)
rect(slide, 6.79, 4.55, 5.52, 1.08, ORANGE_20)
txt(slide, "Statut", 7.05, 4.75, 1.15, 0.26, 10, DEEP, True)
txt(slide, "Cible proposée. Aucun refactoring réalisé.", 7.05, 5.10, 4.95, 0.32, 11, DEEP)
notes(slide, "0:55", "Présenter cette architecture comme une évolution et non comme un résultat actuel. Aujourd'hui la route importe le classificateur concret. Une cible légère : route FastAPI, cas d'usage, port défini par Protocol, adaptateur Transformers. Le lifespan assemble les objets et les injecte. Cela permettrait de tester le cas d'usage sans charger FastAPI ni CLIP, et de remplacer l'adaptateur sans modifier le contrat HTTP. Aucun refactoring n'a été fait.")


# 10. Closing and verified status.
slide = prs.slides.add_slide(prs.slide_layouts[6])
slide.shapes.add_picture(str(CURVE_COVER), 0, 0, width=Inches(SW), height=Inches(SH))
add_logo(slide, white=True, x=0.80, y=0.53, width=1.12)
txt(slide, "Ce qui est démontré", 0.84, 1.54, 6.4, 0.52, 27, WHITE, True)
txt(slide, "45", 0.86, 2.44, 1.72, 0.92, 44, WHITE, True)
txt(slide, "tests automatisés réussis", 0.92, 3.39, 3.45, 0.34, 13, LIGHT, True)
txt(slide, "99,4 %", 4.30, 2.44, 2.35, 0.92, 38, WHITE, True)
txt(slide, "score relatif sur un spécimen", 4.36, 3.39, 3.55, 0.34, 12, LIGHT, True)
rect(slide, 8.73, 2.02, 3.08, 2.06, DEEP)
txt(slide, "À retenir", 9.03, 2.35, 2.50, 0.36, 16, WHITE, True)
txt(slide, "Type reconnu\n≠ document authentique", 9.03, 2.94, 2.50, 0.70, 15, LIGHT, True)
txt(slide, "Prochaine étape : construire Docker et mesurer le cache en situation réelle.",
    0.88, 5.16, 7.55, 0.70, 14, WHITE, True)
txt(slide, "Merci", 0.88, 6.30, 2.0, 0.34, 12, LIGHT, True)
notes(slide, "0:25", "Conclure : 45 tests passent et le parcours local a été démontré. Le score élevé concerne un seul spécimen, pas une garantie. La prochaine étape est de valider le build Docker et la persistance du volume. Remercier l'auditoire et ouvrir aux questions.")


prs.save(OUTPUT)

durations = []
out_of_bounds = []
for number, slide in enumerate(prs.slides, start=1):
    note = slide.notes_slide.notes_text_frame.text
    match = re.search(r"DURÉE : (\d+):(\d+)", note)
    durations.append(int(match.group(1)) * 60 + int(match.group(2)) if match else 0)
    for shape in slide.shapes:
        if shape.left < 0 or shape.top < 0 or shape.left + shape.width > prs.slide_width + 1000 or shape.top + shape.height > prs.slide_height + 1000:
            out_of_bounds.append((number, shape.name))

svg_media = [name for name in zipfile.ZipFile(OUTPUT).namelist() if name.startswith("ppt/media/") and name.endswith(".svg")]
print(f"Created {OUTPUT}")
print(f"Slides: {len(prs.slides)}; duration: {sum(durations)}s; notes: {sum(bool(s.notes_slide.notes_text_frame.text.strip()) for s in prs.slides)}/10")
print(f"Out of bounds: {out_of_bounds}; embedded SVG assets: {len(svg_media)}")
assert len(prs.slides) == 10
assert sum(durations) == 600
assert all(durations)
assert not out_of_bounds
assert len(svg_media) >= 3