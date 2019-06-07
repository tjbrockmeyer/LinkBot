import os
import subprocess

import git

import linkbot.utils.menu as menu
from linkbot.utils.cmd_utils import *


@command([], 'Logs the bot out', [], aliases=['logoff'], show_in_help=False)
@restrict(OWNER_ONLY)
async def logout(cmd: Command):
    if await menu.send_confirmation(
            cmd.channel, bot.embed(
            discord.Color.dark_gold(),
            title="Are you sure you want to log the bot out?"),
            only_accept=bot.owner):
        await send_success(cmd.message)
        await force_logout()


@command([], 'Restarts the bot', [], aliases=['reload', 'reboot'], show_in_help=False)
@restrict(OWNER_ONLY)
async def restart(cmd: Command):
    if await menu.send_confirmation(
            cmd.channel, bot.embed(
            discord.Color.dark_gold(),
            title="Are you sure you want to restart the bot?"),
            only_accept=bot.owner):
        await send_success(cmd.message)
        await force_logout(reload=True)


@command([], 'Updates the bot', [], aliases=['upgrade'], show_in_help=False)
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
    bot.planned_logout = True
    await client.logout()
    await client.close()


@command([], 'Returns the public ip address of the bot', [], aliases=['ip4', 'ip'], show_in_help=False)
@restrict(OWNER_ONLY | DM_ONLY)
async def ipv4(cmd: Command):
    curl = subprocess.run(['curl', 'http://bot.whatismyipaddress.com/'], stdout=subprocess.PIPE, encoding='utf-8',
                          check=True)
    cmd.author.send(curl.stdout)


@command([], "", [], show_in_help=False)
@restrict(OWNER_ONLY)
async def debug(cmd: Command):
    if not bot.debug:
        return

