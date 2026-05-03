import pandas as pd
import joblib
from pathlib import Path
from src.database import fetch_videos
from datetime import datetime, timezone
import re
import numpy as np


def parse_duration(duration):
    pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
    match = re.match(pattern, duration)

    hours = int(match.group(1)) if match.group(1) else 0
    minutes = int(match.group(2)) if match.group(2) else 0
    seconds = int(match.group(3)) if match.group(3) else 0

    return hours * 3600 + minutes * 60 + seconds


def load_model():
    BASE_DIR = Path(__file__).resolve().parent.parent
    MODEL_PATH = BASE_DIR / "models" / "gbr_model.pkl"
    return joblib.load(MODEL_PATH)


def prepare_data():
    rows, cols = fetch_videos()
    df = pd.DataFrame(rows, columns=cols)

    df["published_at"] = pd.to_datetime(df["published_at"], utc=True)
    df["duration_seconds"] = df["duration"].apply(parse_duration)
    df["duration_minutes"] = df["duration_seconds"] / 60

    df["days_since_upload"] = (datetime.now(timezone.utc) - df["published_at"]).dt.days
    df["days_since_upload"] = df["days_since_upload"].replace(0, 1)

    df["comment_ratio"] = df["comments"] / df["views"]

    return df


def predict():
    model = load_model()
    df = prepare_data()

    features = [
        "duration_minutes",
        "days_since_upload",
        "likes",
        "comment_ratio"
    ]

    X = df[features]

    preds_log = model.predict(X)
    preds = np.expm1(preds_log)

    df["predicted_views_per_day"] = preds

    return df

if __name__ == "__main__":
    df = predict()
    print(df[["title", "predicted_views_per_day"]].head())