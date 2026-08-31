import re
from typing import NamedTuple, List, Optional


class RefinedQuery(NamedTuple):
    raw_prompt: str
    cleaned_query: str
    suggested_format: Optional[str]
    tags_detected: List[str]
    explanation: str


# Keyword rules for intent detection
FORMAT_MAP = {
    "mp3": ["mp3", "audio", "song", "track", "music", "podcast audio"],
    "mp4": ["mp4", "video", "clip", "mv", "movie", "film", "watch", "hd video", "4k"],
    "flac": ["flac", "lossless", "high res audio"],
    "m4a": ["m4a", "aac", "apple audio"],
    "wav": ["wav", "uncompressed"],
}

INTENT_KEYWORDS = {
    "live": ["live", "concert", "performance", "in concert", "live performance", "live version"],
    "acoustic": ["acoustic", "unplugged"],
    "remix": ["remix", "edited", "club mix", "extended mix"],
    "official": ["official", "official music video", "official video", "vevo"],
    "lyric": ["lyric", "lyrics", "lyric video"],
    "cover": ["cover", "tribute"],
    "podcast": ["podcast", "interview", "episode", "full episode", "talk"],
    "instrumental": ["instrumental", "karaoke", "no vocals"],
    "clean": ["clean", "radio edit"],
}

STOP_WORDS = {
    "download", "get", "me", "the", "a", "an", "for", "please", "search", "find",
    "version", "format", "into", "to", "in", "with", "best", "high",
    "quality", "full", "hd", "4k", "1080p", "free"
}



def refine_query(raw_prompt: str, current_format: str = "mp3") -> RefinedQuery:
    """
    Intelligently parses natural language prompts using rule-based heuristics.
    Returns an optimized search query string, detected tags, suggested format, and explanation.
    """
    prompt_lower = raw_prompt.strip().lower()
    
    # 1. Detect format intent
    detected_format = None
    for fmt, keywords in FORMAT_MAP.items():
        if any(re.search(r'\b' + re.escape(kw) + r'\b', prompt_lower) for kw in keywords):
            detected_format = fmt
            break

    # 2. Detect version & style tags
    detected_tags = []
    for tag, keywords in INTENT_KEYWORDS.items():
        if any(re.search(r'\b' + re.escape(kw) + r'\b', prompt_lower) for kw in keywords):
            detected_tags.append(tag)

    # 3. Clean query string
    words = re.findall(r'\w+', prompt_lower)
    filtered_words = []
    
    # Preserve important terms even if in stop words if they form core names
    for word in words:
        if word not in STOP_WORDS or word in detected_tags:
            filtered_words.append(word)

    # If filtering removed everything, fall back to original prompt
    if not filtered_words:
        cleaned_query = raw_prompt
    else:
        # Re-capitalize words smartly for search accuracy
        cleaned_query = " ".join([w.capitalize() for w in filtered_words])

    # 4. Generate AI explanation string
    explanation_parts = []
    if detected_tags:
        explanation_parts.append(f"Detected intent tags: [{', '.join(detected_tags)}]")
    if detected_format and detected_format != current_format:
        explanation_parts.append(f"Detected format preference: {detected_format.upper()}")
    
    if explanation_parts:
        explanation = " -> ".join(explanation_parts)
    else:
        explanation = "Cleaned and optimized keywords for YouTube search."

    return RefinedQuery(
        raw_prompt=raw_prompt,
        cleaned_query=cleaned_query,
        suggested_format=detected_format or current_format,
        tags_detected=detected_tags,
        explanation=explanation
    )
