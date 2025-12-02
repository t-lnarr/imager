from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import requests
from io import BytesIO
import asyncio
import os

# Telegram bot token'ınızı buraya yazın
TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context):
    intro_text = (
        "Salam! 👋\n\n"
        "Maňa random bir zat ýaz we men surat döredeýin.\n"
        "Mysal üçin: `harry potter`, `täze ýyl` gibi..."
    )
    await update.message.reply_text(intro_text)

async def generate_image(update: Update, context):
    user_text = update.message.text
    # Kullanıcıya görselin üretileceğini söyle
    msg = await update.message.reply_text("Azajyk garaş, ýasap otyrn… 🖌️")

    # Boşlukları _ ile değiştiriyoruz
    query = user_text.replace(" ", "_")
    image_url = f"https://image.pollinations.ai/prompt/{query}"

    # Görseli çekiyoruz
    response = requests.get(image_url)
    if response.status_code == 200:
        bio = BytesIO(response.content)
        bio.name = "image.png"
        await update.message.reply_photo(photo=bio)
        # Önceki mesajı silebilirsiniz (opsiyonel)
        await msg.delete()
    else:
        await update.message.reply_text("Blaa, döredip bolmada 😢")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), generate_image))

    print("Bot çalışıyor...")
    app.run_polling()
