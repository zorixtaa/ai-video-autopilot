"""Autopilot script for generating AI news videos.

This module provides functions to automatically gather trending AI
stories, compose a script, generate a voice‑over using TTS and
create a simple video by combining a background image and the audio.
It relies on external services (Reddit JSON feeds for news and
Unsplash for images) that do not require API keys.  The final
composition of audio and image into a video uses ffmpeg.  Ensure
that ffmpeg is installed on your system for the video creation to
succeed.
"""

from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime
from typing import List, Dict, Optional

import requests
from gtts import gTTS
from bs4 import BeautifulSoup


def get_trending_topics(num_topics: int = 5) -> List[Dict[str, str]]:
    """Fetch trending AI topics from Reddit.

    This function queries the top posts of the day from the
    r/artificial subreddit, which frequently features AI‑related
    discussions and news.  Only the post titles and links are
    returned.

    Parameters
    ----------
    num_topics : int, optional
        The number of top posts to fetch (default is 5).

    Returns
    -------
    list of dict
        A list of dictionaries containing the title and URL of each
        top post.
    """
    url = f"https://www.reddit.com/r/artificial/top/.json?limit={num_topics}&t=day"
    headers = {"User-Agent": "Mozilla/5.0 (compatible; AI-Autopilot/1.0)"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        topics: List[Dict[str, str]] = []
        for post in data.get("data", {}).get("children", []):
            post_data = post.get("data", {})
            title = post_data.get("title")
            permalink = post_data.get("permalink")
            if not title or not permalink:
                continue
            topics.append({
                "title": title,
                "url": f"https://reddit.com{permalink}",
            })
        return topics
    except Exception:
        # Fallback: return an empty list if Reddit is unreachable
        return []


def generate_script(topics: List[Dict[str, str]]) -> str:
    """Compose the narration script from a list of topics.

    The script introduces the video, enumerates each story with its
    title and a generic invitation to learn more, and finishes with
    a closing statement.

    Parameters
    ----------
    topics : list of dict
        Topics returned by `get_trending_topics`.

    Returns
    -------
    str
        The full narration script.
    """
    lines: List[str] = ["Hello and welcome to today's AI news update."]
    if not topics:
        lines.append("Unfortunately, I could not retrieve the latest stories. Please check back later.")
    else:
        for idx, topic in enumerate(topics, start=1):
            title = topic.get("title", "")
            lines.append(f"Story {idx}: {title}.")
    lines.append("Thank you for watching. Don't forget to like and subscribe for more AI news!")
    return " \n".join(lines)


def generate_audio(script_text: str, audio_filename: str) -> None:
    """Create an audio file from text using gTTS.

    The file will be saved in MP3 format.  gTTS communicates with
    Google’s text‑to‑speech service; an internet connection is
    required.

    Parameters
    ----------
    script_text : str
        The narration text to convert to speech.
    audio_filename : str
        The path where the audio file should be saved.
    """
    tts = gTTS(text=script_text)
    tts.save(audio_filename)


def download_image(query: str, width: int, height: int, image_filename: str) -> None:
    """Download a random image from Unsplash matching a query.

    Uses the Unsplash source service which does not require an API key.
    An internet connection is required.  If the download fails, a
    fallback solid colour image is created instead.

    Parameters
    ----------
    query : str
        Query terms separated by commas (e.g. "ai,technology").
    width : int
        Desired image width in pixels.
    height : int
        Desired image height in pixels.
    image_filename : str
        The path where the image should be saved.
    """
    url = f"https://source.unsplash.com/random/{width}x{height}/?{query}"
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        with open(image_filename, "wb") as fh:
            fh.write(resp.content)
    except Exception:
        # If download fails, create a simple black image
        from PIL import Image

        img = Image.new("RGB", (width, height), color=(0, 0, 0))
        img.save(image_filename)


def combine_audio_image(image_filename: str, audio_filename: str, output_filename: str) -> None:
    """Combine a still image and an audio file into a video using ffmpeg.

    The video will have the same duration as the audio.  This function
    assumes `ffmpeg` is available in the system `PATH`.  If ffmpeg is
    missing or the command fails, a `RuntimeError` is raised.

    Parameters
    ----------
    image_filename : str
        Path to the background image.
    audio_filename : str
        Path to the MP3 audio file.
    output_filename : str
        Destination filename for the video.
    """
    # Construct an ffmpeg command that loops the image for the
    # duration of the audio and uses sensible defaults for encoding.
    command = [
        "ffmpeg",
        "-y",  # overwrite output file without asking
        "-loop", "1",
        "-i", image_filename,
        "-i", audio_filename,
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        output_filename,
    ]
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except FileNotFoundError:
        raise RuntimeError("ffmpeg executable not found. Please install ffmpeg and ensure it is in your PATH.")
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"ffmpeg failed: {exc.stderr.decode('utf-8', errors='ignore')}")


def run_autopilot(topics_override: Optional[List[str]] = None) -> str:
    """Run the full autopilot sequence.

    This function fetches trending topics (or uses the provided
    override), generates a narration script, creates a voice‑over,
    downloads a background image, and merges them into a video.  The
    output files are named with a timestamp to avoid collisions.

    Parameters
    ----------
    topics_override : list of str, optional
        If provided, these strings are used as the topics instead of
        pulling live data from Reddit.  Each item becomes a "Story" in
        the generated video.

    Returns
    -------
    str
        The path to the generated video file.
    """
    # Determine topics either from the override list or by querying Reddit
    if topics_override and len(topics_override) > 0:
        topics = [{"title": t, "url": ""} for t in topics_override]
    else:
        topics = get_trending_topics(num_topics=5)
    # Generate the narration script
    script_text = generate_script(topics)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    audio_filename = f"voice_{timestamp}.mp3"
    image_filename = f"background_{timestamp}.jpg"
    video_filename = f"output_{timestamp}.mp4"
    # Create audio
    generate_audio(script_text, audio_filename)
    # Download image
    download_image(query="ai,technology", width=1280, height=720, image_filename=image_filename)
    # Combine into video
    combine_audio_image(image_filename, audio_filename, video_filename)
    return os.path.abspath(video_filename)


if __name__ == "__main__":
    # When executed directly, run the autopilot with live data
    video_path = run_autopilot()
    print(f"Video generated at: {video_path}")
