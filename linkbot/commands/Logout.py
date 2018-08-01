from linkbot.utils.cmd_utils import *


@command(
    [], "", [],
    aliases=['logoff'],
    show_in_help=False
)
@restrict(OWNER_ONLY)
async def logout(cmd: Command):
    await send_success(cmd.message)
    await client.logout()
    await client.close()


@command(
    [], "", [],
    aliases=['reload', 'reboot'],
    show_in_help=False
)
@restrict(OWNER_ONLY)
async def restart(cmd: Command):
    bot.restart = True
    await logout(cmd)


@command(
    [], "", [],
    show_in_help=False
)
@restrict(OWNER_ONLY)
async def debugcmd(cmd: Command):
    from linkbot.utils.misc import send_split_message
    string = "l" * 2100
    logging.info(string)
    await send_split_message(bot.owner, string)