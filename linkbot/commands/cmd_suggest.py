from linkbot.utils.cmd_utils import *


@command(
    ["{c} add <feature>", "{c} remove <id>", "{c} list"],
    "Suggest a feature that you think the bot should have. Your suggestion will be saved in a suggestions file.",
    [
        ("{c} add some cool stuff", "Suggests that some cool stuff gets added."),
        ("{c} remove 5", "Removes the 5th suggestion from the list."),
        ("{c} list", "Lists all of the given suggestions.")
    ]
)
@require_args(1)
@restrict(DISABLE, reason="Requires updating to enable github issue creation")
async def suggest(cmd: Command):
    if not cmd.args:
        raise CommandSyntaxError(cmd, "You must specify a suggestion.")
    async with await db.Session.new() as sess:
        pass
    await send_success(cmd.message)
