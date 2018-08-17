from linkbot.utils.cmd_utils import *
import linkbot.utils.menu as menu
import git
import os



@command([], "", [], aliases=['logoff'], show_in_help=False)
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
        await send_success(cmd.message)
        await force_logout(reload=True)


@command([], "", [], aliases=['upgrade'], show_in_help=False)
@restrict(OWNER_ONLY)
async def update(cmd: Command):
    if bot.debug:
        raise CommandPermissionError(cmd, "Cannot update in debug mode.")

    if await menu.send_confirmation(
            cmd.channel, bot.embed(
            discord.Color.dark_gold(),
            title="Are you sure you want to update the bot?"),
            only_accept=bot.owner):
        logging.info("Pulling to: " + os.getcwd())
        g = git.cmd.Git(os.getcwd())
        g.pull('origin', 'master')
        logging.info("Pull complete.")
        await send_success(cmd.message)
        await force_logout(reload=True)


async def force_logout(*, reload=False):
    bot.restart = reload
    await client.logout()
    await client.close()



@command([], "", [], show_in_help=False)
@restrict(OWNER_ONLY)
async def debug(cmd: Command):
    if not bot.debug:
        return

