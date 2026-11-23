import asyncio
from dataclasses import dataclass
from typing import Optional
import aiohttp
import yt_dlp
from pyrogram import Client
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioQuality, MediaStream, VideoQuality

from koap_vc.settings import Settings


@dataclass
class StreamItem:
    media_id: str
    title: str
    duration: str
    duration_sec: int
    source: str
    cover_url: str
    views: Optional[int] = None
    video_enabled: bool = False
    requester: str = "User"


class VoiceStreamEngine:
    def __init__(self, user_client: Client, settings: Settings):
        self.user_client = user_client
        self.settings = settings
        self.calls = PyTgCalls(user_client)
        self.active_item: dict[int, StreamItem] = {}
        self.waiting_list: dict[int, list[StreamItem]] = {}

    async def boot(self) -> None:
        await self.calls.start()

    async def lookup_media(self, query: str, video_enabled: bool = False) -> StreamItem:
        def _fetch():
            opts = {
                "format": "bestaudio/best",
                "noplaylist": True,
                "quiet": True,
                "no_warnings": True,
            }
            search_target = query if query.startswith(("http://", "https://")) else f"ytsearch1:{query}"
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(search_target, download=False)
                if "entries" in info and info["entries"]:
                    info = info["entries"][0]
                sec = int(info.get("duration") or 0)
                mins, secs = divmod(sec, 60)
                media_id = str(info.get("id") or "media")
                cover = info.get("thumbnail") or f"https://i.ytimg.com/vi/{media_id}/hqdefault.jpg"
                return StreamItem(
                    media_id=media_id,
                    title=str(info.get("title") or "Untitled Stream"),
                    duration=f"{mins:02d}:{secs:02d}",
                    duration_sec=sec,
                    source=str(info.get("uploader") or info.get("channel") or "Unknown"),
                    cover_url=cover,
                    views=info.get("view_count"),
                    video_enabled=video_enabled,
                )

        return await asyncio.to_thread(_fetch)

    async def resolve_stream_source(self, item: StreamItem) -> str:
        mode = "video" if item.video_enabled else "audio"
        fallback_url = (
            f"{self.settings.stream_api_url}/api/{mode}/{item.media_id}"
            f"?key={self.settings.stream_api_key}&redirect=1"
        )
        if not self.settings.stream_api_url:
            return fallback_url

        endpoint = f"{self.settings.stream_api_url}/api/{mode}/{item.media_id}"
        headers = {"X-API-Key": self.settings.stream_api_key} if self.settings.stream_api_key else {}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status == 200:
                        payload = await resp.json()
                        if payload.get("ok") and payload.get("url"):
                            return str(payload["url"])
        except Exception:
            pass
        return fallback_url

    async def enqueue_or_start(self, chat_id: int, item: StreamItem) -> tuple[bool, int]:
        self.waiting_list.setdefault(chat_id, [])

        if chat_id not in self.active_item:
            self.active_item[chat_id] = item
            source_url = await self.resolve_stream_source(item)
            stream = MediaStream(
                source_url,
                audio_parameters=AudioQuality.HIGH,
                video_parameters=VideoQuality.HD_720p if item.video_enabled else None,
                video_flags=MediaStream.Flags.IGNORE if not item.video_enabled else MediaStream.Flags.AUTO_DETECT,
            )
            await self.calls.play(chat_id, stream)
            return True, 0

        self.waiting_list[chat_id].append(item)
        return False, len(self.waiting_list[chat_id])
