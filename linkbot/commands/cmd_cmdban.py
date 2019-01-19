
from linkbot.utils.cmd_utils import *


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
    if not cmd.message.mentions:
        raise CommandError(cmd, "You must specify someone to ban from the command.")
    if cmd.message.mentions[0] == cmd.guild.owner:
        raise CommandError(cmd, "You cannot ban the server owner from commands.")
    if cmd.message.mentions[0] == cmd.author:
        raise CommandPermissionError(cmd, "You cannot ban yourself.")
    with db.Session() as sess:
        sess.create_command_ban(cmd.guild.id, cmd.author.id, cmd.args[0])
    await send_success(cmd.message)


@require_args(2)
async def command_unban(cmd: Command):
    if cmd.args[0] not in bot.commands.keys():
        raise CommandError(cmd, f"`{cmd.args[0]} is not a valid command.")
    if not cmd.message.mentions:
        raise CommandError(cmd, "You must specify someone to unban from the command.")
    if cmd.message.mentions[0] == cmd.author:
        raise CommandPermissionError(cmd, "You cannot unban yourself.")
    with db.Session() as sess:
        sess.delete_command_ban(cmd.guild.id, cmd.author.id, cmd.args[0])
    await send_success(cmd.message)
