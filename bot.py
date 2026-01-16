# bot.py
import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters
import pytz
from datetime import time
import logging

# ================== 配置区（请修改这里！）==================
BOT_TOKEN = " "          # 替换为你的 Bot Token
GROUP_CHAT_ID = -1003609938547            # 替换为你的群组 ID（带 -100 前缀）
# =========================================================

# 启用日志（方便排查问题）
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# === 自动回复逻辑（仅响应群组消息）===
async def auto_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_type = update.message.chat.type
    if chat_type not in ["group", "supergroup"]:
        return  # 忽略私聊和频道

    text = update.message.text.lower()
    user_first_name = update.message.from_user.first_name or "用户"

    # 关键词匹配（可自行扩展）
    if any(kw in text for kw in ["价格", "多少钱", "售价"]):
        reply = f"{user_first_name}您好！\n产品基础版 ¥299，专业版 ¥599，支持 7 天无理由退换！"
    elif any(kw in text for kw in ["售后", "保修", "维修"]):
        reply = f"{user_first_name}您好！\n我们提供 1 年质保，请加客服微信：kefu123 获取支持。"
    elif any(kw in text for kw in ["官网", "网站", "链接"]):
        reply = "🔗 官网地址：https://example.com\n欢迎访问了解详情！"
    elif "帮助" in text:
        reply = (
            "💡 常见指令：\n"
            "• 问「价格」→ 查看报价\n"
            "• 问「售后」→ 获取支持方式\n"
            "• 问「官网」→ 跳转官网"
        )
    else:
        return  # 不匹配关键词，不回复（避免刷屏）

    # 在群组中回复（@ 提及提问者）
    await update.message.reply_text(reply, quote=True)

# === 每天定时发送广告 ===
async def send_daily_ad(context: ContextTypes.DEFAULT_TYPE):
    ad_text = """
📣【每日特惠】限时优惠！

🔥 今日下单立减 50 元！
📦 前 20 名送精美礼品
⏰ 优惠截止今晚 24:00

👉 立即抢购：https://example.com/buy
    """
    try:
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=ad_text)
        logging.info("✅ 广告已成功发送")
    except Exception as e:
        logging.error(f"❌ 发送广告失败: {e}")

# === 主函数 ===
def main():
    # 创建应用
    app = Application.builder().token(BOT_TOKEN).build()

    # 添加消息处理器
    app.add_handler(MessageHandler(filters.TEXT & ～filters.COMMAND, auto_reply))

    # 设置每天 10:00（北京时间）发送广告
    beijing_tz = pytz.timezone("Asia/Shanghai")
    app.job_queue.run_daily(
        send_daily_ad,
        time=time(hour=10, minute=0, second=0, tzinfo=beijing_tz),
        name="daily_ad"
    )

    print("🤖 Telegram 群组自动回复 + 定时广告 Bot 已启动！")
    print("确保 Bot 已加入群组并设为管理员（需关闭隐私模式）")

    # 开始轮询
    app.run_polling()

if __name__ == "__main__":
    main()