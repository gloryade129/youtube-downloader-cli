import json
import os
import shutil
from pathlib import Path

CONFIG_FILE = Path.home() / ".yt_downloader_config.json"

DEFAULT_CONFIG = {
    "download_dir": str(Path.home() / "Downloads" / "YouTube-Downloads"),
    "default_format": "mp3",
    "audio_quality": "192",
    "search_limit": 5,
    "embed_metadata": True,
    "embed_thumbnail": True,
}


def load_config() -> dict:
    """Load configuration from JSON file or return defaults if not found."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                config = DEFAULT_CONFIG.copy()
                config.update(data)
                return config
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()


def save_config(config: dict) -> bool:
    """Save configuration to JSON file."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        return True
    except Exception:
        return False


def check_ffmpeg() -> tuple[bool, str]:
    """Check if ffmpeg executable is available in system PATH or via imageio_ffmpeg."""
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        return True, ffmpeg_path
    
    # Try built-in imageio_ffmpeg binary
    try:
        import imageio_ffmpeg
        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
        if ffmpeg_bin and os.path.exists(ffmpeg_bin):
            return True, ffmpeg_bin
    except Exception:
        pass

    # Check common Windows locations
    common_paths = [
        Path("C:/ffmpeg/bin/ffmpeg.exe"),
        Path("C:/Program Files/ffmpeg/bin/ffmpeg.exe"),
        Path(os.path.expanduser("~") + "/ffmpeg/bin/ffmpeg.exe"),
        Path(os.path.expanduser("~") + "/AppData/Local/bin/ffmpeg.exe"),
    ]
    for p in common_paths:
        if p.exists():
            return True, str(p)
            
    return False, ""

