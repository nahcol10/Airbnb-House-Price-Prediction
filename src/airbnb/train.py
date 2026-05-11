"""Model training, evaluation, hyper-parameter tuning, and artifact saving.

Centralises everything that touches an XGBoost (or compatible) estimator so
that ``main.py`` stays thin and each function can be tested in isolation.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import joblib
import matplotlib
matplotlib.use("Agg")  # non-interactive backend for headless environments
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import RandomizedSearchCV
from xgboost import XGBRegressor

from .utils import get_current_timestamp, save_json

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------

def train_xgboost(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    config: dict,
) -> XGBRegressor:
    """Train an XGBRegressor using parameters from *config*.

    Parameters
    ----------
    X_train:
        Training feature matrix.
    y_train:
        Training target vector.
    config:
        Full project configuration.

    Returns
    -------
    XGBRegressor
        Fitted model.
    """
    params = config.get("training", {}).get("xgboost", {})
    model = XGBRegressor(**params)
    logger.info("Training XGBoost with params: %s", params)
    model.fit(X_train, y_train)
    logger.info("Training complete.")
    return model


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def evaluate_model(
    model: Any,
    X: pd.DataFrame,
    y_true: pd.Series,
) -> dict[str, float]:
    """Compute regression metrics on a hold-out set.

    Parameters
    ----------
    model:
        Fitted regressor with a ``.predict()`` method.
    X:
        Feature matrix.
    y_true:
        Ground-truth target.

    Returns
    -------
    dict
        ``{"mae": …, "rmse": …, "r2": …}``
    """
    y_pred = model.predict(X)
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    metrics = {"mae": round(mae, 4), "rmse": round(rmse, 4), "r2": round(r2, 4)}
    logger.info("Evaluation metrics: %s", metrics)
    return metrics


# ---------------------------------------------------------------------------
# Hyper-parameter tuning
# ---------------------------------------------------------------------------

def tune_model(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    config: dict,
) -> XGBRegressor:
    """Run RandomizedSearchCV over XGBoost hyper-parameters.

    Parameters
    ----------
    X_train, y_train:
        Training data.
    config:
        Full project configuration (reads ``training.cv_folds``,
        ``training.random_search_iter``, and ``training.xgboost``).

    Returns
    -------
    XGBRegressor
        Best estimator found by the search.
    """
    train_cfg = config.get("training", {})
    base_params = train_cfg.get("xgboost", {})
    cv_folds = train_cfg.get("cv_folds", 5)
    n_iter = train_cfg.get("random_search_iter", 50)

    param_distributions = {
        "n_estimators": [200, 300, 500, 700, 1000],
        "max_depth": [3, 4, 5, 6, 8, 10],
        "learning_rate": [0.01, 0.05, 0.1, 0.2],
        "subsample": [0.6, 0.7, 0.8, 0.9, 1.0],
        "colsample_bytree": [0.6, 0.7, 0.8, 0.9, 1.0],
        "min_child_weight": [1, 3, 5, 7],
        "gamma": [0, 0.1, 0.2, 0.3],
        "reg_alpha": [0, 0.01, 0.1, 1],
        "reg_lambda": [1, 1.5, 2],
    }

    base_model = XGBRegressor(**base_params)

    logger.info(
        "Starting RandomizedSearchCV (%d iterations, %d-fold CV).",
        n_iter, cv_folds,
    )
    search = RandomizedSearchCV(
        estimator=base_model,
        param_distributions=param_distributions,
        n_iter=n_iter,
        scoring="neg_mean_absolute_error",
        cv=cv_folds,
        verbose=1,
        random_state=base_params.get("random_state", 42),
        n_jobs=base_params.get("n_jobs", -1),
    )
    search.fit(X_train, y_train)

    logger.info("Best params: %s", search.best_params_)
    logger.info("Best CV MAE: %.4f", -search.best_score_)
    return search.best_estimator_


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

def save_model(model: Any, path: str | Path) -> None:
    """Persist *model* to disk using ``joblib``.

    Parameters
    ----------
    model:
        Fitted scikit-learn / XGBoost model.
    path:
        Destination file path.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)
    logger.info("Model saved to %s", path.resolve())


def save_artifacts(
    model: Any,
    feature_names: list[str],
    metrics: dict[str, float],
    config: dict,
) -> None:
    """Save model, feature-name list, and performance CSV in one call.

    Creates the ``models/`` and ``artifacts/`` directories if they do not
    already exist.

    Parameters
    ----------
    model:
        Fitted model.
    feature_names:
        Ordered list of feature column names.
    metrics:
        Dictionary of evaluation metrics.
    config:
        Project configuration (reads ``paths.*``).
    """
    paths = config.get("paths", {})

    # Save model
    model_path = paths.get("model_save", "models/xgboost_best.joblib")
    save_model(model, model_path)

    # Save feature names
    fn_path = Path(paths.get("feature_names", "artifacts/feature_names.json"))
    fn_path.parent.mkdir(parents=True, exist_ok=True)
    save_json(
        {"feature_names": feature_names, "timestamp": get_current_timestamp()},
        fn_path,
    )
    logger.info("Feature names saved to %s", fn_path)

    # Save performance CSV
    perf_path = Path(paths.get("performance_csv", "artifacts/model_performance.csv"))
    perf_path.parent.mkdir(parents=True, exist_ok=True)
    perf_df = pd.DataFrame([metrics])
    perf_df["timestamp"] = get_current_timestamp()
    perf_df.to_csv(perf_path, index=False)
    logger.info("Performance metrics saved to %s", perf_path)

    logger.info("All artifacts saved.")


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

def plot_feature_importance(
    model: Any,
    feature_names: list[str],
    save_path: str | Path,
    top_n: int = 20,
) -> None:
    """Create a horizontal bar chart of the *top_n* most important features.

    Parameters
    ----------
    model:
        Fitted XGBoost model (must have ``feature_importances_``).
    feature_names:
        List of feature names aligned with ``model.feature_importances_``.
    save_path:
        Where to write the PNG.
    top_n:
        Number of bars to show.
    """
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    importances = pd.Series(model.feature_importances_, index=feature_names)
    top = importances.sort_values(ascending=True).tail(top_n)

    fig, ax = plt.subplots(figsize=(10, 8))
    top.plot(kind="barh", ax=ax, color="steelblue")
    ax.set_title(f"Top {top_n} Feature Importances")
    ax.set_xlabel("Importance (gain)")
    plt.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)
    logger.info("Feature importance plot saved to %s", save_path)


def plot_predictions(
    y_true: pd.Series | np.ndarray,
    y_pred: np.ndarray,
    save_path: str | Path,
) -> None:
    """Scatter plot of actual vs. predicted values with a 45° reference line.

    Parameters
    ----------
    y_true:
        Ground-truth target values.
    y_pred:
        Model predictions.
    save_path:
        Destination file path for the PNG.
    """
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.scatter(y_true, y_pred, alpha=0.15, s=4, color="steelblue")
    lo = min(y_true.min(), y_pred.min())
    hi = max(y_true.max(), y_pred.max())
    ax.plot([lo, hi], [lo, hi], "r--", linewidth=1)
    ax.set_xlabel("Actual log_price")
    ax.set_ylabel("Predicted log_price")
    ax.set_title("Actual vs. Predicted")
    plt.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)
    logger.info("Predictions plot saved to %s", save_path)


def plot_residuals(
    y_true: pd.Series | np.ndarray,
    y_pred: np.ndarray,
    save_path: str | Path,
) -> None:
    """Histogram of residuals (y_true − y_pred).

    Parameters
    ----------
    y_true, y_pred:
        Ground truth and predictions.
    save_path:
        Destination file path for the PNG.
    """
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    residuals = y_true.values - y_pred if hasattr(y_true, "values") else y_true - y_pred

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(residuals, bins=60, color="steelblue", edgecolor="white", alpha=0.85)
    ax.axvline(0, color="red", linestyle="--")
    ax.set_xlabel("Residual (actual − predicted)")
    ax.set_ylabel("Frequency")
    ax.set_title("Residual Distribution")
    plt.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)
    logger.info("Residual plot saved to %s", save_path)
