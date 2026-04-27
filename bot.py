from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "8550250568:AAGxUDnU0tVBGBAElMycRUpQuYM8sUqIwlA"

user_data = {}

TAGS = ["初级", "高级", "客户", "产品", "销售", "电商", "语言", "运营", "BD", "市场"]

def build_keyboard(selected):
    keyboard = []

    # 两列布局
    for i in range(0, len(TAGS), 2):
        row = []

        # 左边
        tag1 = TAGS[i]
        text1 = f"✅ {tag1}" if tag1 in selected else f"⬜ {tag1}"
        row.append(InlineKeyboardButton(text1, callback_data=tag1))

        # 右边（防止越界）
        if i + 1 < len(TAGS):
            tag2 = TAGS[i + 1]
            text2 = f"✅ {tag2}" if tag2 in selected else f"⬜ {tag2}"
            row.append(InlineKeyboardButton(text2, callback_data=tag2))

        keyboard.append(row)

    # 最后一行：保存按钮
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
