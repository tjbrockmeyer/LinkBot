# LinkBot
Hello! This is my discord bot, LinkBot. He is made in Python, using [Discord.py](https://github.com/Rapptz/discord.py). You can find the documentation [here](https://discordpy.readthedocs.io/en/latest/index.html).
## Features
- A per-server Admin system that restricts Admin level commands from being used by non-admins.
- A per-server Quote database in which Admins can immortalize their friends' most disappointing, out-of-context statements.
- A per-server Birthday tracking system. Have an Admin set birthdays for everyone (who is important) and have LinkBot wish them Happy Birthday when it comes!
- Youtube video and Google image first-result search embedding.
- Plus more, and more to come in the future!
## Getting Started
To get LinkBot to run, you'll need a config file. If you run the program once, it will automatically generate one for you. From here, you can read through the file and fill in the required information (it has lots of comments). You will need a bot application and account of your own, and you can get one on the Discord Developer portal [here](https://discordapp.com/developers/applications/). 

You will also need a Google API key (for image and YouTube searches), a Google Custom Search (also required for image search), and a Riot Games API key (for League of Legends game lookup). These are all optional, and if they are not included, the functionality will be automatically disabled.

# Commands
LinkBot works like any other discord bot: by reacting to user commands. The prefix for commands is stored in the config file, and when LinkBot receives a command
in a server that has the prefix attached, or through a direct message with/without the prefix, the associated command function for that command will be run.

Commands each have their own .py file that holds their function (Commands/Funcs/*.py). Commands also have an entry in the Command Data dictionary (Commands/Data.py).
The Command's function defines what happens when the command is run, and the Command Data dictionary defines the usage of the command, including a reference to its function.
It is in the Command Data dictionary that aliases for commands can be defined. Some aliases already exist (youtube/yt, image/img, ...). An alias for the main command is specified by using the
'alias' key with the name of the main command as the value. A command lookup will automatically return the main command.

## Adding Commands
- Create a script for your command at `Commands/Funcs/<yourcommand>.py`.
- Import the helper files: `from Commands.CmdHelper import *`.
- Create a function for your command: `async def <yourcommand>():`.
- Decorate your function with `@command()` and fill out the required parameters.
- Write your script, using any of the helper functions and decorators that are included from `Commands.CmdHelper`.
- Possibly add functionality to the main bot files `Main/*` that is required for your command.
- That's it! 
  - From here, your command should be callable by addressing the bot using the prefix specified in your config.
  - Your command should also be available via the `help` command.

## Recent List of Commands
```
  admin list  |  admin add <@user|@role>...  |  admin remove <@user|@role>...
  birthday list  |  birthday set <name> <mm/dd>  |  birthday remove <name>
  help [here] [command]
  image <query>  |  img <query>
  logout  |  logoff
  lolgame <player> [,region]
  migrate <ch>, <ch>
  pause  |  unpause
  quote <#id>  |  quote list [author]  |  quote random [author]
    |  quote add <quote -author>  |  quote remove <#id>
  suggest <feature>
  youtube <query>  |  yt <query> 
```
