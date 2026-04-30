import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def connect_db():
    conn = psycopg2.connect(
        dbname="youtube_pipeline",
        user="gayathwethmin",
        password=os.getenv("DB_PASSWORD"),
        host="localhost",
        port="5432"
    )
    return conn

def insert_videos(videos):
    conn = connect_db()
    cur = conn.cursor()

    for video in videos:
        cur.execute("""
            INSERT INTO videos (video_id, title, published_at, duration, views, likes, comments)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (video_id) DO NOTHING;
        """, (
            video["video_id"],
            video["title"],
            video["published_at"],
            video["duration"],
            video["views"],
            video["likes"],
            video["comments"]
        ))

    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    conn = connect_db()
    print("Connected successfully!")
    conn.close()