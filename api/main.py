"""FastAPI backend for Airbnb price prediction."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import logging

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from airbnb.utils import setup_logging

ROOT = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="Airbnb Price Predictor API",
    version="1.0.0",
    description="Predict Airbnb listing nightly prices using XGBoost",
)

logger = logging.getLogger("airbnb.api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = None
feature_names: list[str] = []


class ListingInput(BaseModel):
    accommodates: int = 4
    bathrooms: float = 1.0
    bedrooms: float = 1.0
    beds: float = 1.0
    city: str = "NYC"
    room_type: str = "Entire home/apt"
    property_type: str = "Apartment"
    cleaning_fee: bool = True
    host_has_profile_pic: bool = True
    host_identity_verified: bool = True
    host_response_rate: float = 95.0
    instant_bookable: bool = True
    number_of_reviews: int = 10
    review_scores_rating: float = 95.0
    latitude: float = 40.75
    longitude: float = -73.98
    zipcode: str = "10001"
    neighbourhood: str = "Manhattan"
    bed_type: str = "Real Bed"
    cancellation_policy: str = "flexible"
    amenity_count: int = 8


class PredictionOutput(BaseModel):
    log_price: float
    price_usd: float


def load_artifacts():
    global model, feature_names
    model_path = ROOT / "models" / "xgboost_best.joblib"
    fn_path = ROOT / "artifacts" / "feature_names.json"

    if not model_path.exists():
        logger.warning(f"{model_path} not found. Returning dummy predictions.")
        model = None
        feature_names = []
        return

    model = joblib.load(str(model_path))
    with open(fn_path) as f:
        feature_names = json.load(f)["feature_names"]
    logger.info(f"Model loaded successfully. Found {len(feature_names)} features.")


def build_feature_row(data: dict) -> pd.DataFrame:
    row = {k: 0 for k in feature_names}

    row["accommodates"] = data.get("accommodates", 4)
    row["bathrooms"] = data.get("bathrooms", 1.0)
    row["bedrooms"] = data.get("bedrooms", 1.0)
    row["beds"] = data.get("beds", 1.0)
    row["host_response_rate"] = data.get("host_response_rate", 95.0)
    row["cleaning_fee"] = int(data.get("cleaning_fee", True))
    row["host_has_profile_pic"] = int(data.get("host_has_profile_pic", True))
    row["host_identity_verified"] = int(data.get("host_identity_verified", True))
    row["instant_bookable"] = int(data.get("instant_bookable", False))
    row["number_of_reviews"] = data.get("number_of_reviews", 10)
    row["review_scores_rating"] = data.get("review_scores_rating", 95.0)
    row["latitude"] = data.get("latitude", 40.75)
    row["longitude"] = data.get("longitude", -73.98)

    for feat in feature_names:
        if feat.startswith("city_"):
            if data.get("city") == feat[5:]:
                row[feat] = 1
        elif feat.startswith("room_type_"):
            if data.get("room_type") == feat[10:]:
                row[feat] = 1
        elif feat.startswith("property_type_"):
            if data.get("property_type") == feat[14:]:
                row[feat] = 1
        elif feat.startswith("bed_type_"):
            if data.get("bed_type") == feat[9:]:
                row[feat] = 1
        elif feat.startswith("cancellation_policy_"):
            if data.get("cancellation_policy") == feat[20:]:
                row[feat] = 1

    return pd.DataFrame([row])


@app.on_event("startup")
def startup():
    log_file = ROOT / "logs" / "api.log"
    setup_logging(log_file=str(log_file))
    logger.info("Starting up Airbnb Price Predictor API...")
    load_artifacts()


@app.get("/health")
def health():
    logger.info("Health check requested")
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "features": len(feature_names),
    }


@app.get("/features")
def get_features():
    logger.info("Features list requested")
    return {"features": feature_names, "count": len(feature_names)}


@app.post("/predict", response_model=PredictionOutput)
def predict(input_data: ListingInput):
    logger.info(
        f"Prediction requested for listing in {input_data.city}, {input_data.neighbourhood}"
    )
    if model is None:
        logger.warning("Model not loaded, using dummy prediction fallback.")
        log_p = 4.7 + np.random.randn() * 0.3
        return PredictionOutput(
            log_price=round(log_p, 4), price_usd=round(np.exp(log_p), 2)
        )

    data = build_feature_row(input_data.model_dump())
    log_p = float(model.predict(data)[0])
    price = round(np.exp(log_p), 2)
    logger.info(f"Prediction successful: log_price={round(log_p, 4)}, price={price}")
    return PredictionOutput(log_price=round(log_p, 4), price_usd=price)
