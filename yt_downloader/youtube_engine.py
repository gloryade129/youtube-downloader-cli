import os
import re
import yt_dlp
from typing import List, Dict, Any, Callable, Optional


def format_duration(seconds: Optional[int]) -> str:
    """Format duration in seconds to HH:MM:SS or MM:SS."""
    if not seconds:
        return "N/A"
    seconds = int(seconds)
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def format_views(views: Optional[int]) -> str:
    """Format view count to human-readable format (e.g. 1.2M, 450K)."""
    if not views:
        return "N/A"
    if views >= 1_000_000:
        return f"{views / 1_000_000:.1f}M"
    elif views >= 1_000:
        return f"{views / 1_000:.1f}K"
    return str(views)


def search_youtube(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Search YouTube using yt-dlp and return list of result dicts.
    """
    ydl_opts = {
        "extract_flat": "in_playlist",
        "quiet": True,
        "no_warnings": True,
        "default_search": f"ytsearch{limit}",
    }

    results = []
    search_query = f"ytsearch{limit}:{query}"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(search_query, download=False)
        if not info or "entries" not in info:
            return []

        for entry in info["entries"]:
            if not entry:
                continue
            
            # Fetch detailed duration & view count if available
            duration = entry.get("duration")
            views = entry.get("view_count")
            uploader = entry.get("uploader") or entry.get("channel") or "Unknown Channel"
            title = entry.get("title") or "Untitled Video"
            url = entry.get("url") or entry.get("webpage_url") or f"https://www.youtube.com/watch?v={entry.get('id')}"
            thumbnail = entry.get("thumbnail") or (entry.get("thumbnails")[0]["url"] if entry.get("thumbnails") else "")
            
            results.append({
                "id": entry.get("id", ""),
                "title": title,
                "uploader": uploader,
                "duration": format_duration(duration),
                "views": format_views(views),
                "url": url,
                "thumbnail": thumbnail,
                "raw_duration": duration or 0,
            })

    return results


def download_media(
    url: str,
    output_dir: str,
    target_format: str = "mp3",
    ffmpeg_path: Optional[str] = None,
    progress_hook: Optional[Callable[[Dict[str, Any]], None]] = None
) -> Dict[str, Any]:
    """
    Download video or audio from YouTube URL into the target format.
    """
    os.makedirs(output_dir, exist_ok=True)
    target_format = target_format.lower()

    ydl_opts: Dict[str, Any] = {
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        "nooverwrites": True,
        "download_archive": os.path.join(output_dir, ".downloaded_history.txt"),
        "restrictfilenames": False,
        "retries": 15,
        "fragment_retries": 15,
        "file_access_retries": 15,
        "continuedl": True,
        "socket_timeout": 30,
        "http_chunk_size": 10485760,
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web"],
                "player_skip": ["js", "configs"],
            }
        },
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        },
    }

    if ffmpeg_path:
        ydl_opts["ffmpeg_location"] = ffmpeg_path

    if progress_hook:
        ydl_opts["progress_hooks"] = [progress_hook]

    audio_formats = ["mp3", "m4a", "flac", "wav", "opus", "aac"]

    if target_format in audio_formats:
        if ffmpeg_path:
            ydl_opts["format"] = "bestaudio/best"
            postprocessors = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": target_format,
                    "preferredquality": "192",
                },
                {"key": "FFmpegMetadata"},
            ]
            if target_format in ["mp3", "m4a"]:
                ydl_opts["writethumbnail"] = True
                postprocessors.append({"key": "EmbedThumbnail"})
            ydl_opts["postprocessors"] = postprocessors
        else:
            # Without ffmpeg, download native pre-extracted audio format
            ydl_opts["format"] = "bestaudio[ext=m4a]/bestaudio/best"
    else:
        # Video format (MP4)
        if ffmpeg_path:
            ydl_opts["format"] = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
            ydl_opts["postprocessors"] = [
                {"key": "FFmpegVideoConvertor", "preferedformat": "mp4"},
                {"key": "FFmpegMetadata"},
            ]
        else:
            # Without ffmpeg, YouTube cannot merge separate streams.
            # We MUST download a pre-merged single stream containing both video & audio!
            ydl_opts["format"] = "b/best"



    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        
        # Adjust extension after postprocessor extraction
        base, _ = os.path.splitext(filename)
        expected_filepath = f"{base}.{target_format}"
        if not os.path.exists(expected_filepath) and os.path.exists(filename):
            expected_filepath = filename

        return {
            "title": info.get("title"),
            "filepath": expected_filepath,
            "format": target_format,
            "uploader": info.get("uploader"),
        }


def is_playlist_url(url_or_query: str) -> bool:
    """Check if input is a YouTube playlist URL or video link containing list parameter."""
    s = url_or_query.strip()
    if s.startswith("http://") or s.startswith("https://") or s.startswith("www."):
        if "list=" in s or "playlist" in s.lower():
            return True
    return "list=" in s or "playlist" in s.lower()


def fetch_playlist_info(playlist_url: str) -> Dict[str, Any]:
    """
    Fetch playlist metadata and all entries/episodes from a YouTube playlist URL.
    """
    ydl_opts = {
        "extract_flat": True,
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False)
        if not info:
            return {"title": "Playlist", "entries": []}

        playlist_title = info.get("title") or "YouTube Playlist"
        entries = []
        raw_entries = info.get("entries") or []

        for idx, entry in enumerate(raw_entries, 1):
            if not entry:
                continue
            title = entry.get("title") or f"Episode {idx}"
            url = entry.get("url") or entry.get("webpage_url") or f"https://www.youtube.com/watch?v={entry.get('id')}"
            duration = entry.get("duration")
            uploader = entry.get("uploader") or entry.get("channel") or info.get("uploader") or "Playlist Channel"
            thumbnail = entry.get("thumbnail") or ""

            entries.append({
                "id": entry.get("id", ""),
                "title": title,
                "uploader": uploader,
                "duration": format_duration(duration),
                "views": "N/A",
                "url": url,
                "thumbnail": thumbnail,
                "episode_index": idx,
            })

        return {
            "title": playlist_title,
            "entries": entries
        }

