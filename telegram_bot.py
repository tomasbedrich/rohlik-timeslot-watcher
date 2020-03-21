import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import CommandStart, CommandHelp
from aiogram.utils import executor
from aiohttp import ClientSession, ClientError

from config import config
from rohlik import get_free_timeslot, download_timeslots

logging.basicConfig(level=logging.INFO)

log = logging.getLogger(__name__)

bot = Bot(token=config["TELEGRAM_BOT_TOKEN"])
dp = Dispatcher(bot)

watch_tasks = {}


@dp.message_handler(CommandStart())
async def start(message: types.Message):
    chat_id = message.chat.id
    log.info(f"Starting watcher for {chat_id=}")

    if chat_id not in watch_tasks:
        run_watcher = asyncio.create_task(watch(chat_id))
        answer = message.answer("Okay, started")
        watch_tasks[chat_id] = run_watcher
        await asyncio.gather(run_watcher, answer)
    else:
        await message.answer("Already started")


@dp.message_handler(commands=["stop"])
async def stop(message: types.Message):
    chat_id = message.chat.id
    log.info(f"Stopping watcher for {chat_id=}")

    task = watch_tasks.get(chat_id)
    if task:
        task.cancel()
        del watch_tasks[chat_id]
        await message.answer("Okay, stopped")
    else:
        await message.answer("Already stopped")


@dp.message_handler(CommandHelp())
async def help(message: types.Message):
    await message.answer("Available commands:\n/start - start watching\n/stop - stop watching")


async def watch(telegram_chat_id):
    async with ClientSession(**config.get_namespace("HTTP_")) as session:
        while True:
            try:
                timeslots = await download_timeslots(session, config["ROHLIK_URL"])
                log.debug("Downloaded timeslots")
            except (ClientError, asyncio.TimeoutError):
                log.exception("Request failed")
                await asyncio.sleep(config["BACKOFF_SLEEP"])

            timeslot = get_free_timeslot(timeslots)
            sleep = config["SLEEP"]
            if timeslot:
                await bot.send_message(telegram_chat_id, timeslot)
                sleep = config["SUCCESS_SLEEP"]

            log.debug(f"{sleep=} (seconds)")
            await asyncio.sleep(sleep)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
