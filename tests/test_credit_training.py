"""Check the scoring pipelines' raw input and serialization contract."""

import subprocess
import sys

import joblib
import numpy as np
import pandas as pd
import pytest
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

from iatos_core.ml.credit_training import (
    add_business_features,
    build_scoring_pipeline,
)


def test_business_features_invalid_denominators():
    data = pd.DataFrame({
        "montant_demande": [12000.0, 0.0, -1.0, np.nan],
        "duree_mois": [24.0, 0.0, -1.0, np.nan],
        "revenu_mensuel": [3000.0] * 4,
        "epargne_globale": [6000.0] * 4,
    })
    result = add_business_features(data)
    assert result.loc[0, "reste_a_vivre_estime"] == 2500.0
    assert result.loc[0, "ratio_epargne_emprunt"] == 0.5
    assert result.loc[1:, ["reste_a_vivre_estime", "ratio_epargne_emprunt"]].isna().all().all()
    assert "reste_a_vivre_estime" not in data
    assert len(result) == len(data)


@pytest.mark.parametrize("classification", [False, True])
def test_pipeline_unknown_missing_and_fresh_process(tmp_path, classification):
    data = pd.DataFrame({
        "montant_demande": [12000.0, 1000.0, 8000.0, 20000.0, 6000.0, 4000.0],
        "duree_mois": [24, 12, 36, 48, 24, 12],
        "revenu_mensuel": [3000.0, 1500.0, 2000.0, 4000.0, 2500.0, 2800.0],
        "epargne_globale": [6000.0, 500.0, 800.0, 1000.0, 2000.0, 3000.0],
        "type_contrat": ["CDI", "CDD", "CDI", "CDD", "CDI", "CDI"],
    })
    estimator = (
        RandomForestClassifier(n_estimators=5, random_state=42)
        if classification else RandomForestRegressor(n_estimators=5, random_state=42)
    )
    target = [0, 1, 0, 1, 0, 1] if classification else [600, 500, 550, 650, 620, 630]
    pipeline = build_scoring_pipeline(estimator).fit(data, target)
    probe = data.iloc[:3].copy()
    probe.loc[probe.index[0], "type_contrat"] = "NOUVEAU_CONTRAT"
    probe.loc[probe.index[1], "type_contrat"] = pd.NA
    probe.loc[probe.index[2], "revenu_mensuel"] = np.nan
    probe.loc[probe.index[2], "duree_mois"] = 0
    expected = pipeline.predict(probe)
    assert expected.shape == (3,)
    assert np.isfinite(expected).all()
    if classification:
        probabilities = pipeline.predict_proba(probe)
        assert probabilities.shape == (3, 2)
        np.testing.assert_allclose(probabilities.sum(axis=1), 1)
    bundle_path = tmp_path / "pipeline.joblib"
    input_path = tmp_path / "input.joblib"
    output_path = tmp_path / "predictions.joblib"
    joblib.dump(pipeline, bundle_path)
    joblib.dump(probe, input_path)
    subprocess.run(
        [
            sys.executable, "-c",
            "import joblib, sys; "
            "model = joblib.load(sys.argv[1]); "
            "data = joblib.load(sys.argv[2]); "
            "joblib.dump(model.predict(data), sys.argv[3])",
            str(bundle_path), str(input_path), str(output_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    np.testing.assert_allclose(joblib.load(output_path), expected)
