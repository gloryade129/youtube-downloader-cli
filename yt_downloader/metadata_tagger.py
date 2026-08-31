import os
import requests
from pathlib import Path
from typing import Optional
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, ID3NoHeaderError


def embed_metadata_and_artwork(
    file_path: str,
    title: str,
    artist: str,
    album: Optional[str] = None,
    thumbnail_url: Optional[str] = None
) -> bool:
    """
    Ensures proper ID3 tags and album cover art thumbnail are embedded into MP3 file.
    """
    if not os.path.exists(file_path) or not file_path.lower().endswith(".mp3"):
        return False

    try:
        # Load or create ID3 tags
        try:
            audio = ID3(file_path)
        except ID3NoHeaderError:
            audio = ID3()

        # Set text metadata
        audio["TIT2"] = TIT2(encoding=3, text=title)
        audio["TPE1"] = TPE1(encoding=3, text=artist)
        audio["TALB"] = TALB(encoding=3, text=album or artist)

        # Download thumbnail image if available and not already embedded
        if thumbnail_url and not any(isinstance(tag, APIC) for tag in audio.values()):
            try:
                res = requests.get(thumbnail_url, timeout=10)
                if res.status_code == 200:
                    audio["APIC"] = APIC(
                        encoding=3,
                        mime="image/jpeg",
                        type=3,  # Front cover
                        desc="Cover",
                        data=res.content,
                    )
            except Exception:
                pass  # Ignore network errors for image fetch

        audio.save(file_path)
        return True
    except Exception:
        return False
