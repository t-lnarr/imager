from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import requests
from io import BytesIO
import os

# Telegram bot token
TOKEN = os.getenv("BOT_TOKEN")

# Admin Telegram ID'nizi buraya yazın
ADMIN_ID = 7172270461   # <-- BURAYA kendi ID'nizi yazın!


# --- Kullanıcı Kaydı ---
def save_user(user_id):
    if not os.path.exists("users.txt"):
        open("users.txt", "w").close()

    with open("users.txt", "r") as f:
        users = f.read().splitlines()

    if str(user_id) not in users:
        with open("users.txt", "a") as f:
            f.write(str(user_id) + "\n")


# --- Prompt Kaydı ---
def save_prompt(user_id, prompt):
    with open("prompts.txt", "a") as f:
        f.write(f"{user_id} : {prompt}\n")


# /start komutu
async def start(update: Update, context):
    save_user(update.message.from_user.id)

    intro_text = (
        "Salam! 👋\n\n"
        "Maňa islendik zat ýaz, menem şoňa görä surat döredeýin.\n"
        "Mysal: `harry potter`, `täze ýyl`, `sunrise forest` ..."
    )
    await update.message.reply_text(intro_text)


# Görsel üretme fonksiyonu
async def generate_image(update: Update, context):
    user_id = update.message.from_user.id
    user_text = update.message.text

    save_user(user_id)
    save_prompt(user_id, user_text)

    msg = await update.message.reply_text("Azajyk garaş, ýasap otyryn… 🖌️")

    query = user_text.replace(" ", "_")
    image_url = f"https://image.pollinations.ai/prompt/{query}"

    response = requests.get(image_url)
    if response.status_code == 200:
        bio = BytesIO(response.content)
        bio.name = "image.png"
        await update.message.reply_photo(photo=bio)
        await msg.delete()
    else:
        await update.message.reply_text("Blaa, döredip bolmady 😢")


# --- ADMIN KOMUTLARI ---

# /allsent mesaj
async def allsent(update: Update, context):
    if update.message.from_user.id != ADMIN_ID:
        return await update.message.reply_text("Bu komut diňe admin üçindir.")

    text = " ".join(context.args)
    if not text:
        return await update.message.reply_text("Ulanyş: /allsent <mesaj>")

    if not os.path.exists("users.txt"):
        return await update.message.reply_text("Ulanyjy ýok ýaly.")

    with open("users.txt", "r") as f:
        users = f.read().splitlines()

    say = 0
    for uid in users:
        try:
            await context.bot.send_message(chat_id=int(uid), text=text)
            say += 1
        except:
            pass

    await update.message.reply_text(f"Mesaj {say} ulanyja ugradyldy.")


# /view
async def view(update: Update, context):
    if update.message.from_user.id != ADMIN_ID:
        return await update.message.reply_text("Bu komut diňe admin içindir.")

    if not os.path.exists("prompts.txt"):
        return await update.message.reply_text("Entäk prompt ýok.")

    with open("prompts.txt", "r") as f:
        data = f.read()

    await update.message.reply_text(f"📄 Soňky promptlar:\n\n{data}")


# /much
async def much(update: Update, context):
    if not os.path.exists("users.txt"):
        return await update.message.reply_text("0 ulanyjy bar.")

    with open("users.txt", "r") as f:
        users = f.read().splitlines()

    await update.message.reply_text(f"👥 Jemi ulanyjy: {len(users)}")


# --- BOT ÇALIŞTIRMA ---
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("allsent", allsent))
    app.add_handler(CommandHandler("view", view))
    app.add_handler(CommandHandler("much", much))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), generate_image))

    print("Bot işleýär...")
    app.run_polling()
