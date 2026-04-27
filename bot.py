from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

import json
import os
import requests

TOKEN = "8550250568:AAGxUDnU0tVBGBAElMycRUpQuYM8sUqIwlA"

# ====== Google Sheet API（改这里）======
SHEET_API = "https://opensheet.elk.sh/1bgrXN6pZZm-cMMqjvixbYT4SFB-dhAOILb3KeHyALOk/jobs"

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

# ====== 构建按钮 ======
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

# ====== 获取岗位 ======
def fetch_jobs():
    try:
        res = requests.get(SHEET_API)
        data = res.json()

        jobs = []
        for row in data:
            tags = row.get("标签", "")
            tag_list = [t.strip() for t in tags.replace("，", ",").split(",") if t]

            jobs.append({
                "title": row.get("岗位名称"),
                "company": row.get("公司"),
                "link": row.get("链接"),
                "tags": tag_list
            })

        return jobs

    except Exception as e:
        print("获取岗位失败:", e)
        return []

# ====== 推送岗位 ======
async def push_jobs(context: ContextTypes.DEFAULT_TYPE, user_id=None):
    jobs = fetch_jobs()

    # 👉 如果传了 user_id = 只推给当前用户（测试用）
    if user_id:
        user_tags = user_data.get(user_id, [])
        for job in jobs:
            if any(tag in job["tags"] for tag in user_tags):

                text = f"""📌 {job['title']}
公司：{job['company']}
申请：{job['link']}
标签：{' '.join(['#'+t for t in job['tags']])}
"""
                await context.bot.send_message(chat_id=int(user_id), text=text)
        return

    # 👉 否则全量推送（以后定时用）
    for uid, user_tags in user_data.items():
        for job in jobs:
            if any(tag in job["tags"] for tag in user_tags):

                text = f"""📌 {job['title']}
公司：{job['company']}
申请：{job['link']}
标签：{' '.join(['#'+t for t in job['tags']])}
"""
                await context.bot.send_message(chat_id=int(uid), text=text)

# ====== /start ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    selected = user_data.get(user_id, [])

    await update.message.reply_text(
        "请选择你感兴趣的岗位类型（可多选）：",
        reply_markup=build_keyboard(selected)
    )

    # ⭐测试：同时推送岗位给自己
    await push_jobs(context, user_id=user_id)

# ====== 按钮逻辑 ======
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

    user_data[user_id] = selected
    save_data(user_data)

    await query.answer()
    await query.edit_message_reply_markup(
        reply_markup=build_keyboard(selected)
    )

# ====== 启动 ======
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))

app.run_polling()
