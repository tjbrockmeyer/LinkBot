from Commands.CmdHelper import *

# Pause/unpause the bot.
def cmd_pause(cmd: Command):
    logging.info("Command: pause/unpause")
    if not bot.send_error_message(cmd.author):
        bot.send_message(cmd.channel, "You must be the owner to use this command.")
        return

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
    logging.info("Bot paused." if bot.paused else "Bot unpaused.")
