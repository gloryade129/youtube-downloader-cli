# YouTube Search & Multi-Format Downloader CLI System 🎵🎬

An intelligent, interactive command-line system built in Python to search YouTube using natural language prompts, refine queries via heuristic AI parsing, and download media into **MP3**, **MP4 (HD Video)**, **FLAC**, **M4A**, **WAV**, or **OPUS** formats with automatic ID3 tagging and album art cover embedding.

---

## 🌟 Features

- **Format Options**: Choose between MP3, MP4 HD Video, FLAC, M4A, WAV, or OPUS before downloading.
- **🤖 Built-in AI Search Refinement**: Parses natural language prompts (e.g. *"acoustic live hotel california eagles"* or *"latest Lex Fridman podcast"*), cleans stop words, extracts intent tags, and optimizes search terms for YouTube.
- **🎨 Interactive Rich CLI UI**: Beautiful terminal formatting with `rich` tables, `questionary` arrow-key menus, and real-time download progress bars.
- **🏷️ Auto-Embedding ID3 Metadata & Album Art**: Automatically embeds Title, Artist/Channel name, and downloaded YouTube cover thumbnails into MP3 audio files.
- **⚡ Direct CLI Commands**: Supports interactive mode as well as direct command-line arguments for quick searching and URL downloading.
- **⚙️ Configurable Defaults**: Remembers default output folder, default format, and search result limits.

---

## 🚀 Quick Setup

### 1. Requirements
- **Python**: 3.8+
- **ffmpeg** (Required for audio format extraction, MP3 conversion, and HD video merging):
  - On Windows (PowerShell): `winget install ffmpeg` or `choco install ffmpeg`
  - On macOS: `brew install ffmpeg`
  - On Linux (Ubuntu/Debian): `sudo apt install ffmpeg`

### 2. Installation
```bash
# Clone or navigate to the project directory
cd youtube_downloader_cli

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install package in editable mode
pip install -e .
```

---

## 💻 Usage

### 1. Interactive Session (Recommended)
Simply launch the CLI with no arguments to start the interactive session:
```bash
yt-downloader
# or
ytmp3
```
Flow:
1. **Step 1**: Choose target format (MP3, MP4, M4A, FLAC, etc.) from an interactive menu.
2. **Step 2**: Type your search query or natural language prompt.
3. **Step 3**: View the rule-based AI query refinement and formatted search results table.
4. **Step 4**: Select the video to download and watch the live progress bar.

### 2. Search & Download Command
```bash
yt-downloader search "acoustic live hotel california" --format mp3 --limit 5
yt-downloader search "python fastAPI tutorial" --format mp4
```

### 3. Direct URL Download
```bash
yt-downloader download "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --format mp3
```

### 4. Configuration
```bash
# View settings
yt-downloader config --show

# Change default download folder
yt-downloader config --set-dir "D:/Music/Downloads"

# Change default format
yt-downloader config --set-format "flac"
```

---

## 📁 Project Architecture

```
youtube_downloader_cli/
├── setup.py                    # Package packaging & console script definitions
├── requirements.txt            # Package dependencies
├── README.md                   # Documentation
└── yt_downloader/
    ├── __init__.py             # Module initialization
    ├── cli.py                  # CLI entrypoint & click subcommands
    ├── query_refiner.py        # Rule-based heuristic AI search parser
    ├── youtube_engine.py       # yt-dlp search & download wrapper
    ├── metadata_tagger.py      # Mutagen ID3 tag & album art embedder
    ├── ui.py                   # Rich tables, menus & progress bars
    └── config.py               # Settings manager & ffmpeg checker
```
