import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    api_id: int
    api_hash: str
    bot_token: str
    user_session: str
    stream_api_url: str
    stream_api_key: str


def load_settings() -> Settings:
    return Settings(
        api_id=int(os.getenv("TG_API_ID", "0")),
        api_hash=os.getenv("TG_API_HASH", "").strip(),
        bot_token=os.getenv("TG_BOT_TOKEN", "").strip(),
        user_session=os.getenv("TG_USER_SESSION", "").strip(),
        stream_api_url=os.getenv("STREAM_API_URL", "https://host-repository.vercel.app").rstrip("/"),
        stream_api_key=os.getenv("STREAM_API_KEY", "").strip(),
    )
