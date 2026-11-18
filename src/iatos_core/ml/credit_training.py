"""Pipeline factories and financial features for the scoring experiments."""

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, clone
from sklearn.compose import ColumnTransformer, make_column_selector
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler


def add_business_features(data: pd.DataFrame) -> pd.DataFrame:
    """Estimate disposable income excluding interest, insurance and living costs."""
    result = data.copy()
    duration = result["duree_mois"].where(result["duree_mois"] > 0)
    amount = result["montant_demande"].where(result["montant_demande"] > 0)
    result["reste_a_vivre_estime"] = (
        result["revenu_mensuel"] - result["montant_demande"] / duration
    )
    result["ratio_epargne_emprunt"] = result["epargne_globale"] / amount
    return result


def normalize_missing_categories(data: pd.DataFrame) -> pd.DataFrame:
    """Normalize pandas string missing values for SimpleImputer."""
    result = data.copy()
    columns = result.select_dtypes(exclude="number").columns
    for column in columns:
        result[column] = result[column].astype(object).where(
            result[column].notna(), np.nan
        )
    return result


def build_scoring_pipeline(
    estimator: BaseEstimator, *, business_features: bool = True
) -> Pipeline:
    numeric = Pipeline([
        ("imputation", SimpleImputer(strategy="median")),
        ("standardisation", StandardScaler()),
    ])
    categorical = Pipeline([
        ("imputation", SimpleImputer(strategy="constant", fill_value="INCONNU")),
        ("encodage", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    preprocessing = ColumnTransformer([
        ("numerique", numeric, make_column_selector(dtype_include="number")),
        ("categorielle", categorical, make_column_selector(dtype_exclude="number")),
    ])
    return Pipeline([
        ("variables_metier", FunctionTransformer(add_business_features)
         if business_features else "passthrough"),
        ("valeurs_manquantes", FunctionTransformer(normalize_missing_categories)),
        ("pretraitement", preprocessing),
        ("modele", clone(estimator)),
    ])
