import asyncio
from pyrogram import Client, idle

from koap_vc.engine import VoiceStreamEngine
from koap_vc.handlers import attach_all_handlers
from koap_vc.settings import load_settings
from koap_vc.ui.style_adapter import install_button_style_adapter


async def main() -> None:
    install_button_style_adapter()
    cfg = load_settings()

    bot = Client(
        name="koap_vc_bot",
        api_id=cfg.api_id,
        api_hash=cfg.api_hash,
        bot_token=cfg.bot_token,
        in_memory=True,
    )
    user_client = Client(
        name="koap_vc_user",
        api_id=cfg.api_id,
        api_hash=cfg.api_hash,
        session_string=cfg.user_session,
        in_memory=True,
    )

    engine = VoiceStreamEngine(user_client, cfg)
    attach_all_handlers(bot, engine)

    await bot.start()
    await user_client.start()
    await engine.boot()

    await idle()

    await bot.stop()
    await user_client.stop()


if __name__ == "__main__":
    asyncio.run(main())
