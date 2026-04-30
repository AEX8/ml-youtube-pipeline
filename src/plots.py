import matplotlib.pyplot as plt

def plot_views_vs_duration(df):
    plt.figure()

    plt.scatter(df["duration_minutes"], df["views_per_day"])
    plt.xlabel("Duration (minutes)")
    plt.ylabel("Views per Day")
    plt.title("Video Duration vs Views per Day")

    plt.show()

def plot_engagement_distribution(df):
    plt.figure()
    plt.hist(df["engagement_rate"], bins=10)
    plt.xlabel("Engagement Rate")
    plt.ylabel("Frequency")
    plt.title("Engagement Rate Distribution")
    plt.show()

def plot_views_vs_engagement(df):
    plt.figure()
    plt.scatter(df["views"], df["engagement_rate"])
    plt.xlabel("Views")
    plt.ylabel("Engagement Rate")
    plt.title("Views vs Engagement")
    plt.show()

def plot_top_videos(df):
    top = df.sort_values("views_per_day", ascending=False).head(5)

    plt.figure()
    plt.barh(top["title"], top["views_per_day"])
    plt.xlabel("Views per Day")
    plt.title("Top Performing Videos")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.show()

def plot_recency_vs_performance(df):
    plt.figure()
    plt.scatter(df["days_since_upload"], df["views_per_day"])
    plt.xlabel("Days Since Upload")
    plt.ylabel("Views per Day")
    plt.title("Recency vs Performance")
    plt.show()