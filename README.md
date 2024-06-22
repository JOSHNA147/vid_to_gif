# vid_to_gif
# Video to GIF with Subtitles

This project is a Flask web application that allows users to upload a video file, transcribe it, segment the video and subtitles, generate GIFs with synchronized subtitles, and display the results.

## Features

- Upload video files in formats such as MP4, AVI, and MOV.
- Transcribe video using Whisper.
- Segment video and corresponding subtitles.
- Generate GIFs with synchronized subtitles.
- Display the generated GIFs on a results page.

## Prerequisites

- Python 3.x
- FFmpeg
- Whisper (or your transcription tool)

## Directory Structure

project-root/
│
├── app.py
├── templates/
│ ├── upload.html
│ └── results.html
├── uploads/
├── transcripts/
├── segments/
└── static/
└── outputs/


## Installation

1. **Clone the repository:**

```bash
git clone https://github.com/yourusername/video-to-gif-with-subtitles.git
cd video-to-gif-with-subtitles
2. **Create and activate a virtual environment:
'''bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
3. **Install the required packages:
pip install -r requirements.txt

