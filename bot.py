import os
import asyncio
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ==========================================
# БАСТЫ БАПТАУЛАР
# ==========================================

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = 7104896018

PRICE = 600

KASPI = "4400 4303 3000 9942"

CHANNEL_URL = "https://t.me/films1kz"


# ==========================================
# RENDER HEALTH SERVER
# ==========================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is running!")

    def log_message(self, format, *args):
        pass


def start_health_server():
    port = int(os.environ.get("PORT", 10000))

    server = HTTPServer(
        ("0.0.0.0", port),
        HealthHandler
    )

    print(f"🌐 Health server started on port {port}")

    server.serve_forever()


# ==========================================
# /START
# ==========================================

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
        "Мұнда фильмдерді толық нұсқада\n"
        "көруге болады.\n\n"
        "🎥 Толық фильм\n"
        "💰 Бағасы: 600 ₸\n\n"
        "Төмендегі батырманы басып,\n"
        "фильмді сатып алыңыз:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ==========================================
# САТЫП АЛУ
# ==========================================

async def buy(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    await query.message.reply_text(
        f"💰 Бағасы: {PRICE} ₸\n\n"
        f"💳: {KASPI}\n\n"
        "Төлем жасағаннан кейін:\n"
        "🧾 Чекті (файл түрінде) осы ботқа жіберіңіз."
    )


# ==========================================
# ЧЕК ҚАБЫЛДАУ
# ==========================================

async def receipt(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

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

    # ======================================
    # ФОТО
    # ======================================

    if update.message.photo:

        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=update.message.photo[-1].file_id,
            caption=caption,
            reply_markup=keyboard
        )

    # ======================================
    # DOCUMENT / ФАЙЛ
    # ======================================

    elif update.message.document:

        await context.bot.send_document(
            chat_id=ADMIN_ID,
            document=update.message.document.file_id,
            caption=caption,
            reply_markup=keyboard
        )

    # ======================================
    # ҚОЛДАНУШЫҒА
    # ======================================

    await update.message.reply_text(
        "✅ Чек қабылданды!\n\n"
        "⏳ Төлем тексерілуде.\n"
        "Расталғаннан кейін хабарлама аласыз."
    )


# ==========================================
# АДМИН БАТЫРМАЛАРЫ
# ==========================================

async def admin_buttons(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    # Тек админ
    if query.from_user.id != ADMIN_ID:

        await query.answer(
            "❌ Бұл батырма тек админге арналған.",
            show_alert=True
        )

        return

    await query.answer()

    try:

        action, user_id = query.data.split("_")

        user_id = int(user_id)

    except Exception:

        return

    # ======================================
    # РАСТАУ
    # ======================================

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
                "🎬 Киноны көру үшін төмендегі "
                "батырманы басыңыз:"
            ),
            reply_markup=keyboard
        )

        try:

            if query.message.photo or query.message.document:

                await query.edit_message_caption(
                    caption="✅ ТӨЛЕМ РАСТАЛДЫ"
                )

            else:

                await query.edit_message_text(
                    text="✅ ТӨЛЕМ РАСТАЛДЫ"
                )

        except Exception as e:

            print("Edit error:", e)

    # ======================================
    # БАС ТАРТУ
    # ======================================

    elif action == "no":

        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "❌ Төлем қабылданбады.\n\n"
                "🧾 Чекті қайта жіберіңіз."
            )
        )

        try:

            if query.message.photo or query.message.document:

                await query.edit_message_caption(
                    caption="❌ ТӨЛЕМ ҚАБЫЛДАНБАДЫ"
                )

            else:

                await query.edit_message_text(
                    text="❌ ТӨЛЕМ ҚАБЫЛДАНБАДЫ"
                )

        except Exception as e:

            print("Edit error:", e)


# ==========================================
# ҚАТЕЛЕР
# ==========================================

async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE
):

    print("❌ Қате:", context.error)


# ==========================================
# БОТТЫ ІСКЕ ҚОСУ
# ==========================================

def main():

    if not BOT_TOKEN:

        print("❌ BOT_TOKEN табылмады!")
        print("Render → Environment → BOT_TOKEN тексеріңіз.")

        return

    # Render health server
    health_thread = threading.Thread(
        target=start_health_server,
        daemon=True
    )

    health_thread.start()

    print("🤖 БОТ ІСКЕ ҚОСЫЛУДА...")

    app = Application.builder().token(BOT_TOKEN).build()

    # /start
    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    # Сатып алу
    app.add_handler(
        CallbackQueryHandler(
            buy,
            pattern=r"^buy$"
        )
    )

    # Админ Растау / Бас тарту
    app.add_handler(
        CallbackQueryHandler(
            admin_buttons,
            pattern=r"^(yes|no)_\d+$"
        )
    )

    # Фото
    app.add_handler(
        MessageHandler(
            filters.PHOTO,
            receipt
        )
    )

    # Document
    app.add_handler(
        MessageHandler(
            filters.Document.ALL,
            receipt
        )
    )

    # Қате
    app.add_error_handler(error_handler)

    print("✅ БОТ ІСКЕ ҚОСЫЛДЫ!")
    print("📱 Telegram-нан /start басып тексеріңіз.")

    # Polling
    app.run_polling(
        drop_pending_updates=True
    )


# ==========================================
# START
# ==========================================

if __name__ == "__main__":
    main()
