from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import requests
from io import BytesIO
import os

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7172270461


# --- Kullanıcı Kaydı ---
def save_user(user_id):
    if not os.path.exists("users.txt"):
        open("users.txt", "w").close()

    with open("users.txt", "r") as f:
        users = f.read().splitlines()

    if str(user_id) not in users:
        with open("users.txt", "a") as f:
            f.write(str(user_id) + "\n")


# --- Prompt kaydı ---
def save_prompt(user_id, username, prompt):
    with open("prompts.txt", "a") as f:
        f.write(f"{user_id} | {username} | {prompt}\n")


# --- Uzun mesajları bölme ---
async def send_long_message(bot, chat_id, text):
    limit = 4096
    for i in range(0, len(text), limit):
        await bot.send_message(chat_id=chat_id, text=text[i:i + limit])


# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    save_user(user.id)

    text = (
        "Salam! 👋\n\n"
        "Maňa islendik zat ýaz, menem şoňa görä surat döredeýin.\n"
        "Mysal: `harry potter`, `täze ýyl`, `sunrise forest` ..."
    )
    await update.message.reply_text(text)


# Görsel üretme fonksiyonu
async def generate_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id
    username = user.username or "NoUsername"
    prompt = update.message.text

    save_user(user_id)
    save_prompt(user_id, username, prompt)

    msg = await update.message.reply_text("Azajyk garaş, ýasap otyryn… 🖌️")

    query = prompt.replace(" ", "_")
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
async def allsent(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
            # Eğer mesaj görsel URL'si içeriyorsa fotoğraf olarak gönder
            if text.lower().endswith((".jpg", ".png", ".jpeg")):
                try:
                    img = requests.get(text).content
                    bio = BytesIO(img)
                    bio.name = "image.jpg"
                    await context.bot.send_photo(chat_id=int(uid), photo=bio)
                except:
                    await context.bot.send_message(chat_id=int(uid), text=text)
            else:
                await send_long_message(context.bot, int(uid), text)

            say += 1
        except:
            pass

    await update.message.reply_text(f"Mesaj {say} ulanyja ugradyldy.")


# /view — son aramalar sayfalı
async def view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return await update.message.reply_text("Bu komut diňe admin içindir.")

    if not os.path.exists("prompts.txt"):
        return await update.message.reply_text("Entäk prompt ýok.")

    # Sayfa numarası
    try:
        page = int(context.args[0]) if context.args else 1
    except:
        page = 1

    page_size = 15

    with open("prompts.txt", "r") as f:
        lines = f.read().splitlines()

    lines.reverse()  # En yeni en üstte

    total_pages = max(1, (len(lines) + page_size - 1) // page_size)

    if page < 1 or page > total_pages:
        return await update.message.reply_text(f"Sahypa tapylmady. 1–{total_pages} aralygynda bar.")

    start = (page - 1) * page_size
    end = start + page_size
    selected = lines[start:end]

    text = f"📄 Soňky promptlar (Sahypa {page}/{total_pages}):\n\n"

    for row in selected:
        uid, username, prompt = row.split(" | ", 2)
        text += f"👤 <b>{username}</b> (<code>{uid}</code>)\n📝 {prompt}\n\n"

    await send_long_message(context.bot, update.message.chat_id, text)


# /much
async def much(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
