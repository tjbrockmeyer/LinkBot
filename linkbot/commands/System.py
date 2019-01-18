
from linkbot.utils.cmd_utils import *


@command([], "", [], name='infochan', show_in_help=False, help_subcommand=False)
@require_args(1)
@restrict(ADMIN_ONLY)
async def set_info_channel(cmd: Command):
    if not cmd.message.channel_mentions:
        raise CommandSyntaxError(cmd, "You must @ mention a text channel to be the information channel.")
    chan = cmd.message.channel_mentions[0]
    with db.Session() as sess:
        sess.set_info_channel(cmd.guild.id, chan.id)
    await send_success(cmd.message)


@command([], "", [], name='cmdban', show_in_help=False, help_subcommand=False)
@require_args(2)
@restrict(ADMIN_ONLY + DISABLE, reason="Requires database implementation")
async def command_ban(cmd: Command):
    if cmd.args[0] not in bot.commands.keys():
        raise CommandError(cmd, f"`{cmd.args[0]} is not a valid command.")
    if not cmd.message.mentions:
        raise CommandError(cmd, "You must specify someone to ban from the command.")
    if cmd.message.mentions[0] == cmd.guild.owner:
        raise CommandError(cmd, "You cannot ban the server owner from commands.")
    if cmd.message.mentions[0] == cmd.author:
        raise CommandPermissionError(cmd, "You cannot ban yourself.")
    with db.Session() as sess:
        cur.execute("INSERT INTO cmdbans (server_id, user_id, command) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING;",
                    [cmd.guild.id, cmd.message.mentions[0].id, cmd.args[0]])
        conn.commit()
    await send_success(cmd.message)


@command([], "", [], name='cmdunban', show_in_help=False, help_subcommand=False)
@require_args(2)
@restrict(ADMIN_ONLY + DISABLE, reason="Requires database implementation")
async def command_unban(cmd: Command):
    if cmd.args[0] not in bot.commands.keys():
        raise CommandError(cmd, f"`{cmd.args[0]} is not a valid command.")
    if not cmd.message.mentions:
        raise CommandError(cmd, "You must specify someone to unban from the command.")
    if cmd.message.mentions[0] == cmd.author:
        raise CommandPermissionError(cmd, "You cannot unban yourself.")
    with db.Session() as sess:
        cur.execute("DELETE FROM cmdbans WHERE server_id = %s AND user_id = %s AND command = %s;",
                    [cmd.guild.id, cmd.message.mentions[0].id, cmd.args[0]])
        conn.commit()
    await send_success(cmd.message)
