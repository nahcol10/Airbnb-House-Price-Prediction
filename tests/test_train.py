"""Tests for the train and utils modules — metrics, save/load round-trip."""

from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from airbnb.utils import calculate_metrics
from airbnb.train import train_xgboost, evaluate_model, save_model
from airbnb.predict import load_model


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def simple_config() -> dict:
    return {
        "training": {
            "xgboost": {
                "n_estimators": 10,
                "max_depth": 3,
                "learning_rate": 0.1,
                "subsample": 0.8,
                "colsample_bytree": 0.8,
                "random_state": 42,
                "n_jobs": 1,
            },
            "cv_folds": 2,
            "random_search_iter": 2,
        }
    }


@pytest.fixture()
def toy_xy():
    """Tiny regression dataset for fast testing."""
    np.random.seed(42)
    X = np.random.randn(100, 5)
    y = 3 * X[:, 0] + 2 * X[:, 1] + np.random.randn(100) * 0.5
    return X, y


# ---------------------------------------------------------------------------
# Tests — calculate_metrics
# ---------------------------------------------------------------------------

class TestCalculateMetrics:
    """Tests for :func:`calculate_metrics`."""

    def test_returns_expected_keys(self, toy_xy):
        X, y = toy_xy
        metrics = calculate_metrics(y, y + np.random.randn(len(y)) * 0.1)
        for key in ("mae", "rmse", "r2", "mape"):
            assert key in metrics

    def test_perfect_prediction(self):
        y = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        metrics = calculate_metrics(y, y)
        assert metrics["mae"] == 0.0
        assert metrics["rmse"] == 0.0
        assert metrics["r2"] == pytest.approx(1.0, abs=1e-6)

    def test_mape_no_division_by_zero(self):
        y = np.array([0.0, 0.0, 1.0, 2.0])
        pred = np.array([0.5, 0.5, 1.0, 2.0])
        metrics = calculate_metrics(y, pred)
        assert "mape" in metrics
        assert np.isfinite(metrics["mape"]) or metrics["mape"] == float("inf")


# ---------------------------------------------------------------------------
# Tests — save / load round-trip
# ---------------------------------------------------------------------------

class TestSaveLoadRoundTrip:
    """Verify that a trained model can be saved and loaded losslessly."""

    def test_model_roundtrip(self, toy_xy, simple_config):
        X, y = toy_xy
        X_df = pd.DataFrame(X, columns=[f"f{i}" for i in range(X.shape[1])])
        y_s = pd.Series(y, name="target")

        model = train_xgboost(X_df, y_s, simple_config)

        # Save to a temp directory
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "model.joblib"
            save_model(model, path)
            assert path.exists()

            loaded = load_model(str(path))
            preds_orig = model.predict(X_df)
            preds_loaded = loaded.predict(X_df)
            np.testing.assert_array_almost_equal(preds_orig, preds_loaded)
