import pandas as pd
from datetime import datetime
from datetime import datetime, timezone
from database import fetch_videos
from plots import plot_views_vs_duration, plot_engagement_distribution, plot_views_vs_engagement, plot_top_videos, plot_recency_vs_performance
import re

# Load data
def load_data():
    rows, colnames = fetch_videos()
    df = pd.DataFrame(rows, columns=colnames)
    return df

def parse_duration(duration):
    pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
    match = re.match(pattern, duration)

    hours = int(match.group(1)) if match.group(1) else 0
    minutes = int(match.group(2)) if match.group(2) else 0
    seconds = int(match.group(3)) if match.group(3) else 0

    return hours * 3600 + minutes * 60 + seconds

# Clean & prepare data
def clean_data(df):
    # Convert published date to datetime
    df["published_at"] = pd.to_datetime(df["published_at"], utc=True)

    # Remove videos with 0 views (avoid division errors)
    df = df[df["views"] > 0]

    df["duration_seconds"] = df["duration"].apply(parse_duration)
    df["duration_minutes"] = df["duration_seconds"] / 60

    return df


# Create metrics
def add_metrics(df):
    # Engagement rate
    df["engagement_rate"] = (df["likes"] + df["comments"]) / df["views"]

    # Create days_since_upload FIRST
    df["days_since_upload"] = (datetime.now(timezone.utc) - df["published_at"]).dt.days

    # Remove future dates
    df = df[df["days_since_upload"] >= 0]

    # Fix zero values BEFORE using it
    df["days_since_upload"] = df["days_since_upload"].replace(0, 1)

    # safe to use in calculations
    df["views_per_day"] = df["views"] / df["days_since_upload"]

    df["engagement_per_day"] = (df["likes"] + df["comments"]) / df["days_since_upload"]

    df["like_ratio"] = df["likes"] / df["views"]
    df["comment_ratio"] = df["comments"] / df["views"]

    return df

# Generate insights
def generate_insights(df):
    print("\n=== Top Videos by Views per Day ===")
    pd.options.display.float_format = '{:,.2f}'.format
    print(df.sort_values("views_per_day", ascending=False)[
        ["title", "views_per_day"]
    ].head(5))

    print("\n=== Top Videos by Engagement Rate ===")
    print(df.sort_values("engagement_rate", ascending=False)[
        ["title", "engagement_rate"]
    ].head(5))

# Main pipeline
def main():
    df = load_data()
    df = clean_data(df)
    df = add_metrics(df)

    print("\nProcessed Data Preview:")
    print(df.head())

    generate_insights(df)
    plot_views_vs_duration(df)
    plot_engagement_distribution(df)
    plot_views_vs_engagement(df)
    plot_top_videos(df)
    plot_recency_vs_performance(df)

if __name__ == "__main__":
    main()


