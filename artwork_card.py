import os
from typing import Any
from PIL import Image, ImageDraw, ImageFont, ImageOps


def format_view_metric(raw_views: Any) -> str:
    if raw_views is None or raw_views == "":
        return "Views: N/A"
    text = str(raw_views).strip()
    if text.lower().startswith("views:"):
        text = text.split(":", 1)[1].strip()
    cleaned = text.replace(",", "").replace(" ", "")
    try:
        count = int(float(cleaned))
    except (ValueError, TypeError):
        return f"Views: {text}"

    if count < 0:
        return "Views: N/A"
    if count >= 1_000_000_000:
        return f"Views: {count / 1_000_000_000:.1f}B"
    if count >= 1_000_000:
        return f"Views: {count / 1_000_000:.1f}M"
    if count >= 1_000:
        return f"Views: {count / 1_000:.1f}K"
    return f"Views: {count}"


class ArtworkCardBuilder:
    def __init__(self, out_dir: str = "runtime_cache"):
        self.out_dir = out_dir
        self.canvas_size = (1280, 720)
        self.font_large = ImageFont.load_default()
        self.font_med = ImageFont.load_default()
        self.font_small = ImageFont.load_default()

    def create_card(self, item: dict[str, Any], cover_file: str | None = None) -> str:
        os.makedirs(self.out_dir, exist_ok=True)
        w, h = self.canvas_size
        track_id = str(item.get("id") or "track")
        target = os.path.join(self.out_dir, f"card_{track_id}.png")

        canvas = Image.new("RGB", (w, h), (15, 23, 42))
        draw = ImageDraw.Draw(canvas)

        if cover_file and os.path.exists(cover_file):
            thumb = ImageOps.fit(Image.open(cover_file).convert("RGB"), (380, 380))
            canvas.paste(thumb, (70, 170))
        else:
            draw.rectangle((70, 170, 450, 550), fill=(30, 41, 59), outline=(56, 189, 248), width=2)

        title = str(item.get("title") or "Untitled Stream")[:50]
        source = str(item.get("source") or "YouTube")[:40]
        duration = str(item.get("duration") or "00:00")
        views_label = format_view_metric(item.get("views"))

        draw.text((490, 200), title, fill=(248, 250, 252), font=self.font_large)
        draw.text((490, 250), f"Source: {source}", fill=(125, 211, 252), font=self.font_med)
        draw.text((490, 295), f"Duration: {duration}", fill=(226, 232, 240), font=self.font_med)
        draw.text((490, 340), views_label, fill=(56, 189, 248), font=self.font_med)

        canvas.save(target, format="PNG")
        return target
