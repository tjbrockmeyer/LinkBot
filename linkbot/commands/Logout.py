from linkbot.utils.cmd_utils import *


@command(
    ["{c}"], "", [],
    aliases=['logoff'],
    show_in_help=False
)
@restrict(OWNER_ONLY)
async def logout(cmd: Command):
    await send_success(cmd.message)
    await client.logout()
    await client.close()


@command(
    ["{c}"], "", [],
    aliases=['reload', 'reboot'],
    show_in_help=False
)
@restrict(OWNER_ONLY)
async def restart(cmd: Command):
    bot.restart = True
    await logout(cmd)
