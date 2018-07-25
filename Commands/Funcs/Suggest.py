from Commands.CmdHelper import *
from Main.LinkBot import SUGGESTION_FILE

# suggest a new feature for the bot
def cmd_suggest(cmd: Command):
    logging.info('Command: suggest')

    # Check args exist.
    if len(cmd.args) == 0:
        cmd.on_syntax_error('You should probably suggest something.')
        return

    with bot.lock:
        with open(SUGGESTION_FILE, 'a') as suggestion_file:
            suggestion_file.write(cmd.argstr + '\n')
    bot.send_message(cmd.channel, 'Your suggestion has been noted!')
    logging.info('Suggestion has been noted.')
