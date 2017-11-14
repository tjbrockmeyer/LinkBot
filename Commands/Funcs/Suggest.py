from Commands.CmdHelper import *
from Main.FileWriting import DATA_FOLDER, SUGGESTION_FILE

# suggest a new feature for the bot
def cmd_suggest(cmd: Command):
    logging.info('Command: suggest')

    # Check args exist.
    if len(cmd.args) == 0:
        cmd.OnSyntaxError('You should probably suggest something.')
        return

    with link_bot.lock:
        suggestion_file = open(DATA_FOLDER + SUGGESTION_FILE, 'a')
        suggestion_file.write(cmd.argstr + '\n')
        suggestion_file.close()
    SendMessage(cmd.channel, 'Your suggestion has been noted!')
    logging.info('Suggestion has been noted.')
