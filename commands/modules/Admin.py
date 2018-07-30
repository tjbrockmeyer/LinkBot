from commands.cmd_utils import *
from functools import reduce
import utils.database as db


@command(
    ["{c} list", "admin add <@user|@role>", "admin remove <@user|@role>"],
    "List admins, or add/remove them.",
    [
        ("{c} list", "Lists all of the admins for this server."),
        ("{c} add @JoeBlow", "Adds JoeBlow as an admin. This has to be a valid mention!"),
        ("{c} add @TheBigDawgs", "If TheBigDawgs is a role, adds all members of TheBigDawgs as admins."),
        ("{c} add @JoeBlow @TheBigDawgs", "Chain mentions together to add multiple people and/or roles as admins"),
        ("{c} remove @JoeBlow @TheBigDawgs", "Removing admins works the same way.")
    ]
)
@restrict(SERVER_ONLY)
@require_args(1)
async def admin(cmd: Command):
    subcmd = cmd.args[0].lower()
    cmd.shiftargs()
    if subcmd == "list":
        await admin_list(cmd)
    elif subcmd == "add":
        await admin_add(cmd)
    elif subcmd == "remove":
        await admin_remove(cmd)
    else:
        raise CommandSyntaxError(cmd, '{} is not a valid subcommand.'.format(subcmd))


async def admin_list(cmd):
    with db.connect() as (conn, cur):
        cur.execute(
            """
            SELECT user_id FROM admins
            WHERE server_id = %s;
            """, [cmd.guild.id])
        admins = [x[0] for x in cur.fetchall()]

        # Check for existing admins
        if len(admins) == 0:
            raise CommandError(cmd, 'There are no admins on this server.')

        # get the admin names from their IDs, save them to a string, then send it to the channel.
        admins = [str(client.get_user(x)) for x in admins]
        if len(admins) == 1:
            admins = "Admin: " + admins[0]
        else:
            admins = reduce(lambda x, y: "{}, {}".format(x, y), admins, "Admins: ")
        await cmd.channel.send(admins)


@restrict(ADMIN_ONLY)
async def admin_add(cmd):
    if len(cmd.message.mentions) == 0 and len(cmd.message.role_mentions) == 0:
        raise CommandSyntaxError(cmd, "You must at-mention at least one role or user.")

    with db.connect() as (conn, cur):
        mentions = [m.id for m in cmd.message.mentions] + [m.id for r in cmd.message.role_mentions for m in r.members]
        values = ','.join(cur.mogrify('(%s,%s)', (cmd.guild.id, m)) for m in mentions)
        query = 'INSERT INTO admins (server_id, user_id) VALUES {} ON CONFLICT DO NOTHING;'.format(values)
        cur.execute(query)
        conn.commit()
    await send_success(cmd.message)


@restrict(ADMIN_ONLY)
async def admin_remove(cmd):
    if len(cmd.message.mentions) == 0 and len(cmd.message.role_mentions) == 0:
        raise CommandSyntaxError(cmd, "You must at-mention at least one role or user.")

    with db.connect() as (conn, cur):
        mentions = [m.id for m in cmd.message.mentions] + [m.id for r in cmd.message.role_mentions for m in r.members]
        cur.execute(
            """
            DELETE FROM admins 
            WHERE server_id = %s AND user_id IN %s;
            """, [cmd.guild.id, tuple(mentions)])
        conn.commit()
    await send_success(cmd.message)
