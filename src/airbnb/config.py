"""Configuration loader for the Airbnb Price Prediction project.

Exposes :class:`Settings` — a thin wrapper around the YAML config that
provides dot-access to every top-level section and makes all file-system
paths absolute via :mod:`pathlib`.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# YAML loader
# ---------------------------------------------------------------------------

def load_config(path: str | Path) -> dict[str, Any]:
    """Read a YAML configuration file and return its contents as a dict.

    Parameters
    ----------
    path:
        Path to the YAML file.  If the file does not exist a ``FileNotFoundError``
        is raised with a helpful message.

    Returns
    -------
    dict
        Parsed YAML contents.
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(
            f"Configuration file not found: {path.resolve()}\n"
            "Please copy config/config.example.yaml to config/config.yaml "
            "and adjust values for your environment."
        )
    with path.open("r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    logger.info("Loaded configuration from %s", path.resolve())
    return cfg


# ---------------------------------------------------------------------------
# Settings dataclass-style helper
# ---------------------------------------------------------------------------

class Settings:
    """Convenience wrapper that gives attribute-based access to config sections.

    Example
    -------
    >>> s = Settings("config/config.yaml")
    >>> s.model["type"]
    'xgboost'
    >>> s.paths.model_save  # resolved to absolute Path
    PosixPath('/.../models/xgboost_best.joblib')
    """

    def __init__(self, config_path: str | Path | None = None, config_dict: dict | None = None) -> None:
        if config_dict is not None:
            self._cfg = config_dict
        elif config_path is not None:
            self._cfg = load_config(config_path)
        else:
            raise ValueError("Either config_path or config_dict must be provided.")
        self._root = Path(config_path).resolve().parent.parent if config_path else Path.cwd()

    # -- public helpers -------------------------------------------------------

    @property
    def data(self) -> dict[str, Any]:
        return self._cfg.get("data", {})

    @property
    def model(self) -> dict[str, Any]:
        return self._cfg.get("model", {})

    @property
    def features(self) -> dict[str, Any]:
        return self._cfg.get("features", {})

    @property
    def training(self) -> dict[str, Any]:
        return self._cfg.get("training", {})

    @property
    def paths(self) -> dict[str, Any]:
        """Return paths dict with every value resolved as an absolute ``Path``."""
        raw = self._cfg.get("paths", {})
        return {k: (self._root / v) if isinstance(v, str) else v for k, v in raw.items()}

    @property
    def raw_config(self) -> dict[str, Any]:
        """Return the full, unprocessed config dictionary."""
        return self._cfg

    def __repr__(self) -> str:
        return f"Settings(keys={list(self._cfg.keys())})"
