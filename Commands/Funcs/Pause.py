from Commands.CmdHelper import *

# Pause/unpause the bot.
def cmd_pause(cmd: Command):
    logging.info("Command: pause/unpause")
    if not IsOwner(cmd.author):
        SendMessage(cmd.channel, "You must be the owner to use this command.")
        return

    if cmd.command.lower() == "pause":
        if link_bot.paused:
            SendMessage(cmd.channel, "The bot is already paused.")
        else:
            link_bot.paused = True
    elif cmd.command.lower() == "unpause":
        if not link_bot.paused:
            SendMessage(cmd.channel, "The bot is already unpaused.")
        else:
            link_bot.paused = False

    SendMessage(cmd.author, "Bot paused." if link_bot.paused else "Bot unpaused.")
    logging.info("Bot paused." if link_bot.paused else "Bot unpaused.")
