import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7104896018

PRICE = 600
KASPI = "4400 4303 3000 9942"
CHANNEL_URL = "https://t.me/films1kz"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton(
                "💳 Сатып алу — 600 ₸",
                callback_data="buy"
            )
        ]
    ]

    await update.message.reply_text(
        "Films🍿| KZ Фильмдер 🎬\n\n"
        "Қош келдіңіз! 👋\n"
        "Мұнда фильмдерді толық нұсқада көруге болады.\n\n"
        "🎥 Толық фильм\n"
        "💰 Бағасы: 600 ₸\n\n"
        "Төмендегі батырманы басып, фильмді сатып алыңыз:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        f"💰 Бағасы: {PRICE} ₸\n\n"
        f"💳: {KASPI}\n\n"
        "Төлем жасағаннан кейін:\n"
        "Чекті (файл түрінде) осы ботқа жіберіңіз."
    )


async def receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "✅ РАСТАУ",
                callback_data=f"yes_{user.id}"
            ),
            InlineKeyboardButton(
                "❌ БАС ТАРТУ",
                callback_data=f"no_{user.id}"
            )
        ]
    ])

    caption = (
        "🧾 ЖАҢА ЧЕК\n\n"
        f"👤 {user.first_name}\n"
        f"🆔 {user.id}\n"
        f"💰 {PRICE} ₸"
    )

    if update.message.photo:
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=update.message.photo[-1].file_id,
            caption=caption,
            reply_markup=keyboard
        )

    elif update.message.document:
        await context.bot.send_document(
            chat_id=ADMIN_ID,
            document=update.message.document.file_id,
            caption=caption,
            reply_markup=keyboard
        )

    await update.message.reply_text(
        "✅ Чек қабылданды!\n\n"
        "⏳ Төлем тексерілуде.\n"
        "Расталғаннан кейін хабарлама аласыз."
    )


async def admin_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    action, user_id = query.data.split("_")
    user_id = int(user_id)

    if action == "yes":
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "🎬 Киноға кіру ↗️",
                    url=CHANNEL_URL
                )
            ]
        ])

        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "✅ Төлем расталды!\n\n"
                "🎬 Киноны көру үшін төмендегі батырманы басыңыз:"
            ),
            reply_markup=keyboard
        )

        try:
            if query.message.photo:
                await query.edit_message_caption(
                    caption="✅ ТӨЛЕМ РАСТАЛДЫ"
                )
            else:
                await query.edit_message_text(
                    text="✅ ТӨЛЕМ РАСТАЛДЫ"
                )
        except Exception:
            pass

    elif action == "no":
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "❌ Төлем қабылданбады.\n\n"
                "🧾 Чекті қайта жіберіңіз."
            )
        )

        try:
            if query.message.photo:
                await query.edit_message_caption(
                    caption="❌ ТӨЛЕМ ҚАБЫЛДАНБАДЫ"
                )
            else:
                await query.edit_message_text(
                    text="❌ ТӨЛЕМ ҚАБЫЛДАНБАДЫ"
                )
        except Exception:
            pass


def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN орнатылмаған!")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        CallbackQueryHandler(
            buy,
            pattern="^buy$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            admin_buttons,
            pattern="^(yes|no)_"
        )
    )

    app.add_handler(
        MessageHandler(
            filters.PHOTO | filters.Document.ALL,
            receipt
        )
    )

    print("🤖 БОТ ІСКЕ ҚОСЫЛДЫ!")

    app.run_polling()


if __name__ == "__main__":
    main()
