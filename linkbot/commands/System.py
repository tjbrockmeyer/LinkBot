
from linkbot.utils.cmd_utils import *


@command([], "", [], name='infochan', show_in_help=False, help_subcommand=False)
@require_args(1)
def set_info_channel(cmd: Command):
    if not cmd.message.channel_mentions:
        raise CommandSyntaxError(cmd, "You must @ mention a text channel to be the information channel.")
    chan = cmd.message.channel_mentions[0]
    with db.connect() as (conn, cur):
        cur.execute("UPDATE servers SET info_channel = %s;", [chan.id])
        conn.commit()
    send_success(cmd.message)
