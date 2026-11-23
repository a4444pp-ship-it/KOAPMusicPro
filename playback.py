import os
import aiohttp
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, Message

from koap_vc.engine import VoiceStreamEngine
from koap_vc.media.artwork_card import ArtworkCardBuilder, format_view_metric
from koap_vc.ui.emoji_map import CUSTOM_EMOJI_MAP, render_icon
from koap_vc.ui.style_adapter import styled_button

card_builder = ArtworkCardBuilder()


def _controls_markup(chat_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                styled_button(
                    "Pause",
                    callback_data=f"vc:pause:{chat_id}",
                    tone="primary",
                    custom_emoji_id=CUSTOM_EMOJI_MAP.get("pause"),
                ),
                styled_button(
                    "Skip",
                    callback_data=f"vc:skip:{chat_id}",
                    tone="success",
                    custom_emoji_id=CUSTOM_EMOJI_MAP.get("skip"),
                ),
            ],
            [
                styled_button(
                    "Stop",
                    callback_data=f"vc:stop:{chat_id}",
                    tone="danger",
                    custom_emoji_id=CUSTOM_EMOJI_MAP.get("stop"),
                ),
            ],
        ]
    )


async def _fetch_cover(url: str, dest: str) -> str | None:
    os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status == 200:
                    with open(dest, "wb") as f:
                        f.write(await resp.read())
                    return dest
    except Exception:
        pass
    return None


def attach_playback_handlers(bot: Client, engine: VoiceStreamEngine) -> None:
    @bot.on_message(filters.command(["stream", "vstream"]) & filters.group)
    async def on_stream(_, message: Message):
        query = " ".join(message.command[1:]).strip()
        if not query and message.reply_to_message:
            query = message.reply_to_message.text or message.reply_to_message.caption or ""
        if not query:
            await message.reply_text(f"{render_icon('audio')} Provide a song title or link.")
            return

        video_enabled = message.command[0].lower() == "vstream"
        progress = await message.reply_text(f"{render_icon('queue')} Searching stream...")

        item = await engine.lookup_media(query, video_enabled=video_enabled)
        item.requester = message.from_user.mention if message.from_user else "Member"

        started, position = await engine.enqueue_or_start(message.chat.id, item)
        cover_path = await _fetch_cover(item.cover_url, f"runtime_cache/raw_{item.media_id}.jpg")
        card_path = card_builder.create_card(
            {
                "id": item.media_id,
                "title": item.title,
                "source": item.source,
                "duration": item.duration,
                "views": item.views,
            },
            cover_file=cover_path,
        )

        icon_head = render_icon("video") if video_enabled else render_icon("play")
        status_label = "Now Streaming" if started else f"Queued #{position}"
        caption = (
            f"{icon_head} <b>{status_label}</b>\n"
            f"{render_icon('audio')} <b>Title:</b> {item.title}\n"
            f"{render_icon('queue')} <b>Duration:</b> {item.duration} | "
            f"{render_icon('views')} <b>{format_view_metric(item.views)}</b>\n"
            f"{render_icon('play')} <b>By:</b> {item.requester}"
        )

        await progress.delete()
        await message.reply_photo(
            photo=card_path,
            caption=caption,
            reply_markup=_controls_markup(message.chat.id),
        )
