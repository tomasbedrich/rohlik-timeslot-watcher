from aiohttp import ClientSession

NO_TIMESLOT_MSG = "\u017d\u00e1dn\u00fd term\u00edn rozvozu"


async def download_timeslots(session: ClientSession, url: str) -> str:
    return (await (await session.get(url)).json())["data"]


def get_free_timeslot(timeslots):
    message = timeslots["firstDeliveryAvailableSinceMessage"]
    return None if message == NO_TIMESLOT_MSG else message


async def _main():
    from config import config
    async with ClientSession(**config.get_namespace("HTTP_")) as session:
        timeslots = await download_timeslots(session, config["ROHLIK_URL"])
        timeslot = get_free_timeslot(timeslots)
        print(f"{timeslot=}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(_main())
