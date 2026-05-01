import pandas as pd
from database import fetch_videos
from datetime import datetime, timezone
import re
import matplotlib.pyplot as plt


def parse_duration(duration):
    pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
    match = re.match(pattern, duration)

    hours = int(match.group(1)) if match.group(1) else 0
    minutes = int(match.group(2)) if match.group(2) else 0
    seconds = int(match.group(3)) if match.group(3) else 0

    return hours * 3600 + minutes * 60 + seconds


def load_data():
    rows, colnames = fetch_videos()
    df = pd.DataFrame(rows, columns=colnames)

    df["published_at"] = pd.to_datetime(df["published_at"], utc=True)
    df = df[df["views"] > 0]

    df["duration_seconds"] = df["duration"].apply(parse_duration)
    df["duration_minutes"] = df["duration_seconds"] / 60

    df["days_since_upload"] = (datetime.now(timezone.utc) - df["published_at"]).dt.days
    df = df[df["days_since_upload"] >= 0]
    df["days_since_upload"] = df["days_since_upload"].replace(0, 1)

    df["views_per_day"] = df["views"] / df["days_since_upload"]

    df["engagement_rate"] = (df["likes"] + df["comments"]) / df["views"]
    df["like_ratio"] = df["likes"] / df["views"]
    df["comment_ratio"] = df["comments"] / df["views"]

    return df

def basic_info(df):
    print("\n=== Dataset Info ===")
    print(df.info())

    print("\n=== Summary Stats ===")
    print(df.describe())

def check_missing(df):
    print("\n=== Missing Values ===")
    print(df.isna().sum())

# target distribution
def plot_target(df):
    plt.figure()
    plt.hist(df["views_per_day"], bins=20)
    plt.title("Views per Day Distribution")
    plt.xlabel("Views per Day")
    plt.ylabel("Frequency")
    plt.show()

# feature distribution
def plot_features(df):
    cols = ["duration_minutes", "likes", "comments", "engagement_rate"]

    for col in cols:
        plt.figure()
        plt.hist(df[col], bins=20)
        plt.title(f"{col} Distribution")
        plt.show()

# correlation matrix
def correlation(df):
    print("\n=== Correlation Matrix ===")
    corr = df[
        ["views_per_day", "duration_minutes", "likes", "comments",
         "engagement_rate", "like_ratio", "comment_ratio"]
    ].corr()

    print(corr)

    plt.figure()
    plt.imshow(corr)
    plt.colorbar()
    plt.xticks(range(len(corr.columns)), corr.columns, rotation=45)
    plt.yticks(range(len(corr.columns)), corr.columns)
    plt.title("Correlation Heatmap")
    plt.show()

def main():
    df = load_data()

    basic_info(df)
    check_missing(df)
    plot_target(df)
    plot_features(df)
    correlation(df)


if __name__ == "__main__":
    main()