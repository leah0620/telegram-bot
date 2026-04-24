from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "8550250568:AAGxUDnU0tVBGBAElMycRUpQuYM8sUqIwlA"

user_data = {}

TAGS = ["销售", "电商", "语言" , "KOL", "运营", "BD", "市场"]

def build_keyboard(selected):
    keyboard = []
    for tag in TAGS:
        text = f"✅ {tag}" if tag in selected else f"⬜ {tag}"
        keyboard.append([InlineKeyboardButton(text, callback_data=tag)])
    
    keyboard.append([InlineKeyboardButton("💾 保存", callback_data="save")])
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    selected = user_data.get(user_id, [])
    
    await update.message.reply_text(
        "请选择你感兴趣的岗位类型（可多选）：",
        reply_markup=build_keyboard(selected)
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data

    selected = user_data.get(user_id, [])

    if data == "save":
        await query.answer()
        await query.edit_message_text(f"✅ 已保存：{', '.join(selected)}")
        return

    if data in selected:
        selected.remove(data)
    else:
        selected.append(data)

    user_data[user_id] = selected

    await query.answer()
    await query.edit_message_reply_markup(
        reply_markup=build_keyboard(selected)
    )

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))

app.run_polling()
