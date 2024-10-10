import asyncio
from telegram import Bot

TELEGRAM_BOT_TOKEN = '7888579709:AAERuChULNSnfp5-srT2fl8bpYkAfGQsHHQ'
TELEGRAM_CHAT_ID = '-1002331701813'

async def send_telegram_message(message):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)