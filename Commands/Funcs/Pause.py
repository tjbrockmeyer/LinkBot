from Commands.CmdHelper import *


@command(
    ["{c}"],
    "Pause or unpause the bot. Pausing will prevent the bot from receiving commands until unpaused.",
    [
        ("{c}", "Pauses the bot, preventing command processing."),
        ("unpause", "Unpauses the bot, allowing commands to be processed.")
    ],
    aliases=['unpause'],
    show_in_help=False
)
@restrict(OWNER_ONLY)
async def pause(cmd: Command):
    if cmd.command.lower() == "pause":
        if bot.paused:
            bot.send_message(cmd.channel, "The bot is already paused.")
        else:
            bot.paused = True
    elif cmd.command.lower() == "unpause":
        if not bot.paused:
            bot.send_message(cmd.channel, "The bot is already unpaused.")
        else:
            bot.paused = False
    bot.send_message(cmd.author, "Bot paused." if bot.paused else "Bot unpaused.")
