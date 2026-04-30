import pandas as pd
from datetime import datetime
from datetime import datetime, timezone

# Load data
def load_data(filepath):
    df = pd.read_json(filepath)
    return df


# Clean & prepare data
def clean_data(df):
    # Convert published date to datetime
    df["published_at"] = pd.to_datetime(df["published_at"], utc=True)

    # Remove videos with 0 views (avoid division errors)
    df = df[df["views"] > 0]

    return df


# Create metrics
def add_metrics(df):
    # Engagement rate
    df["engagement_rate"] = (df["likes"] + df["comments"]) / df["views"]

    # Days since upload
    df["days_since_upload"] = (datetime.now(timezone.utc) - df["published_at"]).dt.days

    # Avoid division by zero
    df["days_since_upload"] = df["days_since_upload"].replace(0, 1)

    # Views per day importtant
    df["views_per_day"] = df["views"] / df["days_since_upload"]

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
    filepath = "data/youtube_data.json"

    df = load_data(filepath)
    df = clean_data(df)
    df = add_metrics(df)

    print("\nProcessed Data Preview:")
    print(df.head())

    generate_insights(df)


if __name__ == "__main__":
    main()


