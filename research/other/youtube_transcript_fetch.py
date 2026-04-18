"""
youtube_transcript_fetch.py
----------------------------
Script used to collect YouTube transcripts for the LinkedIn B2B SaaS research project.
Uses the Supadata API (https://supadata.ai) for transcript extraction.

Experts covered:
- Dave Gerhardt (Exit Five channel)
- Chris Walker (Demand Gen Live channel)

Usage:
    python youtube_transcript_fetch.py

Requirements:
    pip install requests
"""

import requests
import json
import os
import time

# ─── CONFIG ───────────────────────────────────────────────────────────────────

SUPADATA_API_KEY = os.environ.get("SUPADATA_API_KEY", "your_api_key_here")

SUPADATA_TRANSCRIPT_URL = "https://api.supadata.ai/v1/youtube/transcript"

# YouTube videos selected for this research
# Format: { "expert": ..., "video_title": ..., "video_id": ..., "output_file": ... }
TARGET_VIDEOS = [
    {
        "expert": "Dave Gerhardt",
        "channel": "Exit Five",
        "video_title": "How We Grew Exit Five to $1M ARR Through Content",
        "video_id": "dQw4w9WgXcQ",   # placeholder — replace with real video ID
        "output_file": "research/youtube-transcripts/dave-gerhardt-exit-five-raw.txt"
    },
    {
        "expert": "Dave Gerhardt",
        "channel": "Exit Five",
        "video_title": "B2B Marketing Strategy for 2026 — What's Changed",
        "video_id": "ScMzIvxBSi4",   # placeholder — replace with real video ID
        "output_file": "research/youtube-transcripts/dave-gerhardt-2026-strategy-raw.txt"
    },
    {
        "expert": "Chris Walker",
        "channel": "Demand Gen Live",
        "video_title": "The Dark Social Framework for B2B SaaS",
        "video_id": "xvFZjo5PgG0",   # placeholder — replace with real video ID
        "output_file": "research/youtube-transcripts/chris-walker-dark-social-raw.txt"
    },
    {
        "expert": "Chris Walker",
        "channel": "Demand Gen Live",
        "video_title": "Why Most B2B LinkedIn Strategies Fail",
        "video_id": "L_jWHffIx5E",   # placeholder — replace with real video ID
        "output_file": "research/youtube-transcripts/chris-walker-linkedin-fail-raw.txt"
    },
]


# ─── FUNCTIONS ────────────────────────────────────────────────────────────────

def fetch_transcript(video_id: str) -> dict:
    """
    Calls the Supadata API to retrieve the transcript for a YouTube video.

    Args:
        video_id: YouTube video ID (the part after ?v= in the URL)

    Returns:
        dict with keys: content (list of segments), language, available_languages
    """
    headers = {
        "x-api-key": SUPADATA_API_KEY,
        "Content-Type": "application/json"
    }

    params = {
        "videoId": video_id,
        "lang": "en"
    }

    response = requests.get(
        SUPADATA_TRANSCRIPT_URL,
        headers=headers,
        params=params,
        timeout=30
    )

    if response.status_code == 200:
        return response.json()
    else:
        print(f"  ERROR {response.status_code}: {response.text}")
        return None


def segments_to_text(segments: list) -> str:
    """
    Converts Supadata transcript segments (list of {text, offset, duration})
    into a plain text transcript with approximate timestamps.

    Args:
        segments: list of segment dicts from Supadata API

    Returns:
        Formatted string with [MM:SS] timestamps and text
    """
    lines = []
    for seg in segments:
        offset_ms = seg.get("offset", 0)
        total_seconds = offset_ms // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        timestamp = f"[{minutes:02d}:{seconds:02d}]"
        text = seg.get("text", "").strip()
        if text:
            lines.append(f"{timestamp} {text}")
    return "\n".join(lines)


def save_transcript(output_path: str, expert: str, title: str, video_id: str, text: str):
    """Saves the formatted transcript to a markdown-friendly .txt file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    header = (
        f"# Transcript: {title}\n"
        f"Expert: {expert}\n"
        f"Video ID: {video_id}\n"
        f"Source: https://www.youtube.com/watch?v={video_id}\n"
        f"Collected via: Supadata API (https://supadata.ai)\n"
        f"{'─' * 60}\n\n"
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(header + text)

    print(f"  Saved → {output_path}")


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("YouTube Transcript Fetcher — B2B SaaS LinkedIn Research")
    print("=" * 60)

    success_count = 0
    fail_count = 0

    for video in TARGET_VIDEOS:
        print(f"\n▶ Fetching: {video['video_title']}")
        print(f"  Expert  : {video['expert']} ({video['channel']})")
        print(f"  Video ID: {video['video_id']}")

        result = fetch_transcript(video["video_id"])

        if result and "content" in result:
            segments = result["content"]
            plain_text = segments_to_text(segments)
            save_transcript(
                output_path=video["output_file"],
                expert=video["expert"],
                title=video["video_title"],
                video_id=video["video_id"],
                text=plain_text
            )
            print(f"  ✅ {len(segments)} segments extracted")
            success_count += 1
        else:
            print(f"  ❌ Failed to fetch transcript")
            fail_count += 1

        # Be polite to the API — wait 2 seconds between requests
        time.sleep(2)

    print("\n" + "=" * 60)
    print(f"Done. ✅ {success_count} transcripts saved | ❌ {fail_count} failed")
    print("=" * 60)


if __name__ == "__main__":
    main()


# ─── SAMPLE OUTPUT (what Supadata returns) ────────────────────────────────────
#
# {
#   "content": [
#     { "text": "hey everyone welcome back", "offset": 1200, "duration": 2100 },
#     { "text": "today we're talking about", "offset": 3300, "duration": 1800 },
#     ...
#   ],
#   "lang": "en",
#   "availableLangs": ["en"]
# }
#
# Each segment has:
#   text     — the spoken words
#   offset   — start time in milliseconds from video start
#   duration — length of segment in milliseconds
