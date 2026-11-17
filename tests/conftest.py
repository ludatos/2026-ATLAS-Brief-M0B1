"""Configuration et fixtures pytest."""

import sys
from pathlib import Path
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient

# Injecter la racine du projet et le dossier src dans sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"

for path in [str(PROJECT_ROOT), str(SRC_DIR)]:
    if path not in sys.path:
        sys.path.insert(0, path)

from backend.main import app


@pytest.fixture(scope="session")
def client():
    """Fixture retournant un client de test FastAPI."""
    with patch("iatos_core.ml.vision.pipeline") as load_pipeline:
        load_pipeline.return_value.return_value = [
            {"label": "blank paper", "score": 0.7},
            {"label": "bank statement", "score": 0.15},
            {"label": "identity card", "score": 0.1},
            {"label": "bank check", "score": 0.05},
        ]
        with TestClient(app) as test_client:
            yield test_client
