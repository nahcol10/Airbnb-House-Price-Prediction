"""Tests for the data module — cleaning, feature engineering, encoding."""

from __future__ import annotations

import pytest
import pandas as pd
import numpy as np

from airbnb.data import clean_data, engineer_features, encode_features, split_data


# ---------------------------------------------------------------------------
# Minimal config fixture used across tests
# ---------------------------------------------------------------------------

@pytest.fixture()
def mini_config() -> dict:
    """Return a stripped-down config dict sufficient for data tests."""
    return {
        "features": {
            "drop_columns": ["id", "thumbnail_url", "name", "description"],
            "numeric_fill_median": [
                "bathrooms", "bedrooms", "beds",
                "review_scores_rating", "host_response_rate",
            ],
            "categorical_fill_unknown": ["neighbourhood", "zipcode"],
            "boolean_columns": [
                "cleaning_fee", "host_has_profile_pic",
                "host_identity_verified", "instant_bookable",
            ],
            "high_value_amenities": ["TV", "Kitchen", "WiFi"],
            "date_columns": ["host_since", "first_review", "last_review"],
            "encode_onehot": ["city", "room_type"],
            "encode_label": ["zipcode"],
        },
        "model": {
            "test_size": 0.2,
            "val_size": 0.2,
            "random_state": 42,
        },
    }


@pytest.fixture()
def mini_df() -> pd.DataFrame:
    """Small synthetic DataFrame that mimics the raw Airbnb schema."""
    return pd.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "name": ["A", "B", "C", "D", "E"],
        "description": ["desc"] * 5,
        "thumbnail_url": ["http://x"] * 5,
        "log_price": [4.5, 5.0, 3.8, 6.1, 4.2],
        "bathrooms": [1.0, None, 2.0, 1.0, None],
        "bedrooms": [2, 1, 3, 1, 2],
        "beds": [2, 1, 3, 1, 2],
        "review_scores_rating": [90, None, 95, 80, None],
        "host_response_rate": ["95%", "nan", "100%", "80%", "nan"],
        "neighbourhood": [" Downtown", None, " Midtown", None, " Downtown"],
        "zipcode": ["02101", None, "10001", None, "02101"],
        "cleaning_fee": ["t", "f", "t", "t", "f"],
        "host_has_profile_pic": ["t", "t", "f", "t", "t"],
        "host_identity_verified": ["t", "f", "t", "t", "f"],
        "instant_bookable": ["f", "t", "f", "f", "t"],
        "city": ["Boston", "NYC", "LA", "NYC", "Boston"],
        "room_type": ["Entire home", "Private room", "Entire home", "Shared room", "Private room"],
        "amenities": ['{TV, Kitchen}', '{WiFi}', '{TV, Kitchen, WiFi}', '{Kitchen}', '{TV}'],
        "host_since": ["2015-01-01", "2016-06-01", "2014-03-15", "2017-09-01", "2015-07-20"],
        "first_review": ["2015-02-01", "2016-07-01", "2014-04-15", "2017-10-01", "2015-08-20"],
        "last_review": ["2018-01-01", "2018-06-01", "2018-04-15", "2018-10-01", "2018-08-20"],
        "accommodates": [4, 2, 6, 1, 3],
        "number_of_reviews": [10, 5, 50, 1, 20],
    })


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestCleanData:
    """Tests for :func:`clean_data`."""

    def test_drops_columns(self, mini_df, mini_config):
        result = clean_data(mini_df, mini_config)
        for col in mini_config["features"]["drop_columns"]:
            assert col not in result.columns

    def test_no_nulls_remain(self, mini_df, mini_config):
        result = clean_data(mini_df, mini_config)
        assert result.isnull().sum().sum() == 0

    def test_host_response_rate_parsed(self, mini_df, mini_config):
        result = clean_data(mini_df, mini_config)
        # After parsing, values should be float (95.0, not "95%")
        assert result["host_response_rate"].dtype in [float, "float64"]

    def test_boolean_columns_converted(self, mini_df, mini_config):
        result = clean_data(mini_df, mini_config)
        for col in mini_config["features"]["boolean_columns"]:
            assert (
                pd.api.types.is_bool_dtype(result[col])
                or str(result[col].dtype) == "boolean"
            )

    def test_date_columns_dropped(self, mini_df, mini_config):
        result = clean_data(mini_df, mini_config)
        for col in mini_config["features"]["date_columns"]:
            assert col not in result.columns


class TestEngineerFeatures:
    """Tests for :func:`engineer_features`."""

    def test_amenities_count(self, mini_df, mini_config):
        cleaned = clean_data(mini_df, mini_config)
        result = engineer_features(cleaned, mini_config)
        assert "amenities_count" in result.columns

    def test_amenity_flags_created(self, mini_df, mini_config):
        cleaned = clean_data(mini_df, mini_config)
        result = engineer_features(cleaned, mini_config)
        hv = mini_config["features"]["high_value_amenities"]
        for amenity in hv:
            safe = amenity.replace(" ", "_").replace("/", "_").lower()
            assert f"amenity_{safe}" in result.columns

    def test_amenities_column_removed(self, mini_df, mini_config):
        cleaned = clean_data(mini_df, mini_config)
        result = engineer_features(cleaned, mini_config)
        assert "amenities" not in result.columns


class TestEncodeFeatures:
    """Tests for :func:`encode_features`."""

    def test_returns_feature_names(self, mini_df, mini_config):
        cleaned = clean_data(mini_df, mini_config)
        featured = engineer_features(cleaned, mini_config)
        df_enc, names = encode_features(featured, mini_config)
        assert isinstance(names, list)
        assert len(names) > 0
        assert "log_price" not in names

    def test_onehot_creates_dummies(self, mini_df, mini_config):
        cleaned = clean_data(mini_df, mini_config)
        featured = engineer_features(cleaned, mini_config)
        df_enc, _ = encode_features(featured, mini_config)
        # After one-hot, original categorical cols should be gone
        for col in mini_config["features"]["encode_onehot"]:
            assert col not in df_enc.columns


class TestSplitData:
    """Tests for :func:`split_data`."""

    def test_split_shapes(self, mini_df, mini_config):
        cleaned = clean_data(mini_df, mini_config)
        featured = engineer_features(cleaned, mini_config)
        df_enc, _ = encode_features(featured, mini_config)
        X_tr, X_va, X_te, y_tr, y_va, y_te = split_data(df_enc, config=mini_config)
        assert len(X_tr) + len(X_va) + len(X_te) == len(df_enc)
        assert len(y_tr) == len(X_tr)
        assert len(y_te) == len(X_te)
