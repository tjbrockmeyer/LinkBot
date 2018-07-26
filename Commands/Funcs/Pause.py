from Commands.CmdHelper import *


@restrict(OWNER_ONLY)
@command
def pause(cmd: Command):
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
