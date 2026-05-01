from googleapiclient.discovery import build
import json
import os
from dotenv import load_dotenv
from database import insert_videos

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
CHANNEL_ID = "UCDogdKl7t7NHzQ95aEwkdMw"     # Sidemen

youtube = build("youtube", "v3", developerKey=API_KEY)

# Get latest videos
video_ids = []
video_snippets = {}

next_page_token = None

while len(video_ids) < 100:
    request = youtube.search().list(
        part="snippet",
        channelId=CHANNEL_ID,
        maxResults=50,  # max allowed
        order="date",
        type="video",
        pageToken=next_page_token
    )

    response = request.execute()

    for item in response["items"]:
        if "videoId" not in item["id"]:
            continue
        video_id = item["id"]["videoId"]
        # avoid duplicates
        if video_id not in video_snippets:
            video_ids.append(video_id)
            video_snippets[video_id] = item["snippet"]

    next_page_token = response.get("nextPageToken")

    if not next_page_token:
        break

# avoid going over the limit
video_ids = list(dict.fromkeys(video_ids))
video_ids = video_ids[:100]

print(f"Fetched {len(video_ids)} video IDs")

def chunk_list(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]

# Get stats
videos_data = []

for batch in chunk_list(video_ids, 50):
    stats_response = youtube.videos().list(
        part="statistics,contentDetails",
        id=",".join(batch)
    ).execute()

    for item in stats_response["items"]:
        vid = item["id"]
        snippet = video_snippets.get(vid)

        if not snippet:
            continue

        videos_data.append({
            "video_id": vid,
            "title": snippet["title"],
            "published_at": snippet["publishedAt"],
            "duration": item["contentDetails"].get("duration", "PT0S"),
            "views": int(item["statistics"].get("viewCount", 0)),
            "likes": int(item["statistics"].get("likeCount", 0)),
            "comments": int(item["statistics"].get("commentCount", 0))
        })

print(f"Prepared {len(videos_data)} videos for insertion")

# save
with open("data/youtube_data.json", "w") as f:
    json.dump(videos_data, f, indent=2)

# save to databse
insert_videos(videos_data)
print("Data inserted into database successfully!")

print("Data saved successfully!")



