from pyrogram.raw import types as raw_types
from pyrogram.types import InlineKeyboardButton


def _extract_flags_and_icon(button: InlineKeyboardButton, raw_button) -> tuple[bool, bool, bool, int | None]:
    style_meta = getattr(button, "style", None)
    raw_style = getattr(raw_button, "style", None)

    def _has_flag(flag_name: str) -> bool:
        for source in (style_meta, button, raw_style):
            if source is None:
                continue
            if isinstance(source, dict) and bool(source.get(flag_name)):
                return True
            if bool(getattr(source, flag_name, False)):
                return True
        if isinstance(style_meta, str) and style_meta.lower() in (flag_name, flag_name.replace("bg_", "")):
            return True
        return False

    primary = _has_flag("bg_primary")
    danger = _has_flag("bg_danger")
    success = _has_flag("bg_success")

    icon_val = None
    for source in (style_meta, button, raw_style):
        if source is None:
            continue
        if isinstance(source, dict):
            icon_val = source.get("icon") or source.get("icon_custom_emoji_id")
        else:
            icon_val = getattr(source, "icon", None) or getattr(source, "icon_custom_emoji_id", None)
        if icon_val is not None:
            break

    if icon_val is not None:
        try:
            icon_val = int(icon_val)
        except (TypeError, ValueError):
            icon_val = None

    return primary, danger, success, icon_val


def install_button_style_adapter() -> None:
    if getattr(InlineKeyboardButton.write, "_koap_vc_adapted", False):
        return

    base_write = InlineKeyboardButton.write

    async def _adapted_write(self, client):
        raw_btn = await base_write(self, client)
        primary, danger, success, icon_id = _extract_flags_and_icon(self, raw_btn)

        if primary or danger or success or icon_id is not None:
            payload = {
                "bg_primary": primary,
                "bg_danger": danger,
                "bg_success": success,
            }
            if icon_id is not None:
                payload["icon"] = icon_id
            try:
                raw_btn.style = raw_types.KeyboardButtonStyle(**payload)
            except TypeError:
                pass

        return raw_btn

    _adapted_write._koap_vc_adapted = True
    InlineKeyboardButton.write = _adapted_write


def styled_button(
    text: str,
    callback_data: str | None = None,
    url: str | None = None,
    tone: str | None = None,
    custom_emoji_id: int | None = None,
) -> InlineKeyboardButton:
    args = {}
    if callback_data is not None:
        args["callback_data"] = callback_data
    elif url is not None:
        args["url"] = url

    btn = InlineKeyboardButton(text, **args)
    style_cfg: dict[str, object] = {}

    if tone == "primary":
        style_cfg["bg_primary"] = True
    elif tone == "danger":
        style_cfg["bg_danger"] = True
    elif tone == "success":
        style_cfg["bg_success"] = True

    if custom_emoji_id is not None:
        style_cfg["icon"] = int(custom_emoji_id)

    if style_cfg:
        btn.style = style_cfg

    return btn
