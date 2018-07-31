from linkbot.bot import SUGGESTION_FILE
from linkbot.utils.cmd_utils import *


@command(
    ["{c} <feature>"],
    "Suggest a feature that you think the bot should have. Your suggestion will be saved in a suggestions file.",
    [
        ("{c} Flying puppies please!", "Leaves a suggestion for flying puppies - politely...")
    ]
)
@require_args(1)
async def suggest(cmd: Command):
    with open(SUGGESTION_FILE, 'a') as suggestion_file:
        suggestion_file.write(cmd.argstr + '\n')
    await send_success(cmd.message)
