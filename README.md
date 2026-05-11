# Airbnb Price Predictor

End-to-end ML project that predicts nightly listing prices on Airbnb. Trains and compares multiple models (Linear Regression, Random Forest, XGBoost, LightGBM) on real listing data across six US cities, and serves predictions through a REST API backed by a Next.js frontend.

## Project Structure

```
airbnb-price-predictor/
├── api/                        FastAPI backend (predict + health endpoints)
├── artifacts/                  Feature names, model performance metrics
├── config/config.yaml          All hyperparameters and feature config
├── data/                       Raw and processed CSV datasets
├── models/                     Serialized .joblib model files
├── notebooks/
│   ├── eda.ipynb               Exploratory data analysis (50 cells)
│   └── training.ipynb          Full training pipeline (54 cells)
├── src/airbnb/                 Core ML package
│   ├── config.py               YAML config loader
│   ├── data.py                 Data loading, cleaning, feature engineering
│   ├── train.py                Model training, tuning, comparison
│   ├── predict.py              Inference wrapper
│   └── utils.py                Shared helpers
├── tests/                      Unit tests for data and training modules
├── web/                        Next.js 14 + React frontend
│   └── src/
│       ├── app/                App Router pages and layout
│       ├── components/         PredictionForm, ResultCard
│       ├── lib/api.ts          API client for backend calls
│       └── types/index.ts      TypeScript interfaces
├── template.py                 CLI scaffolder for new ML projects
├── main.py                     CLI entry point
├── docker-compose.yml          Full-stack local dev (API + Web)
├── Dockerfile                  Multi-stage production build for API
├── heroku.yaml                 Heroku Docker deployment
├── pyproject.toml              Python package metadata
├── Procfile                    Heroku process definition
└── requirements.txt            Python dependencies
```

## Tech Stack

| Layer       | Technology                                |
|-------------|-------------------------------------------|
| ML Models   | XGBoost, LightGBM, Random Forest, Scikit-learn |
| Backend     | FastAPI, Uvicorn, Pydantic, Joblib        |
| Frontend    | Next.js 14, React 18, TypeScript, Tailwind CSS |
| Data        | Pandas, NumPy, Matplotlib, Seaborn        |
| Deployment  | Docker, Docker Compose, Heroku            |
| Config      | YAML, pyproject.toml                      |

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker and Docker Compose (optional, for containerized setup)

### 1. Clone and Install Backend

```bash
git clone https://github.com/<your-username>/airbnb-price-predictor.git
cd airbnb-price-predictor

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run Training

Open `notebooks/training.ipynb` in Jupyter and run all cells. This will:
- Clean and preprocess `data/Airbnb_Data.csv`
- Engineer features (amenity flags, host tenure, date diffs)
- Train and compare four regression models
- Run RandomizedSearchCV on the best performer
- Save the tuned model to `models/xgboost_best.joblib`

### 3. Start the API

```bash
uvicorn api.main:app --reload --port 8000
```

The API docs are available at [http://localhost:8000/docs](http://localhost:8000/docs).

**Key endpoints:**

| Method | Path        | Description                           |
|--------|-------------|---------------------------------------|
| POST   | `/predict`  | Predict price for a listing           |
| GET    | `/health`   | Check API status and model readiness  |
| GET    | `/features` | List all model feature names          |

### 4. Start the Frontend

```bash
cd web
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to access the prediction interface.

### 5. Docker (All-in-One)

```bash
docker compose up --build
```

- API runs on **port 8000**
- Web UI runs on **port 3000**

## Prediction API

Send a POST request with listing details to get a predicted nightly price:

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "accommodates": 4,
    "bathrooms": 1.0,
    "bedrooms": 1,
    "beds": 1,
    "city": "NYC",
    "room_type": "Entire home/apt",
    "property_type": "Apartment",
    "cleaning_fee": true,
    "instant_bookable": true,
    "latitude": 40.75,
    "longitude": -73.98,
    "review_scores_rating": 95.0,
    "number_of_reviews": 25,
    "amenity_count": 12
  }'
```

**Response:**

```json
{
  "log_price": 5.1234,
  "price_usd": 167.89
}
```

## Training Pipeline

The training notebook (`notebooks/training.ipynb`) walks through the full pipeline:

1. **Data Cleaning** — Handle missing values, drop unusable columns, convert booleans
2. **Feature Engineering** — Amenity presence flags, host tenure, review recency, location features
3. **Encoding** — One-hot for categorical (city, room_type, property_type, bed_type, cancellation_policy), label encoding for zipcode and neighbourhood
4. **Train/Test Split** — 70/15/15 split (train/validation/test)
5. **Model Comparison** — Linear Regression, Random Forest, XGBoost, LightGBM with default params
6. **Hyperparameter Tuning** — RandomizedSearchCV (50 iterations, 5-fold CV) on the best model
7. **Evaluation** — RMSE, MAE, R-squared on the held-out test set
8. **Artifact Export** — Save model, feature names, and performance metrics

## Scaffolding New Projects

The included `template.py` generates the same folder structure for new ML projects:

```bash
python template.py my-new-project --with-web
```

This creates all directories, placeholder files, and the web frontend template so you can start building immediately.

## Deployment

### Heroku (Docker)

The project includes `heroku.yaml` for container-based Heroku deployment:

```bash
heroku create my-price-predictor
git push heroku main
```

### Docker (Production)

```bash
docker build -t airbnb-api .
docker run -p 8000:8000 airbnb-api
```

## Config

All model parameters, feature lists, and paths live in `config/config.yaml`. Edit this file to change:
- Which columns to drop or fill
- Amenity feature flags
- Training hyperparameters (n_estimators, max_depth, learning rate, etc.)
- CV folds and search iterations
- File output paths

## Tests

```bash
pytest tests/
```

## License

MIT
