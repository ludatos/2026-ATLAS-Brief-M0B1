"""Classification zero-shot de documents avec CLIP sur CPU."""

from io import BytesIO
from typing import TypedDict
import warnings

from PIL import Image, ImageOps, UnidentifiedImageError
from transformers import pipeline

from iatos_core.logger import logger


MAX_IMAGE_BYTES = 5 * 1024 * 1024
MAX_IMAGE_PIXELS = 16_000_000
MODEL_ID = "openai/clip-vit-base-patch32"
DEFAULT_LABELS = ("identity card", "bank statement", "bank check", "blank paper")


class DocumentScore(TypedDict):
    label: str
    score: float


class InvalidDocumentError(ValueError):
    """Image ou categories incompatibles avec la classification."""


class DocumentClassifier:
    """Charge une instance CLIP et la reutilise pour les classifications."""

    def __init__(self) -> None:
        logger.info("Chargement de CLIP sur CPU : {model}", model=MODEL_ID)
        self._classifier = pipeline(
            "zero-shot-image-classification",
            model=MODEL_ID,
            device=-1,
        )
        logger.success("CLIP pret sur CPU")

    def classify(self, content: bytes, labels: list[str]) -> list[DocumentScore]:
        """Valide l'image en memoire et retourne les scores decroissants."""
        labels = [label.strip() for label in labels]
        if not 2 <= len(labels) <= 20:
            raise InvalidDocumentError("Fournir entre 2 et 20 categories.")
        if any(not label or len(label) > 100 for label in labels):
            raise InvalidDocumentError("Chaque categorie doit contenir entre 1 et 100 caracteres.")
        if len({label.casefold() for label in labels}) != len(labels):
            raise InvalidDocumentError("Les categories doivent etre distinctes.")
        if not content or len(content) > MAX_IMAGE_BYTES:
            raise InvalidDocumentError("L'image doit contenir entre 1 octet et 5 Mio.")

        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error", Image.DecompressionBombWarning)
                with Image.open(BytesIO(content)) as source:
                    if source.format not in {"JPEG", "PNG"}:
                        raise InvalidDocumentError("Seules les images JPEG et PNG sont acceptees.")
                    if source.width * source.height > MAX_IMAGE_PIXELS:
                        raise InvalidDocumentError("L'image ne doit pas depasser 16 millions de pixels.")
                    source.verify()
                with Image.open(BytesIO(content)) as source:
                    image = ImageOps.exif_transpose(source).convert("RGB")
        except (UnidentifiedImageError, OSError, SyntaxError, Image.DecompressionBombError,
                Image.DecompressionBombWarning) as exc:
            raise InvalidDocumentError("Image illisible, corrompue ou trop grande.") from exc

        try:
            results = self._classifier(image, candidate_labels=labels)
        finally:
            image.close()
        return sorted(
            [{"label": item["label"], "score": float(item["score"])} for item in results],
            key=lambda item: item["score"],
            reverse=True,
        )