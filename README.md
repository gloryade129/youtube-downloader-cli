# YouTube Search & Multi-Format Batch Downloader CLI 🎵🎬

An intelligent, interactive command-line system built in Python to search YouTube using natural language prompts, refine queries via heuristic AI parsing, and download media into **MP3**, **MP4 (HD Video)**, **FLAC**, **M4A**, **WAV**, or **OPUS** formats with automatic ID3 tagging and playlist batching.

---

## 📦 Simple 3-Step Installation Guide (For Anyone)

Anyone can install and run this CLI on their laptop in **3 simple steps**:

### Step 1: Clone Repository
Open terminal/PowerShell and run:
```bash
git clone https://github.com/gloryade129/youtube-downloader-cli.git
cd youtube-downloader-cli
```

### Step 2: Install
```bash
pip install -e .
pip install imageio-ffmpeg
```

### Step 3: Start Downloading!
```bash
yt
```
*(Or run `yt-downloader` or `ytmp3`)*

---

## 🎮 Usage Guide

### 1. Interactive Mode (Simplest)
Just type `yt` from any terminal:
- **Format Selection**: Choose between MP3, MP4 HD Video, FLAC, M4A, WAV, or OPUS.
- **Search Prompt / URL**: Enter any prompt (e.g. `acoustic live hotel california`) or paste any YouTube Playlist URL.
- **Selection**: Choose a video or pick `📦 BATCH MODE` to download multiple items/full seasons in one go.
- **Back Navigation**: Select `↩️ Back` or type `b` at any point to change query or format.

### 2. Direct Commands
- **Search & Download**: `yt search "acoustic live hotel california" --format mp3`
- **Direct URL / Playlist**: `yt download "https://www.youtube.com/playlist?list=..." --format mp4`
- **Settings**: `yt config --show` or `yt config --set-dir "D:/Movies"`

---

## 📁 Download Storage
All media files are saved directly onto your laptop at:
`C:\Users\<YourUsername>\Downloads\YouTube-Downloads`
