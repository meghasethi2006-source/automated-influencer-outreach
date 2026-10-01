import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")

INPUT_FILE = "data/processed/filtered_influencers.csv"
OUTPUT_FILE = "data/processed/enriched_influencers.csv"

CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"
PLAYLIST_ITEMS_URL = "https://www.googleapis.com/youtube/v3/playlistItems"
VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"


def get_uploads_playlist(channel_id):
    """
    Get the playlist ID containing a channel's uploaded videos.
    """

    params = {
        "part": "contentDetails",
        "id": channel_id,
        "key": API_KEY
    }

    response = requests.get(
    CHANNEL_URL,
    params=params,
    timeout=15
)
    response.raise_for_status()

    data = response.json()

    if not data.get("items"):
        return None

    return (
        data["items"][0]
        .get("contentDetails", {})
        .get("relatedPlaylists", {})
        .get("uploads")
    )


def get_recent_videos(playlist_id, max_results=5):
    """
    Get recent videos from a channel's uploads playlist.
    """

    params = {
        "part": "snippet,contentDetails",
        "playlistId": playlist_id,
        "maxResults": max_results,
        "key": API_KEY
    }

    response = requests.get(
    PLAYLIST_ITEMS_URL,
    params=params,
    timeout=15
)

    response.raise_for_status()

    data = response.json()

    videos = []

    for item in data.get("items", []):

        video_id = (
            item.get("contentDetails", {})
            .get("videoId")
        )

        title = (
            item.get("snippet", {})
            .get("title", "")
        )

        if video_id:
            videos.append({
                "video_id": video_id,
                "title": title
            })

    return videos


def get_video_statistics(video_ids):
    """
    Get statistics for a batch of videos.
    """

    if not video_ids:
        return []

    params = {
        "part": "statistics",
        "id": ",".join(video_ids),
        "key": API_KEY
    }

    response = requests.get(
    VIDEOS_URL,
    params=params,
    timeout=15
)

    response.raise_for_status()

    data = response.json()

    results = []

    for item in data.get("items", []):

        stats = item.get("statistics", {})

        results.append({
            "video_id": item["id"],
            "views": int(stats.get("viewCount", 0)),
            "likes": int(stats.get("likeCount", 0)),
            "comments": int(stats.get("commentCount", 0))
        })

    return results


def calculate_engagement(video_stats):
    """
    Calculate average engagement rate across recent videos.
    """

    rates = []

    for video in video_stats:

        views = video["views"]
        likes = video["likes"]
        comments = video["comments"]

        if views > 0:

            rate = (
                (likes + comments)
                / views
            ) * 100

            rates.append(rate)

    if not rates:
        return None

    return round(sum(rates) / len(rates), 2)


def calculate_averages(video_stats):
    """
    Calculate average views, likes and comments.
    """

    if not video_stats:
        return {
            "average_views": None,
            "average_likes": None,
            "average_comments": None
        }

    return {
        "average_views": round(
            sum(v["views"] for v in video_stats)
            / len(video_stats)
        ),

        "average_likes": round(
            sum(v["likes"] for v in video_stats)
            / len(video_stats)
        ),

        "average_comments": round(
            sum(v["comments"] for v in video_stats)
            / len(video_stats)
        )
    }


def detect_content_themes(description, video_titles):
    """
    Detect basic content themes using keywords.
    """

    text = (
        str(description) + " "
        + " ".join(video_titles)
    ).lower()

    themes = []

    keywords = {
        "Skincare": [
            "skincare",
            "skin",
            "acne",
            "serum",
            "moisturizer",
            "sunscreen"
        ],

        "Makeup": [
            "makeup",
            "foundation",
            "concealer",
            "lipstick",
            "eyeshadow"
        ],

        "Beauty": [
            "beauty",
            "glow",
            "glowing",
            "beauty tips"
        ],

        "Product Reviews": [
            "review",
            "reviews",
            "testing",
            "tested",
            "haul"
        ],

        "Routines": [
            "routine",
            "morning routine",
            "night routine"
        ],

        "Haircare": [
            "hair",
            "haircare",
            "shampoo",
            "hair growth"
        ]
    }

    for theme, words in keywords.items():

        if any(word in text for word in words):
            themes.append(theme)

    if not themes:
        themes.append("Beauty & Skincare")

    return ", ".join(themes)
  
def enrich_creator(creator):
    """
    Enrich one creator with recent video data.
    """

    channel_id = creator["channel_id"]

    print(f"Enriching: {creator['name']}")

    playlist_id = get_uploads_playlist(channel_id)

    if not playlist_id:
        creator["recent_video_count"] = 0
        creator["recent_video_titles"] = "Not Found"
        creator["average_views"] = None
        creator["average_likes"] = None
        creator["average_comments"] = None
        creator["engagement_rate"] = None
        creator["content_themes"] = "Not Found"
        creator["contact_email"] = "Not Found"

        return creator

    recent_videos = get_recent_videos(
        playlist_id,
        max_results=5
    )

    video_ids = [
        video["video_id"]
        for video in recent_videos
    ]

    video_stats = get_video_statistics(video_ids)

    averages = calculate_averages(video_stats)

    engagement_rate = calculate_engagement(video_stats)

    video_titles = [
        video["title"]
        for video in recent_videos
    ]

    # Store actual recent video titles for AI personalization
    creator["recent_video_titles"] = " | ".join(video_titles)

    themes = detect_content_themes(
        creator["description"],
        video_titles
    )

    creator["recent_video_count"] = len(video_stats)

    creator["average_views"] = averages["average_views"]

    creator["average_likes"] = averages["average_likes"]

    creator["average_comments"] = averages["average_comments"]

    creator["engagement_rate"] = engagement_rate

    creator["content_themes"] = themes

    # We will populate this later from public sources.
    creator["contact_email"] = "Not Found"

    return creator


def main():

    df = pd.read_csv(INPUT_FILE)

    # Only enrich qualified creators
    qualified = df[
        df["filter_status"] == "PASS"
    ].copy()

    print(
        f"Qualified creators to enrich: "
        f"{len(qualified)}"
    )

    enriched_creators = []

    for _, creator in qualified.iterrows():

        creator_data = creator.to_dict()

        try:
            enriched = enrich_creator(
                creator_data
            )

            enriched_creators.append(enriched)

        except requests.exceptions.RequestException as e:

            print(
                f"Could not enrich {creator_data['name']}: {e}"
            )

            creator_data["recent_video_count"] = 0
            creator_data["recent_video_titles"] = "Not Found"
            creator_data["average_views"] = None
            creator_data["average_likes"] = None
            creator_data["average_comments"] = None
            creator_data["engagement_rate"] = None
            creator_data["content_themes"] = "Not Found"
            creator_data["contact_email"] = "Not Found"

            enriched_creators.append(creator_data)

    # Create DataFrame AFTER all creators have been processed
    enriched_df = pd.DataFrame(
        enriched_creators
    )

    os.makedirs(
        "data/processed",
        exist_ok=True
    )

    enriched_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nEnrichment completed.")

    print(
        f"Saved {len(enriched_df)} enriched creators to:"
    )

    print(OUTPUT_FILE)

    print("\nColumns created:")
    print(enriched_df.columns.tolist())

    print("\nSample enriched data:")

    print(
        enriched_df[
            [
                "name",
                "subscriber_count",
                "average_views",
                "average_likes",
                "average_comments",
                "engagement_rate",
                "content_themes",
                "recent_video_titles",
                "contact_email"
            ]
        ].head(10).to_string(index=False)
    )


if __name__ == "__main__":
    main()

   


if __name__ == "__main__":
    main()