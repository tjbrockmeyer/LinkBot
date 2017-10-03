from Main.LinkBot import LinkBot
from Sensitive import GOOGLE_API_KEY, RIOT_API_KEY

link_bot = LinkBot(GOOGLE_API_KEY, RIOT_API_KEY)
link_bot.debug = False
