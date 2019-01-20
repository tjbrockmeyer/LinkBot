
from linkbot.utils.cmd_utils import *
from linkbot.utils.search import search_members, resolve_search_results


@command([], "", [], name='cmdban', show_in_help=False, help_subcommand=False)
@require_args(2)
@restrict(ADMIN_ONLY)
async def command_ban(cmd: Command):
    if cmd.args[0] == 'unban':
        cmd.shiftargs()
        await command_unban(cmd)
        return
    if cmd.args[0] not in bot.commands.keys():
        raise CommandError(cmd, f"`{cmd.args[0]} is not a valid command.")

    async def set_member(m):
        nonlocal member
        member = m

    member = None
    bancmd = cmd.args[0]
    cmd.shiftargs()
    results = search_members(cmd.argstr, cmd.guild)
    await resolve_search_results(results, cmd.argstr, 'members', cmd.author, cmd.channel, set_member)
    if not member:
        return
    if member == cmd.author:
        raise CommandPermissionError(cmd, "You cannot ban yourself.")
    if member == cmd.guild.owner:
        raise CommandError(cmd, "You cannot ban the server owner from commands.")
    with db.Session() as sess:
        sess.create_command_ban(cmd.guild.id, member.id, bancmd)
    await send_success(cmd.message)


@require_args(2)
async def command_unban(cmd: Command):
    if cmd.args[0] not in bot.commands.keys():
        raise CommandError(cmd, f"`{cmd.args[0]} is not a valid command.")

    async def set_member(m):
        nonlocal member
        member = m

    member = None
    bancmd = cmd.args[0]
    cmd.shiftargs()
    results = search_members(cmd.argstr, cmd.guild)
    await resolve_search_results(results, cmd.argstr, 'members', cmd.author, cmd.channel, set_member)
    if not member:
        return
    if member == cmd.author:
        raise CommandPermissionError(cmd, "You cannot ban yourself.")
    if member == cmd.guild.owner:
        raise CommandError(cmd, "You cannot ban the server owner from commands.")
    with db.Session() as sess:
        sess.delete_command_ban(cmd.guild.id, member.id, bancmd)
    await send_success(cmd.message)
