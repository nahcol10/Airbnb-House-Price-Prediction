"""Shared utilities — logging, timestamps, JSON I/O, display helpers."""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def setup_logging(log_file: str | None = None, level: int = logging.INFO) -> logging.Logger:
    """Configure the root logger with both console and optional file output.

    Parameters
    ----------
    log_file:
        If provided, also write log messages to this file.
    level:
        Logging level (default ``logging.INFO``).

    Returns
    -------
    logging.Logger
        Configured root logger.
    """
    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]

    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(level=level, format=fmt, handlers=handlers)
    return logging.getLogger()


# ---------------------------------------------------------------------------
# Timestamps
# ---------------------------------------------------------------------------

def get_current_timestamp() -> str:
    """Return an ISO-8601 timestamp string (UTC).

    Returns
    -------
    str
        e.g. ``"2025-01-15T12:30:00Z"``
    """
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# JSON helpers
# ---------------------------------------------------------------------------

def save_json(data: dict, path: str | Path) -> None:
    """Serialise *data* to a JSON file with indentation.

    Parameters
    ----------
    data:
        Dictionary to persist.
    path:
        Destination file path.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, default=str)


def load_json(path: str | Path) -> dict:
    """Load a JSON file into a Python dictionary.

    Parameters
    ----------
    path:
        Path to the JSON file.

    Returns
    -------
    dict
        Parsed contents.
    """
    with Path(path).open("r", encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def print_section_header(title: str, width: int = 70, char: str = "=") -> None:
    r"""Print a visually distinct section header to stdout.

    Example
    -------
    >>> print_section_header("Training")
    ================================================================
                               Training
    ================================================================
    """
    padding = (width - len(title)) // 2
    print()
    print(char * width)
    print(" " * padding + title)
    print(char * width)
    print()


def format_metrics(metrics: dict[str, float]) -> str:
    """Render a metrics dictionary as a tidy alignment table.

    Parameters
    ----------
    metrics:
        Mapping of metric name → value.

    Returns
    -------
    str
        Multi-line table string.
    """
    sep = "-" * 32
    rows = [f"{k:<20} {v:>10.4f}" for k, v in metrics.items()]
    return "\n".join([sep, f"{'Metric':<20} {'Value':>10}", sep, *rows, sep])


# ---------------------------------------------------------------------------
# Metrics calculation
# ---------------------------------------------------------------------------

def calculate_metrics(
    y_true: np.ndarray | list,
    y_pred: np.ndarray | list,
) -> dict[str, float]:
    """Compute MAE, RMSE, R-squared, and MAPE.

    Parameters
    ----------
    y_true:
        Ground-truth values.
    y_pred:
        Predicted values.

    Returns
    -------
    dict
        ``{"mae": …, "rmse": …, "r2": …, "mape": …}``
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)

    mae = float(np.mean(np.abs(y_true - y_pred)))
    rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    r2 = 1.0 - ss_res / ss_tot if ss_tot != 0 else 0.0
    # MAPE — avoid division by zero
    nonzero = y_true != 0
    if nonzero.any():
        mape = float(np.mean(np.abs((y_true[nonzero] - y_pred[nonzero]) / y_true[nonzero]))) * 100
    else:
        mape = float("inf")

    return {
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "r2": round(r2, 4),
        "mape": round(mape, 2),
    }
