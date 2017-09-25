from CommandFuncs import *

COMMANDS = {
    'help': {
        'func': cmd_help,
        'syntax': "`help [here] [command]`",
        'help': "{syntax}: Pastes help into a DM with the user who sent the command.\n"
            "{prefix}help here\t\t\t\tWrites the help panel to the channel you asked for it in.\n"
            "{prefix}help quote\t\t\t\tGets specific help for the 'quote' command.\n"
            "{prefix}help here quote\t\t\t\tWrites that specific help to the channel you asked for it in."
    },
    'migrate': {
        'func': cmd_migrate,
        'syntax': "`migrate <channel 1>, <channel 2>`",
        'help': "{syntax}: Moves all members inside voice channel 1 to voice channel 2.\n"
               "{prefix}migrate BK lounge, The Potion Shop\t\t\t\tMoves everyone in the BK Lounge to the Potion Shop.\n"
               "\t\t\t\tIt's not case sensitive, so you could also use:\n"
               "{prefix}migrate bk lounge, the potion shop\t\t\t\tand it would still work with the same effect."
    },
    'quote': {
        'func': cmd_quote,
        'syntax': "`quote <#id>` or `quote list [author]` or `quote random [author]`\n"
                  "\t or `quote add <quote -author>` or `quote remove <#id>`",
        'help': "{syntax}: Get a quote, list them all or add/remove a quote.\n"
              "Adding or removing quote is an Admin Only privilege.\n"
              "{prefix}quote 21\t\t\t\tWrites the quote with an ID of 21. If you don't know the quote ID, use:\n"
              "{prefix}quote list\t\t\t\tLists all quote for the server. You can even filter it for only quote from a particular author:\n"
              "{prefix}quote list LocalIdiot\t\t\t\tThis will show all quote from LocalIdiot.\n"
              "{prefix}quote random\t\t\t\tGets a random quote from the server."
              "{prefix}quote random Jimbob\t\t\t\tgets a random quote from Jimbob."
              "{prefix}quote add Hey, it's me! -Dawson\t\t\t\tThis will add \"Hey, it's me\" as a quote from Dawson.\n"
              "\t\t\t\tYou can separate different parts of a quote using `shift+enter` to start a new line.\n"
              "\t\t\t\tYou still need a quote author at the end, so don't forget!\n"
              "{prefix}quote remove 12\t\t\t\tThis will remove the quote that has an ID of 12. Remember to check '{prefix}quote list' to get the ID!"
    },
    'birthday': {
        'func': cmd_birthday,
        'syntax': "`birthday list` or `birthday set <name> <mm/dd>` or `birthday remove <name>`",
        'help': "{syntax}: Set, remove, or list the registered birthdays from the database.\n"
                "Setting and removing birthdays is an Admin Only privilege.\n"
                "{prefix}birthday set xCoDGoDx 04/20\t\t\t\tThis will set xCoDGoDx's birthday as April 20th.\n"
                "{prefix}birthday list\t\t\t\twill list all birthdays that are registered for this server.\n"
                "{prefix}birthday remove xCoDGoDx\t\t\t\twill remove xCoDGoDx's birthday from the system."
    },
    'lolgame': {
        'func': cmd_lolgame,
        'syntax': "`lolgame <summoner name> [region]`",
        'help': "{syntax}: Sends info to the channel about `summoner`'s current League of Legends game.\n"
               "{prefix}lolgame TheBootyToucher\t\t\t\tLooks up and posts information in the chat about TheBootyToucher's league of legends game.\n"
               "\t\t\t\tSummoner names are not case-sensitive, and they also do not require you to use spaces in the name. Therefore:\n"
               "{prefix}lolgame thebootytoucher\t\t\t\twill correctly retrieve the player's info, even if his name is something like, 'ThE BoOtY tOuChEr'.\n"
               "{prefix}lolgame thebootytoucher, kr\t\t\t\tWill look on the Korean servers for the player's game. You can specify any region, but you'll need to know the region ID yourself."
    },
    'yt': {
        'alias': 'youtube'
    },
    'youtube': {
        'func': cmd_youtube,
        'syntax': "`youtube <query>` or `yt <query>`",
        'help': "{syntax}: Links the first video result of a YouTube search for `query`\n"
          "{prefix}youtube the dirtiest of dogs\t\t\t\tThis will link the first youtube video found in the search results for 'the dirtiest of dogs'.\n"
          "{prefix}yt why did i do that\t\t\t\tYou can also use just 'yt' instead of typing out 'youtube'."
    },
    'img': {
        'alias': 'image'
    },
    'image': {
        'func': cmd_image,
        'syntax': "`image <query>` or `img <query>`",
        'help': "{syntax}: Links the first image result of a Google Image search for `query`.\n"
           "{prefix}image what blind people see\t\t\t\tLinks the first result of a google image search for 'what blind people see'.\n"
           "{prefix}img i don't know what i expected\t\t\t\tYou can also use simply 'img' instead of typing out 'image'."
    },
    'play': {
        'func': cmd_play,
        'syntax': "`play`",
        'help': "{syntax}: Plays something in voice chat with you!"
    },
    'suggest': {
        'func': cmd_suggest,
        'syntax': "`suggest <feature>`",
        'help': "{syntax}: Suggest a feature that you think the bot should have. Your suggestion will be saved in a suggestions file.\n"
               "{prefix}suggest Flying puppies please!\t\t\t\tThis will leave a suggestion for flying puppies - politely..."
    },
    'nsfw': {
        'func': cmd_nsfw,
        'syntax': "`nsfw <on|off>`",
        'help': "{syntax}: View the state of the NSFW filter, or **Admin Only** turn it `on` or `off`.\n"
            "\t\t\t\t\tCurrently, it is always disabled due to a bug with Google's API."
    },
    'admin': {
        'func': cmd_admin,
        'syntax': "`admin list` or `admin add <@user|@role>` or `admin remove <@user|@role>`",
        'help': "{syntax}: List admins, or add/remove them, but only admins or the bot owner can add/remove admins.\n"
             "{prefix}admin list\t\t\t\tThis will list all of the admins for this server.\n"
             "{prefix}admin add @JoeBlow\t\t\t\tWill add JoeBlow as an admin. This has to be a valid mention too!\n"
             "{prefix}admin add @TheBigDawgs\t\t\t\tIf TheBigDawgs is a role, this will add all members of TheBigDawgs as admins. Convenience!\n"
             "\t\t\t\tSpeaking of convenience, you can also chain your mentions together to add multiple people and/or roles as admins:\n"
             "{prefix}admin add @JoeBlow @JoeShmoe @JohnDoe @TheBigDawgs @TheSmallDawgs\n"
             "{prefix}admin remove @JoeBlow @TheBigDawgs\t\t\t\tRemoving admins works the same way."
    },
    'logoff': {
        'alias': 'logout'
    },
    'logout': {
        'func': cmd_logout,
        'syntax': "`logout` or `logoff`",
        'help': "{syntax}: **Owner Only** Logs the bot out."
    }
}