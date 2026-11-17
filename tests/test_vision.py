"""Tests CLIP sans reseau ni chargement de poids."""

from io import BytesIO
from unittest.mock import patch

from PIL import Image
import pytest

from iatos_core.ml.vision import DocumentClassifier, InvalidDocumentError, MAX_IMAGE_BYTES


def image_bytes(image_format: str = "PNG", mode: str = "RGB") -> bytes:
    with Image.new(mode, (32, 32), "white") as image:
        buffer = BytesIO()
        image.save(buffer, format=image_format)
        return buffer.getvalue()


@pytest.fixture
def classifier():
    with patch("iatos_core.ml.vision.pipeline") as load_pipeline:
        load_pipeline.return_value.return_value = [
            {"label": "identity card", "score": 0.1},
            {"label": "blank paper", "score": 0.9},
        ]
        yield DocumentClassifier(), load_pipeline


@pytest.mark.parametrize("image_format,mode", [("PNG", "RGBA"), ("JPEG", "RGB")])
def test_classification_reuses_cpu_pipeline(classifier, image_format, mode):
    service, load_pipeline = classifier
    for _ in range(2):
        result = service.classify(image_bytes(image_format, mode), ["identity card", "blank paper"])
        assert result[0] == {"label": "blank paper", "score": 0.9}
    load_pipeline.assert_called_once_with(
        "zero-shot-image-classification", model="openai/clip-vit-base-patch32", device=-1,
    )
    assert load_pipeline.return_value.call_count == 2
    assert load_pipeline.return_value.call_args.args[0].mode == "RGB"


@pytest.mark.parametrize("content", [b"", b"not an image", b"x" * (MAX_IMAGE_BYTES + 1)])
def test_invalid_image_never_runs_model(classifier, content):
    service, load_pipeline = classifier
    with pytest.raises(InvalidDocumentError):
        service.classify(content, ["identity card", "blank paper"])
    load_pipeline.return_value.assert_not_called()


def test_disallowed_format(classifier):
    service, _ = classifier
    with pytest.raises(InvalidDocumentError, match="JPEG et PNG"):
        service.classify(image_bytes("BMP"), ["identity card", "blank paper"])


@pytest.mark.parametrize("labels", [[], ["one"], ["a", " "], ["a", "A"], ["a", "b" * 101],
                                         [str(index) for index in range(21)]])
def test_invalid_categories(classifier, labels):
    service, load_pipeline = classifier
    with pytest.raises(InvalidDocumentError):
        service.classify(image_bytes(), labels)
    load_pipeline.return_value.assert_not_called()


def test_pixel_limit(classifier):
    service, load_pipeline = classifier
    with patch("iatos_core.ml.vision.MAX_IMAGE_PIXELS", 100):
        with pytest.raises(InvalidDocumentError, match="pixels"):
            service.classify(image_bytes(), ["identity card", "blank paper"])
    load_pipeline.return_value.assert_not_called()


def test_endpoint_document_success(client):
    response = client.post(
        "/vision/classify-document",
        files={"file": ("blank.png", image_bytes(), "image/png")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "blank.png"
    assert data["detected_document"] == "blank paper"
    assert data["confidence"] == 0.7
    assert len(data["candidates"]) == 4
    scores = [item["score"] for item in data["candidates"]]
    assert scores == sorted(scores, reverse=True)
    assert all(0 <= score <= 1 for score in scores)


def test_swagger_multipart_encoding(client):
    operation = client.get("/openapi.json").json()["paths"]["/vision/classify-document"]["post"]
    encoding = operation["requestBody"]["content"]["multipart/form-data"]["encoding"]
    assert encoding["labels"] == {"style": "form", "explode": True}


@pytest.mark.parametrize("content", [b"", b"not an image", b"x" * (MAX_IMAGE_BYTES + 1)])
def test_endpoint_invalid_document(client, content):
    response = client.post(
        "/vision/classify-document", files={"file": ("fake.png", content, "image/png")},
    )
    assert response.status_code == 422


def test_endpoint_missing_document(client):
    assert client.post("/vision/classify-document").status_code == 422


@pytest.mark.parametrize("labels", [["only one"], ["a", " "], ["a", "A"]])
def test_endpoint_invalid_categories(client, labels):
    response = client.post(
        "/vision/classify-document",
        files={"file": ("blank.png", image_bytes(), "image/png")},
        data={"labels": labels},
    )
    assert response.status_code == 422


def test_endpoint_custom_categories_and_reuse(client):
    import backend.main as backend

    with patch("iatos_core.ml.vision.pipeline") as load_pipeline:
        with patch.object(backend.document_classifier, "_classifier") as inference:
            inference.return_value = [
                {"label": "invoice", "score": 0.8}, {"label": "letter", "score": 0.2},
            ]
            for _ in range(2):
                response = client.post(
                    "/vision/classify-document",
                    files={"file": ("doc.jpg", image_bytes("JPEG"), "image/jpeg")},
                    data={"labels": ["invoice", "letter"]},
                )
                assert response.status_code == 200
                assert response.json()["detected_document"] == "invoice"
            assert inference.call_args.kwargs["candidate_labels"] == ["invoice", "letter"]
        load_pipeline.assert_not_called()


def test_endpoint_inference_error_is_generic(client):
    import backend.main as backend

    with patch.object(backend.document_classifier, "classify", side_effect=RuntimeError("private path")):
        response = client.post(
            "/vision/classify-document",
            files={"file": ("blank.png", image_bytes(), "image/png")},
        )
    assert response.status_code == 500
    assert "private path" not in response.text


def test_endpoint_unavailable(client, monkeypatch):
    monkeypatch.setattr("backend.main.document_classifier", None)
    response = client.post(
        "/vision/classify-document",
        files={"file": ("blank.png", image_bytes(), "image/png")},
    )
    assert response.status_code == 503


@pytest.mark.parametrize("score", [-0.1, 1.1, float("nan"), float("inf")])
def test_response_score_bounds(score):
    from pydantic import ValidationError
    from backend.schemas import DocumentClassScore

    with pytest.raises(ValidationError):
        DocumentClassScore(label="identity card", score=score)


@pytest.mark.parametrize("detected,score,status", [
    ("identity card", 0.8, "success"),
    ("blank paper", 0.8, "error"),
    ("blank paper", 0.45, "warning"),
])
def test_streamlit_result_states(detected, score, status):
    from pathlib import Path
    from unittest.mock import Mock
    from streamlit.testing.v1 import AppTest

    upload = Mock(name="upload")
    upload.name = "sample.png"
    upload.type = "image/png"
    upload.getvalue.return_value = image_bytes()
    other_label = "identity card" if detected == "blank paper" else "blank paper"
    response = Mock(status_code=200)
    response.json.return_value = {
        "filename": "sample.png", "detected_document": detected, "confidence": score,
        "candidates": [
            {"label": detected, "score": score},
            {"label": other_label, "score": 0.4 if score == 0.45 else 0.1},
            {"label": "bank statement", "score": 0.1 if score == 0.45 else 0.06},
            {"label": "bank check", "score": 0.05 if score == 0.45 else 0.04},
        ],
    }
    page = Path(__file__).resolve().parents[1] / "frontend" / "pages" / "03_Controle_Documents.py"
    with patch("streamlit.file_uploader", return_value=upload):
        with patch("requests.post", return_value=response) as post:
            app = AppTest.from_file(str(page), default_timeout=15).run()
            assert not app.exception
            app.button[0].click().run()
            assert not app.exception
            assert len(getattr(app, status)) == 1
            assert app.metric[1].value == f"{score:.1%}"
            post.assert_called_once()
            app.sidebar.slider[0].set_value(0.95).run()
            assert not app.exception
            assert len(app.warning) == 1
            post.assert_called_once()