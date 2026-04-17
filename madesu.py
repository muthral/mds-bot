import os
import random
from collections import deque
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes
)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# =====================
# STATE
# =====================
chat_members = {}
tebak_sessions = {}  # chat_id -> {"angka": int, "tebakan_per_user": {uid: count}}

# =====================
# KONTEN
# =====================
jawaban = [
    "iyah", "g", "gak", "mungkin", "pasti", "100%", "impossible", "tidak akan", "tanya kuda",
    "waduh ini sulit, ak nyerah", "bisa jadi", "kayaknya iya", "gatau",
    "gay", "1000000%", "37% iya", "berdoa saja", "omaigot, pertanyaan macam apa ini",
    "omaigot", "😱", "i hate u", "stop asking", "bntar, cape.. satu2 guys",
    "ewh", "serius nanya ini?", "iya dong", "JELAS IYA",
    "gak lah, pake nanya", "nyawit ni orang", "stoooop", "kamu nanya?",
    "km nanyea?", "aah ah ahhh..", "🤤🤤🤤", "hehe, ga", "*ngangguk", "jangan sekarang",
]

pesan_jodoh = [
    "semoga samawa ya!",
    "jodoh banget, gak diragukan.",
    "meski nampaknya seperti cinta bertepuk sebelah tangan 🤔",
    "bgus, kpn ciuman?",
    "pasangan ini benar-benar saling mencintai 🪽"
]

# =====================
# HELPER
# =====================
def get_mention(user) -> str:
    if user.username:
        return f"@{user.username}"
    return f'<a href="tg://user?id={user.id}">{user.first_name}</a>'

# =====================
# COMMANDS
# =====================

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menyambut pengguna di chat pribadi atau grup"""
    welcome_text = (
        "👋 Halo! Aku **Madesu Bot**.\n\n"
        "Ketik /help untuk melihat semua perintah yang tersedia.\n"
        "Selamat mengisi kegabutan yhh"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menampilkan daftar perintah"""
    help_text = (
        "📋 *Daftar Perintah Madesu Bot*\n\n"
        "/start - Mulai bot"
        "/help - Menampilkan daftar perintah"
        "🎲 *Permainan & Hiburan*\n"
        "/apa [pertanyaan] - Tanya apapun dengan pertanyaan berawalan apa "
        "/siapa [pertanyaan] - Pilih anggota grup secara acak\n"
        "/berapa [pertanyaan] - Tanya apapun dengan pertanyaan berawalan berapa"
        "/jodoh - Pasangkan dua anggota grup secara acak\n"
        "/tebakangka - Mulai game tebak angka (0-100)\n"
        "/stoptebakangka - Hentikan game tebak angka\n"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def cmd_apa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("masukkan pertanyaannya")
        return

    pertanyaan = " ".join(context.args).lower()

    if context.args[0].lower() == "kabar":
        await update.message.reply_text("baik")
        return

    responses = []
    if any(w in pertanyaan for w in ["islam", "kristen", "buddha", "konghucu", "hindu"]):
        responses.append("jangan bawa2 agama")
    if "bubar" in pertanyaan:
        responses.append("jangan sebut B word")

    hasil = "\n".join(responses) if responses else random.choice(jawaban)
    await update.message.reply_text(hasil)

async def cmd_siapa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    members = chat_members.get(chat_id, {})

    if not members:
        await update.message.reply_text("belum ada member terdeteksi! chat dulu ya.")
        return

    if not context.args:
        await update.message.reply_text("contoh: /siapa yang belum mandi")
        return

    pertanyaan = " ".join(context.args)
    user = random.choice(list(members.values()))
    mention = get_mention(user)

    await update.message.reply_text(
        f"{mention} {pertanyaan}!",
        parse_mode="HTML"
    )

async def cmd_berapa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("masukkan pertanyaan")
        return

    pertanyaan = " ".join(context.args).lower()
    angka = random.randint(0, 100)

    if "persen" in pertanyaan:
        await update.message.reply_text(f"{angka}%")
    else:
        await update.message.reply_text(str(angka))

async def cmd_jodoh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    members = chat_members.get(chat_id, {})

    if len(members) < 2:
        await update.message.reply_text("belum ada cukup member terdeteksi!")
        return

    terpilih = random.sample(list(members.values()), 2)
    mentions = [get_mention(u) for u in terpilih]
    pesan = random.choice(pesan_jodoh)

    await update.message.reply_text(
        f"pasangan di grup ini adalah:\n\n"
        f"{mentions[0]} 💘 {mentions[1]}\n\n"
        f"{pesan}",
        parse_mode="HTML"
    )

async def cmd_tebakangka(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id

    if chat_id in tebak_sessions:
        await update.message.reply_text("🌀 game sedang berlangsung! ketik angka saja.")
        return

    target = random.randint(0, 100)
    tebak_sessions[chat_id] = {"angka": target, "tebakan_per_user": {}}

    await update.message.reply_text(
        "🌀 <b>TEBAK ANGKA DIMULAI!</b>\n\n"
        "siapapun boleh nebak!\n"
        "tebak angka 0 - 100\n\n"
        "langsung ketik angkanya aja!",
        parse_mode="HTML"
    )

async def cmd_stoptebakangka(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id

    if chat_id in tebak_sessions:
        target = tebak_sessions.pop(chat_id)["angka"]
        await update.message.reply_text(f"game dihentikan. angkanya adalah {target}")
    else:
        await update.message.reply_text("tidak ada game yang sedang berjalan")

# =====================
# WELCOME NEW MEMBER
# =====================
async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menyambut anggota baru yang bergabung ke grup"""
    for new_member in update.message.new_chat_members:
        if new_member.is_bot:
            continue
        mention = get_mention(new_member)
        welcome_msg = (
            f"✨ Selamat datang {mention} di grup! ✨\n\n"
            "Aku **Madesu Bot** 🤖, Salken yhh \n"
        )
        await update.message.reply_text(welcome_msg, parse_mode="HTML")
        # Tambahkan ke daftar member grup
        chat_id = update.message.chat_id
        if chat_id not in chat_members:
            chat_members[chat_id] = {}
        chat_members[chat_id][new_member.id] = new_member

# =====================
# MESSAGE HANDLER (tebak angka + tracking)
# =====================

async def track_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.from_user:
        return

    user = update.message.from_user
    if user.is_bot:
        return

    chat_type = update.message.chat.type
    if chat_type == "private":
        return

    chat_id = update.message.chat_id

    if chat_id not in chat_members:
        chat_members[chat_id] = {}
    chat_members[chat_id][user.id] = user

    if chat_id not in tebak_sessions:
        return

    text = update.message.text
    if not text or not text.strip().lstrip("-").isdigit():
        return

    tebakan = int(text.strip())
    session = tebak_sessions[chat_id]
    target = session["angka"]
    uid = user.id
    nama = user.first_name

    session["tebakan_per_user"][uid] = session["tebakan_per_user"].get(uid, 0) + 1

    if tebakan > target:
        await update.message.reply_text(f"⬇️ {nama}: terlalu besar")
    elif tebakan < target:
        await update.message.reply_text(f"⬆️ {nama}: terlalu kecil")
    else:
        jumlah = session["tebakan_per_user"][uid]
        del tebak_sessions[chat_id]
        await update.message.reply_text(
            f"🎉 <b>{nama}</b> berhasil menebak angka <b>{target}</b>!\n\n"
            f"ditebak dalam <b>{jumlah}x</b> tebakan",
            parse_mode="HTML"
        )

# =====================
# MAIN
# =====================

if __name__ == "__main__":
    if not TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN belum diset")

    app = ApplicationBuilder().token(TOKEN).concurrent_updates(True).build()

    # Command handlers
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("apa", cmd_apa))
    app.add_handler(CommandHandler("siapa", cmd_siapa))
    app.add_handler(CommandHandler("berapa", cmd_berapa))
    app.add_handler(CommandHandler("jodoh", cmd_jodoh))
    app.add_handler(CommandHandler("tebakangka", cmd_tebakangka))
    app.add_handler(CommandHandler("stoptebakangka", cmd_stoptebakangka))

    # Welcome new members
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))

    # Track members and handle tebak angka messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, track_member))

    print("Madesu bot is running...")
    app.run_polling()
