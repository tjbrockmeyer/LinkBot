from datetime import datetime, timedelta
import asyncio
from linkbot.utils.cmd_utils import *
from linkbot.utils.misc import english_listing


@command(
    ["{c} list", "{c} set <name> <mm/dd>", "{c} remove <name>"],
    "Set, remove, or list the registered birthdays from the database.",
    [
        ("{c} set Bill 04/20", "This will set Bill's birthday as April 20th."),
        ("{c} list", "will list all birthdays that are registered for this server."),
        ("{c} remove Bill", "will remove Bill's birthday from the system.")
    ],
    aliases=['bday']
)
@restrict(SERVER_ONLY)
@require_args(1)
async def birthday(cmd: Command):
    subcmd = cmd.args[0].lower()
    cmd.shiftargs()
    if subcmd == "set":
        await birthday_set(cmd)
    elif subcmd == "remove":
        await birthday_remove(cmd)
    elif subcmd == "list":
        await birthday_list(cmd)
    else:
        raise CommandSyntaxError(cmd, "Invalid subcommand.")


async def birthday_list(cmd):
    now = datetime.now()
    with db.connect() as (conn, cur):
        cur.execute("SELECT person, birthday FROM birthdays WHERE server_id = %s;", [cmd.guild.id])
        vals = cur.fetchall()
    bdays = []
    for (p, b) in vals:
        if b.month > now.month or (b.month == now.month and b.day >= now.day):
            bdays.append([p, datetime(now.year, b.month, b.day)])
        else:
            bdays.append([p, datetime(now.year + 1, b.month, b.day)])
    if len(bdays) == 0:
        raise CommandError(cmd, "I don't know anyone's birthdays yet.")
    bdays.sort(key=lambda x: x[1])

    send_msg = ""
    for (p, b) in bdays:
        send_msg += p + ": " + b.strftime("%B %d") + "\n"
    await cmd.channel.send(send_msg)


@restrict(ADMIN_ONLY)
@require_args(2)
async def birthday_set(cmd):
    bdayperson = cmd.args[0]
    bdayarg = cmd.args[1]
    # if specified that today is the birthday, set it.
    if bdayarg == "today":
        bday = datetime.now()
    # otherwise, we'll have to parse it out manually.
    else:

        # Try 09/02
        try:
            f = "%m/%d"
            bday = datetime.strptime(bdayarg, f)
        except ValueError:

            # Try 09-02
            try:
                f = "%m-%d"
                bday = datetime.strptime(bdayarg, f)
            except ValueError:

                # Try Sep 02
                try:
                    bdayarg2 = cmd.args[2].lower().capitalize()
                    f = "%b %d"
                    bday = datetime.strptime(bdayarg2 + " " + bdayarg2, f)
                except (ValueError, IndexError):

                    # Try September 02
                    try:
                        bdayarg2 = cmd.args[2].lower().capitalize()
                        f = "%B %d"
                        bday = datetime.strptime(bdayarg + " " + bdayarg2, f)
                    except (ValueError, IndexError):

                        # Send error: Invalid format.
                        raise CommandSyntaxError(
                            cmd, 'Birthdays must be in the format of TB 09/02, TB 09-02, TB Sep 02 or TB September 02.')

    # set the birthday for the server and person.
    bday = datetime(year=1, month=bday.month, day=bday.day)
    with db.connect() as (conn, cur):
        cur.execute("DELETE FROM birthdays WHERE server_id = %s AND person = %s;", [cmd.guild.id, bdayperson])
        cur.execute("INSERT INTO birthdays (server_id, person, birthday) VALUES (%s, %s, %s);",
                    [cmd.guild.id, bdayperson, bday])
        conn.commit()
    await send_success(cmd.message)


@restrict(ADMIN_ONLY)
@require_args(1)
async def birthday_remove(cmd):
    person = cmd.args[0]
    with db.connect() as (conn, cur):
        cur.execute("DELETE FROM birthdays WHERE server_id = %s AND person = %s;", [cmd.guild.id, person])
        if cur.rowcount == 0:
            raise CommandError(cmd, f"{person} doesn't have a registered birthday.")
        conn.commit()
    await send_success(cmd.message)


@background_task
async def birthday_check():
    while True:
        now = datetime.now()
        today = datetime(year=1, month=now.month, day=now.day)
        for guild in client.guilds:
            with db.connect() as (conn, cur):
                cur.execute("SELECT person FROM birthdays "
                            "WHERE server_id = %s AND birthday = %s AND last_congrats != %s;",
                            [guild.id, today, now.year])
                results = [r[0] for r in cur.fetchall()]
                people = english_listing(results)
                if results:
                    cur.execute("SELECT info_channel FROM servers WHERE server_id = %s;", [guild.id])
                    chan = cur.fetchone()[0]
                    if not chan:
                        chan = guild.system_channel
                    await chan.send(f"Happy birthday, {people}!")
                    cur.execute("UPDATE birthdays SET last_congrats = %s WHERE person IN %s;",
                                [now.year, tuple(results)])
                    conn.commit()
        await asyncio.sleep(900)

