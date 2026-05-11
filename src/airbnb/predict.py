"""Prediction helpers — load a saved model and score new data.

This module is intentionally lightweight so it can be imported by
downstream APIs (FastAPI, Flask, Streamlit, …) without pulling in
the entire training pipeline.
"""

from __future__ import annotations

import logging
from typing import Any

import joblib
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------

def load_model(path: str) -> Any:
    """Load a serialised model from disk.

    Parameters
    ----------
    path:
        Path created by :func:`train.save_model` (``.joblib``).

    Returns
    -------
    Any
        Deserialised model object with a ``.predict()`` method.
    """
    logger.info("Loading model from %s", path)
    model = joblib.load(path)
    logger.info("Model loaded successfully.")
    return model


# ---------------------------------------------------------------------------
# Single-sample preprocessing
# ---------------------------------------------------------------------------

def preprocess_input(
    input_data: dict,
    feature_names: list[str],
    config: dict,
) -> pd.DataFrame:
    """Transform a single raw listing dict into a model-ready DataFrame.

    The function mirrors the cleaning / engineering / encoding pipeline
    applied during training so that the feature columns match exactly.

    .. note::
        This is a **minimal** implementation suitable for demos and
        tutorials.  In production you would want a more robust pipeline
        (e.g. ``sklearn.pipeline.Pipeline``) that guarantees consistency.

    Parameters
    ----------
    input_data:
        Dictionary of raw listing attributes (column → value).
    feature_names:
        Ordered list of feature columns expected by the model.
    config:
        Project configuration.

    Returns
    -------
    pd.DataFrame
        A single-row DataFrame whose columns match *feature_names*.
    """
    df = pd.DataFrame([input_data])

    # Parse host_response_rate
    if "host_response_rate" in df.columns:
        df["host_response_rate"] = (
            df["host_response_rate"]
            .astype(str)
            .str.replace("%", "", regex=False)
            .replace("nan", np.nan)
        )

    # Boolean columns
    for col in config.get("features", {}).get("boolean_columns", []):
        if col in df.columns:
            df[col] = df[col].map(
                {"t": True, "f": False, True: True, False: False}
            )

    # Align columns — missing features get 0, extra features dropped
    for feat in feature_names:
        if feat not in df.columns:
            df[feat] = 0
    df = df[feature_names]

    return df


# ---------------------------------------------------------------------------
# Prediction
# ---------------------------------------------------------------------------

def predict(model: Any, processed_data: pd.DataFrame) -> float:
    """Return the predicted price for a single sample.

    Parameters
    ----------
    model:
        Fitted regressor.
    processed_data:
        Single-row DataFrame (from :func:`preprocess_input`).

    Returns
    -------
    float
        Predicted target value.
    """
    pred = model.predict(processed_data)
    return float(pred[0])


def predict_batch(model: Any, processed_data: pd.DataFrame) -> np.ndarray:
    """Return predictions for multiple samples.

    Parameters
    ----------
    model:
        Fitted regressor.
    processed_data:
        DataFrame with one or more rows.

    Returns
    -------
    np.ndarray
        Array of predicted values.
    """
    preds = model.predict(processed_data)
    return preds
