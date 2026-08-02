from __future__ import annotations

import html
import logging
import re
import time

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from .catalog import gameplay_details, localized_card_fields, rarity_appearance_percentage
from .database import Database

logger = logging.getLogger(__name__)

BACK_LABEL = "↩️ رجوع"
ARABIC_COMMANDS = {
    "المتجر": "shop",
    "بطاقاتي": "collection",
    "رصيدي": "balance",
    "مساعدة": "help",
    "شراء": "buy",
    "الدعم": "support",
    "تحويل": "transfer",
}


def _display_name(update: Update) -> str:
    user = update.effective_user
    return user.full_name if user else "جامع بطاقات"


def _db(context: ContextTypes.DEFAULT_TYPE) -> Database:
    return context.application.bot_data["database"]


def _settings(context: ContextTypes.DEFAULT_TYPE):
    return context.application.bot_data["settings"]


def _ensure_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user:
        _db(context).ensure_user(
            update.effective_user.id,
            _display_name(update),
            update.effective_user.username,
        )


def _localized_card(card: dict) -> tuple[str, str, str, str]:
    return localized_card_fields(card["card_id"])


def _main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🛒 المتجر", callback_data="menu:shop"),
                InlineKeyboardButton("📚 مجموعتي", callback_data="menu:collection"),
            ],
            [
                InlineKeyboardButton("🪙 رصيدي", callback_data="menu:balance"),
                InlineKeyboardButton("❓ المساعدة", callback_data="menu:help"),
            ],
        ]
    )


def _back_keyboard(destination: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(BACK_LABEL, callback_data=destination)]]
    )


def _main_menu_text() -> str:
    return (
        "\u200f<b>مرحبًا بك في متجر البطاقات!</b>\n\n"
        "\u200fكوّن مجموعتك من متجر يتغير كل ساعة.\n\n"
        "\u200fاختر من القائمة:"
    )


def _help_text() -> str:
    return (
        "\u200f<b>دليل الأوامر</b>\n\n"
        "\u200f<b>الأوامر العربية</b>\n"
        "\u200f/المتجر — فتح متجر البطاقات\n"
        "\u200f/بطاقاتي — عرض مجموعتي\n"
        "\u200f/رصيدي — عرض رصيدي\n"
        "\u200f/مساعدة — عرض قائمة المساعدة\n"
        "\u200f/شراء &lt;معرّف البطاقة&gt; [الكمية] — شراء بطاقة\n"
        "\u200f/الدعم — التواصل مع مالك البوت\n\n"
        "\u200f/تحويل @اسم_المستخدم المبلغ — تحويل العملات\n\n"
        "\u200f<b>الأوامر الإنجليزية</b>\n"
        "\u200f/shop — عرض بطاقات هذه الساعة\n"
        "\u200f/buy &lt;معرّف البطاقة&gt; [الكمية] — شراء بطاقة\n"
        "\u200f/collection — عرض مجموعتك\n"
        "\u200f/balance — عرض رصيدك\n"
        "\u200f/help — عرض دليل الأوامر\n\n"
        "\u200fيمكنك أيضًا استخدام أزرار المتجر لعرض التفاصيل أو الشراء."
    )


async def arabic_command_router(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle Arabic slash commands even when Telegram omits command entities.

    The MessageHandler fallback is useful in groups and clients where the Bot
    API's command entity only recognizes Latin command names.
    """
    message = update.effective_message
    text = message.text if message else ""
    match = re.match(
        r"^/(المتجر|بطاقاتي|رصيدي|مساعدة|شراء|الدعم|تحويل)(?:@([A-Za-z0-9_]+))?(?:\s+|$)",
        text or "",
    )
    if not match:
        return
    command = ARABIC_COMMANDS[match.group(1)]
    arguments = (text[match.end():] if text else "").split()
    old_args = getattr(context, "args", None)
    context.args = arguments
    try:
        handlers = {
            "shop": shop,
            "collection": collection,
            "balance": balance,
            "help": help_command,
            "buy": buy,
            "support": support,
            "transfer": transfer,
        }
        await handlers[command](update, context)
    finally:
        context.args = old_args


async def arabic_text_router(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle only the exact Arabic words used as chat shortcuts."""
    message = update.effective_message
    text = (message.text if message else "").strip()
    command = ARABIC_COMMANDS.get(text)
    if not command:
        return

    old_args = getattr(context, "args", None)
    context.args = []
    try:
        handlers = {
            "shop": shop,
            "collection": collection,
            "balance": balance,
            "help": help_command,
            "buy": buy,
            "support": support,
            "transfer": transfer,
        }
        await handlers[command](update, context)
    finally:
        context.args = old_args


def _shop_seconds_left(context: ContextTypes.DEFAULT_TYPE, slot_key: int) -> int:
    settings = _settings(context)
    return max(
        0,
        (slot_key + 1) * settings.rotation_minutes * 60 - int(time.time()),
    )


def _shop_keyboard(shop: list) -> InlineKeyboardMarkup | None:
    rows = []
    for card in shop:
        name, _, _, _ = _localized_card(card)
        buttons = [
            InlineKeyboardButton(
                f"🛒 شراء {name}",
                callback_data=f"buy:{card['card_id']}",
            ),
            InlineKeyboardButton(
                "التفاصيل",
                callback_data=f"detail:{card['card_id']}",
            ),
        ]
        if card["stock"] > 0:
            rows.append(buttons)
        else:
            rows.append(
                [
                    InlineKeyboardButton(
                        "التفاصيل",
                        callback_data=f"detail:{card['card_id']}",
                    )
                ]
            )
    rows.append(
        [InlineKeyboardButton(BACK_LABEL, callback_data="menu:main")]
    )
    return InlineKeyboardMarkup(rows)


def _shop_text(shop: list, seconds_left: int, notice: str = "") -> str:
    lines = []
    if notice:
        lines.extend([notice, ""])
    lines.extend(
        [
            "\u200f<b>متجر البطاقات بالساعة</b>",
            f"\u200fيتجدد خلال: <b>{seconds_left // 3600:02d}:{(seconds_left % 3600) // 60:02d}:{seconds_left % 60:02d}</b>",
            "",
        ]
    )
    for card in shop:
        name, set_name, rarity, description = _localized_card(card)
        stock = f"{card['stock']} نسخة" if card["stock"] else "نفدت الكمية"
        lines.append(
            f"\u200f{card['emoji']} <b>{html.escape(name)}</b> · {html.escape(rarity)}\n"
            f"\u200fالمجموعة: {html.escape(set_name)}\n"
            f"\u200fالسعر: <b>{card['price']:,}</b> عملة · المخزون: <b>{stock}</b>\n"
            f"\u200fالوصف: {html.escape(description)}"
        )
    lines.extend(["", "\u200fاضغط على «التفاصيل» لعرض بطاقة كاملة، أو «شراء» للشراء مباشرة."])
    return "\n".join(lines)


def _card_details_text(card: dict, notice: str = "") -> str:
    name, set_name, rarity, description = _localized_card(card)
    card_gameplay = gameplay_details(card["card_id"])
    stock = f"{card['stock']} نسخة متاحة" if card["stock"] else "نفدت الكمية"
    appearance = rarity_appearance_percentage(rarity)
    lines = []
    if notice:
        lines.extend([notice, ""])
    lines.extend(
        [
            f"\u200f{card['emoji']} <b>{html.escape(name)}</b>",
            "",
            f"\u200f<b>الندرة:</b> {html.escape(rarity)}",
            f"\u200f<b>المجموعة:</b> {html.escape(set_name)}",
            f"\u200f<b>السعر:</b> {card['price']:,} عملة",
            f"\u200f<b>المخزون:</b> {stock}",
            f"\u200f<b>الوصف:</b> {html.escape(description)}",
            "",
            "\u200f<b>⚡ خواص البطاقة:</b>",
            *[
                f"\u200f• {html.escape(ability)}"
                for ability in card_gameplay.abilities
            ],
            "",
            f"\u200f<b>🎮 تأثير البطاقة داخل اللعبة:</b> {html.escape(card_gameplay.game_effect)}",
            f"\u200f<b>💪 قوة البطاقة:</b> {html.escape(card_gameplay.power_level)}",
            f"\u200f<b>🎲 نسبة ظهورها في المتجر:</b> {appearance:.2f}٪ تقريبًا",
        ]
    )
    return "\n".join(lines)


def _card_details_keyboard(card: dict) -> InlineKeyboardMarkup:
    rows = []
    if card["stock"] > 0:
        rows.append(
            [
                InlineKeyboardButton(
                    "🛒 شراء نسخة",
                    callback_data=f"buydetail:{card['card_id']}",
                )
            ]
        )
    rows.append(
        [InlineKeyboardButton(BACK_LABEL, callback_data="menu:shop")]
    )
    return InlineKeyboardMarkup(rows)


def _collection_text(cards: list) -> str:
    if not cards:
        return (
            "\u200f<b>مجموعتك فارغة</b>\n\n"
            "\u200fاستخدم /shop واحصل على بطاقتك الأولى."
        )
    lines = ["\u200f<b>مجموعتك</b>", ""]
    for card in cards:
        name, _, rarity, _ = _localized_card(card)
        lines.append(
            f"\u200f{card['emoji']} <b>{html.escape(name)}</b> · {html.escape(rarity)}"
            f" — <b>×{card['quantity']}</b>"
        )
    return "\n".join(lines)


async def _edit_query(
    query,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    await query.edit_message_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup,
    )


def _current_shop_page(
    context: ContextTypes.DEFAULT_TYPE,
    notice: str = "",
) -> tuple[str, InlineKeyboardMarkup, list]:
    slot_key, cards = _db(context).get_current_shop(int(time.time()))
    return (
        _shop_text(cards, _shop_seconds_left(context, slot_key), notice),
        _shop_keyboard(cards),
        cards,
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _ensure_user(update, context)
    await update.message.reply_html(
        _main_menu_text(),
        reply_markup=_main_menu_keyboard(),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _ensure_user(update, context)
    await update.message.reply_html(
        _help_text(),
        reply_markup=_back_keyboard("menu:main"),
    )


async def support(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "💬 حياكم الله جميعًا 🤍\n\n"
        "إذا عندكم أي شكوى أو اقتراح أو واجهتكم أي مشكلة، لا تترددون بالتواصل مع مالك البوت:\n\n"
        "👤 @ffczy"
    )


async def transfer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _ensure_user(update, context)
    if len(context.args) < 2:
        await update.message.reply_text(
            "❌ الاستخدام:\n/تحويل @الشخص المبلغ"
        )
        return

    receiver_username = context.args[0].lstrip("@").strip()
    try:
        amount = int(context.args[1])
    except (TypeError, ValueError):
        await update.message.reply_text("❌ المبلغ غير صحيح")
        return
    if amount <= 0:
        await update.message.reply_text("❌ المبلغ غير صحيح")
        return

    result = _db(context).transfer_coins(
        update.effective_user.id,
        receiver_username,
        amount,
    )
    if result == "insufficient_funds":
        await update.message.reply_text("❌ لا تملك كوينز كافية")
        return
    if result == "receiver_not_found":
        await update.message.reply_text("❌ اللاعب غير موجود")
        return
    if result == "self_transfer":
        await update.message.reply_text("❌ لا يمكنك التحويل لنفسك")
        return
    if result != "transferred":
        await update.message.reply_text("❌ خطأ في الأمر")
        return

    await update.message.reply_text(
        f"✅ تم تحويل {amount} 🪙 كوينز إلى @{receiver_username}"
    )


async def refresh_shop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings = _settings(context)
    if not update.effective_user or update.effective_user.id not in settings.admin_user_ids:
        await update.message.reply_html("هذا الأمر مخصص لمشرفي المتجر فقط.")
        return
    _ensure_user(update, context)
    _db(context).refresh_shop(int(time.time()))
    await update.message.reply_text("✅ تم تحديث المتجر")


async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _ensure_user(update, context)
    text, keyboard, _ = _current_shop_page(context)
    await update.message.reply_html(text, reply_markup=keyboard)


async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _ensure_user(update, context)
    coins = _db(context).get_balance(update.effective_user.id)
    await update.message.reply_html(
        f"\u200f<b>رصيدك</b>\n\n🪙 <b>{coins:,}</b> عملة",
        reply_markup=_back_keyboard("menu:main"),
    )


async def collection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _ensure_user(update, context)
    cards = _db(context).get_collection(update.effective_user.id)
    await update.message.reply_html(
        _collection_text(cards),
        reply_markup=_back_keyboard("menu:main"),
    )


async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _ensure_user(update, context)
    if not context.args:
        await update.message.reply_html(
            "\u200fالاستخدام: <code>/buy card-id [quantity]</code>\n\n"
            "\u200fاستخدم /shop لمعرفة المعرّفات المتاحة.",
            reply_markup=_back_keyboard("menu:shop"),
        )
        return
    card_id = context.args[0].lower().strip()
    try:
        quantity = int(context.args[1]) if len(context.args) > 1 else 1
    except ValueError:
        await update.message.reply_html(
            "يجب أن تكون الكمية رقمًا صحيحًا.",
            reply_markup=_back_keyboard("menu:shop"),
        )
        return
    success, message, coins = _db(context).buy_card(
        update.effective_user.id, card_id, quantity, int(time.time())
    )
    prefix = "✅ " if success else "❌ "
    await update.message.reply_html(
        f"{prefix}{html.escape(message)}\n\n\u200fالرصيد: <b>{coins:,}</b> عملة",
        reply_markup=_back_keyboard("menu:shop"),
    )


async def _purchase_from_callback(
    query,
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    card_id: str,
    detail_view: bool,
) -> None:
    _ensure_user(update, context)
    success, message, coins = _db(context).buy_card(
        query.from_user.id, card_id, 1, int(time.time())
    )
    prefix = "✅ " if success else "❌ "
    notice = (
        f"{prefix}{html.escape(message)}\n"
        f"\u200fالرصيد المتبقي: <b>{coins:,}</b> عملة"
    )
    text, shop_keyboard, cards = _current_shop_page(context, notice if not detail_view else "")
    if detail_view:
        card = next((item for item in cards if item["card_id"] == card_id), None)
        if card:
            await _edit_query(
                query,
                _card_details_text(card, notice),
                _card_details_keyboard(card),
            )
            return
        await _edit_query(
            query,
            f"{notice}\n\n\u200fهذه البطاقة لم تعد في المتجر الحالي.",
            _back_keyboard("menu:shop"),
        )
        return
    await _edit_query(query, text, shop_keyboard)


async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data or ""
    _ensure_user(update, context)

    if data == "menu:main":
        await _edit_query(query, _main_menu_text(), _main_menu_keyboard())
        return
    if data == "menu:shop":
        text, keyboard, _ = _current_shop_page(context)
        await _edit_query(query, text, keyboard)
        return
    if data == "menu:collection":
        cards = _db(context).get_collection(query.from_user.id)
        await _edit_query(query, _collection_text(cards), _back_keyboard("menu:main"))
        return
    if data == "menu:balance":
        coins = _db(context).get_balance(query.from_user.id)
        await _edit_query(
            query,
            f"\u200f<b>رصيدك</b>\n\n🪙 <b>{coins:,}</b> عملة",
            _back_keyboard("menu:main"),
        )
        return
    if data == "menu:help":
        await _edit_query(query, _help_text(), _back_keyboard("menu:main"))
        return
    if data.startswith("detail:"):
        card_id = data.split(":", 1)[1]
        _, _, cards = _current_shop_page(context)
        card = next((item for item in cards if item["card_id"] == card_id), None)
        if card:
            await _edit_query(
                query,
                _card_details_text(card),
                _card_details_keyboard(card),
            )
        else:
            await _edit_query(
                query,
                "\u200fهذه البطاقة ليست في المتجر الحالي.",
                _back_keyboard("menu:shop"),
            )
        return
    if data.startswith("buydetail:"):
        await _purchase_from_callback(
            query,
            update,
            context,
            data.split(":", 1)[1],
            detail_view=True,
        )
        return
    if data.startswith("buy:"):
        await _purchase_from_callback(
            query,
            update,
            context,
            data.split(":", 1)[1],
            detail_view=False,
        )


async def admin_coins(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings = _settings(context)
    if update.effective_user.id not in settings.admin_user_ids:
        await update.message.reply_html("هذا الأمر مخصص لمشرفي المتجر فقط.")
        return
    if len(context.args) != 2:
        await update.message.reply_html("الاستخدام: <code>/admin_coins user_id amount</code>")
        return
    try:
        user_id, amount = int(context.args[0]), int(context.args[1])
        new_balance = _db(context).add_coins(user_id, amount)
    except (ValueError, TypeError):
        await update.message.reply_html("يجب أن يكون معرّف المستخدم والمبلغ أرقامًا صحيحة.")
        return
    await update.message.reply_html(
        f"تمت إضافة {amount:,} عملة. الرصيد الجديد: <b>{new_balance:,}</b>."
    )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Unhandled Telegram update error", exc_info=context.error)
