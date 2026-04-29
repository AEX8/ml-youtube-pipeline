from googleapiclient.discovery import build
import json
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
CHANNEL_ID = "UCDogdKl7t7NHzQ95aEwkdMw"     # Sidemen

youtube = build("youtube", "v3", developerKey=API_KEY)

# Get latest videos
search_response = youtube.search().list(
    part="snippet",
    channelId=CHANNEL_ID,
    maxResults=10,
    order="date",
    type="video"   # only videos
).execute()

video_ids = []
video_snippets = {}

for item in search_response["items"]:
    video_id = item["id"]["videoId"]
    video_ids.append(video_id)
    video_snippets[video_id] = item["snippet"]

# Get stats
stats_response = youtube.videos().list(
    part="statistics,contentDetails",
    id=",".join(video_ids)
).execute()

videos_data = []

# Combine clean data
for item in stats_response["items"]:
    vid = item["id"]
    snippet = video_snippets[vid]

    videos_data.append({
        "video_id": vid,
        "title": snippet["title"],
        "published_at": snippet["publishedAt"],
        "views": int(item["statistics"].get("viewCount", 0)),
        "likes": int(item["statistics"].get("likeCount", 0)),
        "comments": int(item["statistics"].get("commentCount", 0))
    })

# Save
with open("youtube_data.json", "w") as f:
    json.dump(videos_data, f, indent=2)

print("Data saved successfully!")