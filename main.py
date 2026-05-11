"""
Airbnb Price Prediction — Main Entry Point

Usage:
    python main.py train          # Train the model
    python main.py evaluate       # Evaluate on test set
    python main.py predict        # Make a single prediction (reads JSON from stdin or --input file)
    python main.py eda            # Quick EDA summary
    python main.py all            # Run full pipeline: train + evaluate
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Make sure the project root and src/ are on sys.path so that imports work
# regardless of how the script is invoked.
_PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(_PROJECT_ROOT / "src"))

import numpy as np

from airbnb.config import Settings, load_config
from airbnb.data import (
    clean_data,
    encode_features,
    engineer_features,
    load_raw_data,
    split_data,
)
from airbnb.predict import load_model, predict, preprocess_input
from airbnb.train import (
    evaluate_model,
    plot_feature_importance,
    plot_predictions,
    plot_residuals,
    save_artifacts,
    train_xgboost,
    tune_model,
)
from airbnb.utils import format_metrics, print_section_header, setup_logging


# ---------------------------------------------------------------------------
# CLI command implementations
# ---------------------------------------------------------------------------

def cmd_train(args: argparse.Namespace) -> None:
    """Train (or tune) the model and persist artifacts."""
    print_section_header("TRAIN")
    settings = Settings("config/config.yaml")
    cfg = settings.raw_config

    # Load & prepare
    df = load_raw_data(str(_PROJECT_ROOT / cfg["data"]["raw_path"]))
    df = clean_data(df, cfg)
    df = engineer_features(df, cfg)
    df, feature_names = encode_features(df, cfg)
    X_train, X_val, X_test, y_train, y_val, y_test = split_data(df, config=cfg)

    # Train or tune
    if args.tune:
        print_section_header("HYPER-PARAMETER TUNING")
        model = tune_model(X_train, y_train, cfg)
    else:
        model = train_xgboost(X_train, y_train, cfg)

    # Evaluate
    print_section_header("VALIDATION METRICS")
    val_metrics = evaluate_model(model, X_val, y_val)
    print(format_metrics(val_metrics))

    # Save
    save_artifacts(model, feature_names, val_metrics, cfg)

    print("\nTraining complete. Model saved.\n")


def cmd_evaluate(args: argparse.Namespace) -> None:
    """Evaluate a saved model on the held-out test set."""
    print_section_header("EVALUATE")
    settings = Settings("config/config.yaml")
    cfg = settings.raw_config

    model_path = str(settings.paths["model_save"])
    if not Path(model_path).exists():
        print(f"ERROR: No saved model found at {model_path}. Run 'train' first.")
        sys.exit(1)

    model = load_model(model_path)

    # Load & prepare data (same pipeline)
    df = load_raw_data(str(_PROJECT_ROOT / cfg["data"]["raw_path"]))
    df = clean_data(df, cfg)
    df = engineer_features(df, cfg)
    df, feature_names = encode_features(df, cfg)
    X_train, X_val, X_test, y_train, y_val, y_test = split_data(df, config=cfg)

    # Test metrics
    test_metrics = evaluate_model(model, X_test, y_test)
    print("\nTest Set Metrics:")
    print(format_metrics(test_metrics))

    # Plots
    y_pred = model.predict(X_test)
    plot_predictions(y_test, y_pred, "artifacts/predictions_plot.png")
    plot_residuals(y_test, y_pred, "artifacts/residuals_plot.png")
    plot_feature_importance(model, feature_names, "artifacts/feature_importance.png")
    print("Plots saved to artifacts/.")


def cmd_predict(args: argparse.Namespace) -> None:
    """Make a single prediction from a JSON input."""
    print_section_header("PREDICT")
    settings = Settings("config/config.yaml")
    cfg = settings.raw_config

    model_path = str(settings.paths["model_save"])
    fn_path = str(settings.paths["feature_names"])
    if not Path(model_path).exists():
        print(f"ERROR: No saved model found at {model_path}. Run 'train' first.")
        sys.exit(1)

    model = load_model(model_path)
    artifact = json.loads(Path(fn_path).read_text())
    feature_names = artifact["feature_names"]

    # Read input JSON
    if args.input:
        with open(args.input, "r") as fh:
            input_data = json.load(fh)
    else:
        print("Enter JSON listing (Ctrl-D to finish):")
        raw = sys.stdin.read()
        input_data = json.loads(raw)

    processed = preprocess_input(input_data, feature_names, cfg)
    price = predict(model, processed)
    print(f"\n  Predicted log_price : {price:.4f}")
    print(f"  Approx. price (USD): ${np.exp(price):,.2f}\n")


def cmd_eda(args: argparse.Namespace) -> None:
    """Print a quick exploratory summary of the raw dataset."""
    print_section_header("EXPLORATORY DATA ANALYSIS")
    settings = Settings("config/config.yaml")
    cfg = settings.raw_config
    df = load_raw_data(str(_PROJECT_ROOT / cfg["data"]["raw_path"]))

    print(f"Shape : {df.shape[0]:,} rows × {df.shape[1]} columns\n")
    print("── Column Types ──")
    print(df.dtypes.value_counts().to_string())
    print("\n── Missing Values (top 15) ──")
    missing = df.isnull().sum().sort_values(ascending=False).head(15)
    print(missing.to_string())
    print("\n── Target (log_price) Stats ──")
    if "log_price" in df.columns:
        print(df["log_price"].describe().to_string())
    else:
        print("  'log_price' column not found!")
    print("\n── Sample Rows ──")
    print(df.head(3).T.to_string())
    print()


def cmd_all(args: argparse.Namespace) -> None:
    """Run the full pipeline: train → evaluate."""
    # Create a fake args namespace for sub-commands
    train_ns = argparse.Namespace(tune=args.tune)
    cmd_train(train_ns)
    eval_ns = argparse.Namespace()
    cmd_evaluate(eval_ns)


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Airbnb Price Prediction Toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # train
    p_train = sub.add_parser("train", help="Train the XGBoost model")
    p_train.add_argument(
        "--tune", action="store_true",
        help="Run hyper-parameter tuning first",
    )

    # evaluate
    sub.add_parser("evaluate", help="Evaluate saved model on test set")

    # predict
    p_pred = sub.add_parser("predict", help="Predict price for a single listing")
    p_pred.add_argument(
        "--input", type=str, default=None,
        help="Path to JSON input file",
    )

    # eda
    sub.add_parser("eda", help="Quick exploratory data-analysis summary")

    # all
    p_all = sub.add_parser("all", help="Full pipeline: train + evaluate")
    p_all.add_argument(
        "--tune", action="store_true",
        help="Run hyper-parameter tuning first",
    )

    return parser


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    setup_logging()
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    dispatch = {
        "train": cmd_train,
        "evaluate": cmd_evaluate,
        "predict": cmd_predict,
        "eda": cmd_eda,
        "all": cmd_all,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
