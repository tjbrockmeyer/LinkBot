from Commands.CmdHelper import *
from Main.LinkBot import SUGGESTION_FILE


@command(
    ["{c} <feature>"],
    "Suggest a feature that you think the bot should have. Your suggestion will be saved in a suggestions file.",
    [
        ("{c} Flying puppies please!", "Leaves a suggestion for flying puppies - politely...")
    ]
)
@require_args(1)
async def suggest(cmd: Command):
    with bot.lock:
        with open(SUGGESTION_FILE, 'a') as suggestion_file:
            suggestion_file.write(cmd.argstr + '\n')
    bot.send_message(cmd.channel, 'Your suggestion has been noted!')
