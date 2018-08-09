from linkbot.utils.cmd_utils import *
import linkbot.utils.menu as menu



@command( [], "", [], aliases=['logoff'], show_in_help=False)
@restrict(OWNER_ONLY)
async def logout(cmd: Command):
    if await menu.send_confirmation(
            cmd.channel, bot.embed(
            discord.Color.dark_gold(),
            title="Are you sure you want to log the bot out?"),
            only_accept=bot.owner):
        await send_success(cmd.message)
        await force_logout()


@command([], "", [], aliases=['reload', 'reboot'], show_in_help=False)
@restrict(OWNER_ONLY)
async def restart(cmd: Command):
    if await menu.send_confirmation(
            cmd.channel, bot.embed(
            discord.Color.dark_gold(),
            title="Are you sure you want to restart the bot?"),
            only_accept=bot.owner):
        bot.restart = True
        await force_logout()


async def force_logout():
    await client.logout()
    await client.close()



@command([], "", [], show_in_help=False)
@restrict(OWNER_ONLY)
async def debug(cmd: Command):
    if not bot.debug:
        return

