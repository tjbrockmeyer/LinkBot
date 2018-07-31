from linkbot.utils.cmd_utils import *


@command(
    ["{c}"],
    "**Owner Only** Logs the bot out.",
    [
        ("logout", "Logs the bot out.")
    ],
    aliases=['logoff'],
    show_in_help=False
)
@restrict(OWNER_ONLY)
async def logout(cmd: Command):
    await send_success(cmd.message)
    await client.logout()
    await client.close()
