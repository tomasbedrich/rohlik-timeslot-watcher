import asyncio
import logging

from aiohttp import ClientSession, ClientTimeout, ClientError
from llconfig import Config
from llconfig.converters import bool_like

logging.basicConfig(level=logging.INFO)

config = Config()

config.init("URL", str, "https://www.rohlik.cz/services/frontend-service/timeslots-api")

config.init("HTTP_TIMEOUT", lambda val: ClientTimeout(total=int(val)), ClientTimeout(total=10))  # seconds
config.init("HTTP_RAISE_FOR_STATUS", bool_like, True)

config.init("TELEGRAM_BOT_TOKEN", str, None)
config.init("TELEGRAM_URL", str, "https://api.telegram.org/bot{token}/sendMessage")
config.init("TELEGRAM_CHAT_ID", int, None)

config.init("SLEEP", int, 10)  # seconds
config.init("SUCCESS_SLEEP", int, 60)  # seconds
config.init("BACKOFF_SLEEP", int, 10)  # seconds

NO_TIMESLOT_MSG = "\u017d\u00e1dn\u00fd term\u00edn rozvozu"


async def post_telegram(session: ClientSession, text: str):
    telegram_url = config["TELEGRAM_URL"].format(token=config["TELEGRAM_BOT_TOKEN"])
    chat_id = config["TELEGRAM_CHAT_ID"]
    await session.post(telegram_url, data={"chat_id": chat_id, "text": text})


async def download_data(session: ClientSession, url: str) -> str:
    return (await (await session.get(url)).json())["data"]


async def process_timeslots(session, timeslots):
    message = timeslots["firstDeliveryAvailableSinceMessage"]
    logging.info(message)
    sleep = config["SLEEP"]

    if message != NO_TIMESLOT_MSG:
        await post_telegram(session, message)
        sleep = config["SUCCESS_SLEEP"]

    logging.info(f"Sleeping for {sleep=} seconds")
    await asyncio.sleep(sleep)


async def main():
    async with ClientSession(**config.get_namespace("HTTP_")) as session:
        await post_telegram(session, "Starting watcher")
        while True:
            try:
                timeslots = await download_data(session, config["URL"])
                logging.debug("Downloaded timeslots")
            except (ClientError, asyncio.TimeoutError):
                logging.exception("Request failed")
                await asyncio.sleep(config["BACKOFF_SLEEP"])

            await process_timeslots(session, timeslots)


if __name__ == "__main__":
    asyncio.run(main())
