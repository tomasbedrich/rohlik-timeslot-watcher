from aiohttp import ClientTimeout
from llconfig import Config
from llconfig.converters import bool_like

config = Config()

config.init("ROHLIK_URL", str, "https://www.rohlik.cz/services/frontend-service/timeslots-api")

config.init("HTTP_TIMEOUT", lambda val: ClientTimeout(total=int(val)), ClientTimeout(total=10))  # seconds
config.init("HTTP_RAISE_FOR_STATUS", bool_like, True)

config.init("TELEGRAM_BOT_TOKEN", str, None)

config.init("SLEEP", int, 10)  # seconds
config.init("SUCCESS_SLEEP", int, 60)  # seconds
config.init("BACKOFF_SLEEP", int, 10)  # seconds
