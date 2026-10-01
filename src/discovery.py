import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
print("API key loaded:", bool(API_KEY))
SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"


def search_channels(query, max_results=50):
    """Find YouTube channels related to a niche."""

    params = {
        "part": "snippet",
        "q": query,
        "type": "channel",
        "maxResults": max_results,
        "key": API_KEY
    }

    response = requests.get(SEARCH_URL, params=params)
    response.raise_for_status()

    data = response.json()

    channels = []

    for item in data.get("items", []):
        channels.append({
            "channel_id": item["snippet"]["channelId"],
            "name": item["snippet"]["title"],
            "description": item["snippet"]["description"],
            "profile_url": (
                f"https://www.youtube.com/channel/"
                f"{item['snippet']['channelId']}"
            )
        })

    return channels


def get_channel_stats(channel_ids):
    """Get subscriber count and channel statistics."""

    params = {
        "part": "statistics,snippet",
        "id": ",".join(channel_ids),
        "key": API_KEY
    }

    response = requests.get(CHANNEL_URL, params=params)
    response.raise_for_status()

    data = response.json()

    stats = {}

    for item in data.get("items", []):
        stats[item["id"]] = {
            "subscriber_count": int(
                item["statistics"].get("subscriberCount", 0)
            ),
            "view_count": int(
                item["statistics"].get("viewCount", 0)
            ),
            "video_count": int(
                item["statistics"].get("videoCount", 0)
            )
        }

    return stats


def discover_influencers():
    """Discover and enrich YouTube beauty/skincare creators."""

    queries = [
        "beauty skincare",
        "skincare routine",
        "makeup beauty",
        "skincare tips"
    ]

    all_channels = []

    for query in queries:
        print(f"Searching: {query}")

        channels = search_channels(query, max_results=50)
        all_channels.extend(channels)

    # Remove duplicate channels
    unique_channels = {}

    for channel in all_channels:
        unique_channels[channel["channel_id"]] = channel

    channels = list(unique_channels.values())

    print(f"\nUnique channels found: {len(channels)}")

    # Get statistics in batches of 50
    channel_stats = {}

    for i in range(0, len(channels), 50):

        batch = channels[i:i + 50]

        ids = [channel["channel_id"] for channel in batch]

        stats = get_channel_stats(ids)

        channel_stats.update(stats)

    # Combine channel information + statistics
    results = []

    for channel in channels:

        channel_id = channel["channel_id"]

        stats = channel_stats.get(channel_id, {})

        results.append({
            "name": channel["name"],
            "platform": "YouTube",
            "profile_url": channel["profile_url"],
            "channel_id": channel_id,
            "description": channel["description"],
            "subscriber_count": stats.get("subscriber_count"),
            "view_count": stats.get("view_count"),
            "video_count": stats.get("video_count"),
            "category": "Beauty & Skincare"
        })

    return results


if __name__ == "__main__":

    influencers = discover_influencers()

    df = pd.DataFrame(influencers)
    os.makedirs("data/raw", exist_ok=True)

    output_path = "data/raw/discovered_influencers.csv"

    df.to_csv(output_path, index=False)

    print(f"\nSaved {len(df)} influencers to:")
    print(output_path)

    print("\nFirst 10 influencers:")
    print(df.head(10).to_string(index=False))