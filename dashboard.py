import streamlit as st
import pandas as pd
from datetime import datetime, timezone
import re
from src.database import fetch_videos

# Page Config
st.set_page_config(page_title="YouTube Analytics", layout="wide")

st.title("YouTube Analytics Dashboard")

# Load Data
@st.cache_data
def load_data():
    rows, colnames = fetch_videos()
    df = pd.DataFrame(rows, columns=colnames)
    return df

df = load_data()

# Parse Duration
def parse_duration(duration):
    pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
    match = re.match(pattern, duration)

    hours = int(match.group(1)) if match.group(1) else 0
    minutes = int(match.group(2)) if match.group(2) else 0
    seconds = int(match.group(3)) if match.group(3) else 0

    return hours * 3600 + minutes * 60 + seconds

# Data Processing
def process_data(df):
    df["published_at"] = pd.to_datetime(df["published_at"], utc=True)
    df = df[df["views"] > 0]

    # Duration
    df["duration_seconds"] = df["duration"].apply(parse_duration)
    df["duration_minutes"] = df["duration_seconds"] / 60

    # Time metrics
    df["days_since_upload"] = (datetime.now(timezone.utc) - df["published_at"]).dt.days
    df = df[df["days_since_upload"] >= 0]
    df["days_since_upload"] = df["days_since_upload"].replace(0, 1)

    # Performance metrics
    df["views_per_day"] = df["views"] / df["days_since_upload"]
    df["engagement_rate"] = (df["likes"] + df["comments"]) / df["views"]

    # Short titles for display
    df["short_title"] = df["title"].str.slice(0, 40)

    return df

df = process_data(df)

# Sidebar Filters
st.sidebar.header("Filters")

min_views = st.sidebar.slider(
    "Minimum Views",
    0,
    int(df["views"].max()),
    0
)

filtered_df = df[df["views"] >= min_views]

# Key Metrics
st.subheader("Key Metrics")

col1, col2, col3 = st.columns(3)

col1.metric("Total Videos", len(filtered_df))
col2.metric("Average Views", int(filtered_df["views"].mean()))
col3.metric("Avg Engagement Rate", f"{filtered_df['engagement_rate'].mean():.4f}")

# Top Videos
st.subheader("Top Performing Videos")

top_videos = filtered_df.sort_values("views_per_day", ascending=False).head(5)
st.dataframe(top_videos[["title", "views_per_day", "engagement_rate"]])

# Charts
# Duration vs Performance
st.subheader("Duration vs Views per Day")
st.scatter_chart(filtered_df[["duration_minutes", "views_per_day"]])

# Views vs Engagement
st.subheader("Views vs Engagement Rate")
st.scatter_chart(filtered_df[["views", "engagement_rate"]])

# Recency vs Performance
st.subheader("Recency vs Performance")
st.scatter_chart(filtered_df[["days_since_upload", "views_per_day"]])

# Raw Data
st.subheader("Raw Data")
st.dataframe(filtered_df)