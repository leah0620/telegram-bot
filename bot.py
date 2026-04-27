from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

import json
import os

TOKEN = "8550250568:AAGxUDnU0tVBGBAElMycRUpQuYM8sUqIwlA"

# ====== 数据文件 ======
DATA_FILE = "users.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# ====== 初始化用户数据 ======
user_data = load_data()

# ====== 标签 ======
TAGS = ["初级", "高级", "客户", "产品", "销售", "电商", "语言", "运营", "BD", "市场"]

# ====== 按钮构建 ======
def build_keyboard(selected):
    keyboard = []

    for i in range(0, len(TAGS), 2):
        row = []

        tag1 = TAGS[i]
        text1 = f"✅ {tag1}" if tag1 in selected else f"⬜ {tag1}"
        row.append(InlineKeyboardButton(text1, callback_data=tag1))

        if i + 1 < len(TAGS):
            tag2 = TAGS[i + 1]
            text2 = f"✅ {tag2}" if tag2 in selected else f"⬜ {tag2}"
            row.append(InlineKeyboardButton(text2, callback_data=tag2))

        keyboard.append(row)

    keyboard.append([InlineKeyboardButton("💾 保存", callback_data="save")])

    return InlineKeyboardMarkup(keyboard)

# ====== /start ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)  # ⚠️ 用字符串存
    selected = user_data.get(user_id, [])

    await update.message.reply_text(
        "请选择你感兴趣的岗位类型（可多选）：",
        reply_markup=build_keyboard(selected)
    )

# ====== 点击按钮 ======
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = str(query.from_user.id)
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

    # 保存用户选择
    user_data[user_id] = selected
    save_data(user_data)  # ⭐关键：写入文件

    await query.answer()
    await query.edit_message_reply_markup(
        reply_markup=build_keyboard(selected)
    )

# ====== 启动 ======
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))

app.run_polling()
