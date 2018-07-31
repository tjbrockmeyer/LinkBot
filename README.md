# LinkBot
LinkBot is a general-purpose [Discord](http://discordapp.com) bot. He is written in Python, using
[discord.py-rewrite](https://github.com/Rapptz/discord.py) API wrapper
([documentation](https://discordpy.readthedocs.io/en/rewrite/api.html)).

## Some Main Features
- Per-server Admin setting to restrict sensitive commands.
- Birthday tracking on a per-server basis. Birthdays can be set/removed by bot Admins.
- A quote database to store all of your friends' disappointing, out-of-context quotes.
- The ability to remind users about events via the `remind` command.
- Youtube video and Google image first-result search embedding.
- Automatic role-setting for new users in your server.

# Getting Started
To get LinkBot to run, you'll need a config file. If you run the program once, it will automatically generate one for 
you. From here, you can read through the file and fill in the required information (it has lots of comments). You will 
need a bot application and account of your own, and you can get one on the Discord Developer portal 
[here](https://discordapp.com/developers/applications/).

You will also need a Google API key (for image and YouTube searches), a Google Custom Search (also required for image 
search), and a Riot Games API key (for League of Legends game lookup). These are all optional, and if they are not 
included, the functionality will be automatically disabled.

# Commands
LinkBot works like any other discord bot: by reacting to user commands. The prefix for commands is stored in the 
config file, and when LinkBot receives a command in a server that has the prefix attached, or through a direct message 
with/without the prefix, the associated command function for that command will be run.

### Adding Commands
- Create a script for your command at `./linkbot/commands/<yourcommand>.py`.
- Import the helper file: `from linkbot.utils.cmd_utils import *`.
- Create a function for your command: `async def <yourcommand>():`.
- Decorate your function with `@command()` and fill out the required parameters.
- Write your script, using any of the helper functions and decorators that are included from the helper file.
- Possibly add functionality to the main bot files `./linkbot/*` that is required for your command.
- That's it!
  - From here, your command should be callable by addressing the bot using the prefix specified in your config.
  - Your command should also be available via the `help` command.
