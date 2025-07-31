# AI News Video Autopilot

This repository contains a simple application that automatically gathers trending
artificial intelligence (AI) news, generates a script, converts it to speech,
and compiles it into a video.  The goal of the project is to provide a fully
automated workflow for producing AI‑focused news videos that can be uploaded
to YouTube or similar video platforms.

## Features

* **Trending AI topics** – The `autopilot.py` script fetches the current top
  stories from the `r/artificial` subreddit on Reddit.  Each story title is
  used as a news item in the generated video.  You can customise the topics
  by editing the configuration file or by modifying the `get_trending_topics`
  function.
* **Script generation** – The script writes a short introduction, then
  enumerates each news story with its title and adds a closing statement.
* **Text‑to‑speech (TTS)** – Using the [gTTS](https://github.com/pndurette/gTTS)
  library, the generated script is converted into an MP3 audio file.  gTTS
  relies on Google Translate’s text‑to‑speech service and does not require an
  API key, making it a convenient and free TTS solution.
* **Random AI imagery** – A relevant background image is downloaded from
  Unsplash via the [`source.unsplash.com`](https://source.unsplash.com/) service,
  which supplies high‑quality photographs without the need for an API key.
* **Video assembly with ffmpeg** – The audio and image are combined into a
  video using `ffmpeg`.  The script assumes that `ffmpeg` is installed on
  your system; if it is not, you’ll need to install it separately.  The
  generated video has the same length as the voice‑over.
* **Admin dashboard** – A minimal Flask‑based dashboard provides a login page
  and a page for editing the list of topics and triggering the autopilot.
  Only an administrator can access the dashboard.

## Getting Started

These instructions assume you have Python 3.8+ installed on your machine.

### 1. Install dependencies

Install the required Python libraries:

```
pip install -r requirements.txt
```

Additionally, ensure that `ffmpeg` is available in your system `PATH`.  If
`ffmpeg` is not installed, download it from the [official site](https://ffmpeg.org/)
or install it using your package manager:

* On Ubuntu:
  ```
  sudo apt install ffmpeg
  ```
* On macOS (Homebrew):
  ```
  brew install ffmpeg
  ```

### 2. Configure the application

Edit `config.json` to adjust the administrator credentials and the topics you
want to track.  The default configuration looks like this:

```
{
  "admin_username": "admin",
  "admin_password": "changeme",
  "topics": ["AI research", "machine learning", "neural networks"]
}
```

The username and password are stored in plain text for simplicity.  In a
production environment you should store a hashed password instead.

### 3. Run the dashboard

Start the Flask development server:

```
python app.py
```

Navigate to `http://localhost:5000` in your browser.  Log in with the
administrator credentials defined in `config.json`.  From the dashboard you
can update the list of topics and trigger the autopilot to generate a new
video.

### 4. Generate a video via the command line

You can also run the autopilot directly without using the dashboard:

```
python autopilot.py
```

The script downloads the latest AI news stories, generates `voice.mp3`,
downloads a background image, and combines them into `output_video.mp4`.
The resulting video will be saved in the project root.

## License and Attributions

The photos used in the videos are provided by Unsplash via the
`source.unsplash.com` endpoint.  Unsplash pictures are free to use, but
crediting the photographer is appreciated.  The text‑to‑speech audio is
generated using gTTS, which sends the text to Google Translate’s service.  You
are responsible for complying with the terms of use of these services when
producing and distributing your videos.

This code is provided for educational purposes and does not guarantee
compliance with the terms of service of any external websites.  Use at your
own risk.
