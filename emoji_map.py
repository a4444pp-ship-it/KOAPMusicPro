# Custom emoji ID registry for KOAP VC.
# Replace None with integer custom emoji IDs as needed.

CUSTOM_EMOJI_MAP: dict[str, int | None] = {
    "play": None,
    "video": None,
    "pause": None,
    "resume": None,
    "skip": None,
    "stop": None,
    "queue": None,
    "views": None,
    "audio": None,
}

DEFAULT_ICONS: dict[str, str] = {
    "play": "▶",
    "video": "◉",
    "pause": "❚❚",
    "resume": "▶",
    "skip": "⏭",
    "stop": "■",
    "queue": "≡",
    "views": "◈",
    "audio": "♪",
}


def render_icon(key: str) -> str:
    emoji_id = CUSTOM_EMOJI_MAP.get(key)
    fallback = DEFAULT_ICONS.get(key, "•")
    if emoji_id:
        return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'
    return fallback
