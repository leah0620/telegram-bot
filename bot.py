from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

import json
import os
import requests
from datetime import time

TOKEN = "8550250568:AAGxUDnU0tVBGBAElMycRUpQuYM8sUqIwlA"

SHEET_API = "https://opensheet.elk.sh/1bgrXN6pZZm-cMMqjvixbYT4SFB-dhAOILb3KeHyALOk/jobs"

DATA_FILE = "users.json"

# ====== 读写数据 ======
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

user_data = load_data()

# ====== 标签 ======
TAGS = ["初级", "高级", "客户", "产品", "销售", "电商", "语言", "运营", "BD", "市场"]

# ====== 按钮 ======
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

# ====== 推送（带去重）======
async def push_jobs(context: ContextTypes.DEFAULT_TYPE):
    global user_data
    user_data = load_data()
    jobs = fetch_jobs()

    updated = False

    for uid, info in user_data.items():
        tags = info.get("tags", [])
        sent = info.get("sent", [])

        new_jobs = []

        for job in jobs:
            if job["link"] in sent:
                continue

            if any(tag in job["tags"] for tag in tags):
                new_jobs.append(job)

        if not new_jobs:
            continue

        text = "🎯 今日新增岗位：\n\n"

        for job in new_jobs[:5]:
            text += f"""📌 {job['title']}
公司：{job['company']}
申请：{job['link']}
标签：{' '.join(['#'+t for t in job['tags']])}

"""
            sent.append(job["link"])

        user_data[uid]["sent"] = sent
        updated = True

        try:
            await context.bot.send_message(chat_id=int(uid), text=text)
        except Exception as e:
            print("发送失败:", uid, e)

    if updated:
        save_data(user_data)

# ====== /start ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    if user_id not in user_data:
        user_data[user_id] = {"tags": [], "sent": []}

    selected = user_data[user_id]["tags"]

    await update.message.reply_text(
        "请选择你感兴趣的岗位类型（可多选）：",
        reply_markup=build_keyboard(selected)
    )

# ====== 按钮 ======
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = str(query.from_user.id)
    data = query.data

    if user_id not in user_data:
        user_data[user_id] = {"tags": [], "sent": []}

    selected = user_data[user_id]["tags"]

    if data == "save":
        save_data(user_data)
        await query.answer()
        await query.edit_message_text(f"✅ 已保存：{', '.join(selected)}")
        return

    if data in selected:
        selected.remove(data)
    else:
        selected.append(data)

    user_data[user_id]["tags"] = selected

    await query.answer()
    await query.edit_message_reply_markup(
        reply_markup=build_keyboard(selected)
    )

# ====== 启动 ======
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))

job_queue = app.job_queue

# 北京时间18:00
job_queue.run_daily(push_jobs, time=time(hour=10, minute=0))

# 👉 测试用（30秒触发）
# job_queue.run_once(push_jobs, when=30)

app.run_polling()
