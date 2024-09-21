import asyncio
from telegram import Bot

TELEGRAM_BOT_TOKEN = '7888579709:AAERuChULNSnfp5-srT2fl8bpYkAfGQsHHQ'

async def get_chat_id():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    updates = await bot.get_updates()
    if updates:
        chat_id = updates[-1].message.chat_id
        print(f"Chat ID: {chat_id}")
    else:
        print("No updates found. Please send a message to the bot.")

asyncio.run(get_chat_id())