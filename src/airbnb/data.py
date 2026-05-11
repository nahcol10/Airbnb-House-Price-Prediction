"""Data loading, cleaning, feature engineering, and splitting.

This module is the **data layer** of the project.  Every function is
side-effect-free (pure) except for optional logging, making them easy to
unit-test independently.
"""

from __future__ import annotations

import ast
import logging
from typing import Tuple

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def load_raw_data(path: str) -> pd.DataFrame:
    """Load the raw Airbnb CSV into a DataFrame.

    Parameters
    ----------
    path:
        Absolute or relative path to the CSV file.

    Returns
    -------
    pd.DataFrame
        Raw dataset.

    Raises
    ------
    FileNotFoundError
        If *path* does not point to a valid file.
    """
    import os
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Data file not found: {path}")
    logger.info("Loading raw data from %s", path)
    df = pd.read_csv(path)
    logger.info("Loaded %d rows × %d columns", *df.shape)
    return df


# ---------------------------------------------------------------------------
# Cleaning
# ---------------------------------------------------------------------------

def clean_data(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """Apply all cleaning steps dictated by the project configuration.

    Steps (in order):
    1. Drop irrelevant columns.
    2. Parse ``host_response_rate`` from "95%" → 95.0.
    3. Convert string boolean columns to actual ``bool``.
    4. Engineer date-based features and drop the raw date columns.
    5. Fill numeric nulls with the column median.
    6. Fill categorical nulls with ``"Unknown"``.
    7. Drop any rows that still contain nulls.
    8. Remove rows where the target column (``log_price``) is null.

    Parameters
    ----------
    df:
        Raw or partially-cleaned DataFrame.
    config:
        Full project configuration dictionary.

    Returns
    -------
    pd.DataFrame
        Cleaned DataFrame ready for feature engineering.
    """
    df = df.copy()
    feat = config.get("features", {})

    # 1. Drop irrelevant columns
    drop_cols = [c for c in feat.get("drop_columns", []) if c in df.columns]
    if drop_cols:
        df.drop(columns=drop_cols, inplace=True)
        logger.info("Dropped %d columns: %s", len(drop_cols), drop_cols)

    # 2. Parse host_response_rate  "95%" → 95.0
    if "host_response_rate" in df.columns:
        df["host_response_rate"] = (
            df["host_response_rate"]
            .astype(str)
            .str.replace("%", "", regex=False)
            .replace("nan", np.nan)
            .astype(float)
        )
        logger.info("Parsed host_response_rate to float.")

    # 3. Convert boolean columns (t/f → True/False)
    for col in feat.get("boolean_columns", []):
        if col in df.columns:
            df[col] = (
                df[col]
                .map({"t": True, "f": False, True: True, False: False})
                .astype("boolean")
            )
    logger.info("Converted boolean columns.")

    # 4. Date feature engineering
    date_cols = feat.get("date_columns", [])
    reference_date = pd.Timestamp("2018-12-31")  # approximate data snapshot
    for col in date_cols:
        if col not in df.columns:
            continue
        df[col] = pd.to_datetime(df[col], errors="coerce")
        if col == "host_since":
            df["host_tenure_days"] = (reference_date - df[col]).dt.days
        elif col == "first_review":
            df["days_since_first_review"] = (reference_date - df[col]).dt.days
        elif col == "last_review":
            df["days_since_last_review"] = (reference_date - df[col]).dt.days
        df.drop(columns=[col], inplace=True)
    logger.info("Engineered date features and dropped raw date columns.")

    # 5. Fill numeric nulls with median
    for col in feat.get("numeric_fill_median", []):
        if col in df.columns and df[col].isnull().any():
            median_val = df[col].median()
            df[col].fillna(median_val, inplace=True)
            logger.debug("Filled %s nulls with median %.2f", col, median_val)

    # 6. Fill categorical nulls with "Unknown"
    for col in feat.get("categorical_fill_unknown", []):
        if col in df.columns and df[col].isnull().any():
            df[col].fillna("Unknown", inplace=True)
            logger.debug("Filled %s nulls with 'Unknown'", col)

    # 7. Drop remaining rows with any nulls
    before = len(df)
    df.dropna(inplace=True)
    dropped = before - len(df)
    if dropped:
        logger.info("Dropped %d rows with remaining nulls.", dropped)

    # 8. Ensure target is present and non-null
    if "log_price" in df.columns:
        df = df[df["log_price"].notnull()]

    logger.info("After cleaning: %d rows × %d columns", *df.shape)
    return df


# ---------------------------------------------------------------------------
# Feature Engineering
# ---------------------------------------------------------------------------

def engineer_features(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """Derive new features from existing columns.

    Specifically:
    * Parse the ``amenities`` column (a stringified list) and count total
      amenities.
    * Create binary flag columns for each high-value amenity.
    * Drop the raw ``amenities`` column.

    Parameters
    ----------
    df:
        Cleaned DataFrame.
    config:
        Full project configuration dictionary.

    Returns
    -------
    pd.DataFrame
        DataFrame with engineered features appended.
    """
    df = df.copy()
    feat = config.get("features", {})

    # Parse amenities
    if "amenities" in df.columns:
        # Amenities can look like: '{TV, "Wireless Internet", Kitchen}'
        # or: '["TV", "Wireless Internet"]'
        def _parse_amenities(raw):
            if not isinstance(raw, str):
                return []
            try:
                parsed = ast.literal_eval(raw)
                if isinstance(parsed, list):
                    return [
                        str(a).strip().strip('"').strip("'")
                        for a in parsed
                    ]
            except Exception:
                pass
            # fallback: split by comma
            return [
                a.strip().strip('"').strip("'").strip("{").strip("}")
                for a in raw.split(",")
            ]

        df["_amenities_list"] = df["amenities"].apply(_parse_amenities)
        df["amenities_count"] = df["_amenities_list"].apply(len)

        # High-value amenity flags
        hv = feat.get("high_value_amenities", [])
        for amenity in hv:
            safe = amenity.replace(" ", "_").replace("/", "_").lower()
            df[f"amenity_{safe}"] = df["_amenities_list"].apply(
                lambda lst, a=amenity: 1 if a in lst else 0
            )

        df.drop(columns=["amenities", "_amenities_list"], inplace=True)
        logger.info("Engineered %d amenity features.", len(hv) + 1)

    # Text-length proxy features
    for col in ["description", "name"]:
        if col in df.columns:
            df[f"{col}_length"] = df[col].astype(str).apply(len)

    logger.info("Feature engineering complete. Shape: %d × %d", *df.shape)
    return df


# ---------------------------------------------------------------------------
# Encoding
# ---------------------------------------------------------------------------

def encode_features(
    df: pd.DataFrame,
    config: dict,
) -> Tuple[pd.DataFrame, list]:
    """Encode categorical columns and return the feature name list.

    * **One-hot** encode columns listed in ``features.encode_onehot``.
    * **Label** encode columns listed in ``features.encode_label``.

    Parameters
    ----------
    df:
        DataFrame after feature engineering.
    config:
        Full project configuration dictionary.

    Returns
    -------
    tuple[pd.DataFrame, list[str]]
        Encoded DataFrame and an ordered list of feature column names.
    """
    df = df.copy()
    feat = config.get("features", {})

    # One-hot encoding
    onehot_cols = [c for c in feat.get("encode_onehot", []) if c in df.columns]
    if onehot_cols:
        df = pd.get_dummies(df, columns=onehot_cols, drop_first=True, dummy_na=True)
        logger.info("One-hot encoded %d columns.", len(onehot_cols))

    # Label encoding
    label_cols = [c for c in feat.get("encode_label", []) if c in df.columns]
    encoders: dict[str, LabelEncoder] = {}
    for col in label_cols:
        le = LabelEncoder()
        # Fill any remaining NaNs for label encoding
        df[col] = df[col].astype(str)
        df[col] = le.fit_transform(df[col])
        encoders[col] = le
        logger.info("Label encoded '%s' (%d classes).", col, len(le.classes_))

    feature_names = [c for c in df.columns if c != "log_price"]
    logger.info("Total features after encoding: %d", len(feature_names))
    return df, feature_names


# ---------------------------------------------------------------------------
# Train / Val / Test split
# ---------------------------------------------------------------------------

def split_data(
    df: pd.DataFrame,
    target_col: str = "log_price",
    config: dict | None = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, pd.Series]:
    """Split the DataFrame into train / validation / test sets.

    The split sizes are read from ``config.model.test_size`` and
    ``config.model.val_size`` (both default to 0.15).

    Parameters
    ----------
    df:
        Encoded, fully-prepared DataFrame.
    target_col:
        Name of the target column.
    config:
        Project configuration (used for split ratios and random state).

    Returns
    -------
    tuple
        ``(X_train, X_val, X_test, y_train, y_val, y_test)``
    """
    if config is None:
        config = {}
    model_cfg = config.get("model", {})
    test_size = model_cfg.get("test_size", 0.15)
    val_size = model_cfg.get("val_size", 0.15)
    random_state = model_cfg.get("random_state", 42)

    y = df[target_col]
    X = df.drop(columns=[target_col])

    # First split: train+val  vs  test
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    # Second split: train  vs  val  (relative to remaining data)
    val_ratio = val_size / (1 - test_size)
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=val_ratio, random_state=random_state
    )

    logger.info(
        "Data split — train: %d, val: %d, test: %d",
        len(X_train), len(X_val), len(X_test),
    )
    return X_train, X_val, X_test, y_train, y_val, y_test
