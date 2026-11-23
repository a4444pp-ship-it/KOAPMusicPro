from pyrogram import Client
from koap_vc.engine import VoiceStreamEngine
from koap_vc.handlers.actions import attach_action_handlers
from koap_vc.handlers.playback import attach_playback_handlers


def attach_all_handlers(bot: Client, engine: VoiceStreamEngine) -> None:
    attach_playback_handlers(bot, engine)
    attach_action_handlers(bot, engine)
