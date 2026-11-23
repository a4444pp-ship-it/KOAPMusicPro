from pyrogram import Client, filters
from pyrogram.types import CallbackQuery

from koap_vc.engine import VoiceStreamEngine


def attach_action_handlers(bot: Client, engine: VoiceStreamEngine) -> None:
    @bot.on_callback_query(filters.regex(r"^vc:(pause|skip|stop):(-?\d+)$"))
    async def on_action(_, query: CallbackQuery):
        _, action, chat_raw = query.data.split(":", 2)
        chat_id = int(chat_raw)

        try:
            if action == "pause":
                await engine.calls.pause(chat_id)
                await query.answer("Paused", show_alert=False)
            elif action == "skip":
                engine.active_item.pop(chat_id, None)
                await engine.calls.leave_call(chat_id)
                await query.answer("Skipped", show_alert=False)
            elif action == "stop":
                engine.waiting_list.pop(chat_id, None)
                engine.active_item.pop(chat_id, None)
                await engine.calls.leave_call(chat_id)
                await query.answer("Stopped", show_alert=False)
        except Exception as exc:
            await query.answer(str(exc), show_alert=True)
