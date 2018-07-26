from Commands.CmdHelper import *
from Main.LinkBot import SUGGESTION_FILE


@require_args(1)
@command
async def suggest(cmd: Command):
    with bot.lock:
        with open(SUGGESTION_FILE, 'a') as suggestion_file:
            suggestion_file.write(cmd.argstr + '\n')
    bot.send_message(cmd.channel, 'Your suggestion has been noted!')
