from commands.cmd_utils import *
from datetime import datetime
from discord.utils import get as get_channel


@command(
    ["{c} list", "{c} set <name> <mm/dd>", "{c} remove <name>"],
    "Set, remove, or list the registered birthdays from the database.",
    [
        ("{c} set xCoDGoDx 04/20", "This will set xCoDGoDx's birthday as April 20th."),
        ("{c} list", "will list all birthdays that are registered for this server."),
        ("{c} remove xCoDGoDx", "will remove xCoDGoDx's birthday from the system.")
    ],
    aliases=['bday']
)
@restrict(SERVER_ONLY)
@require_args(1)
async def birthday(cmd: Command):
    # create dict for server if it doesn't exist.
    if cmd.guild.id not in bot.data:
        bot.data[cmd.guild.id] = {}
    if 'birthdays' not in bot.data[cmd.guild.id]:
        bot.data[cmd.guild.id]['birthdays'] = {}

    subcmd = cmd.args[0].lower()
    cmd.shiftargs()
    if subcmd == "set":
        birthday_set(cmd)
    elif subcmd == "remove":
        birthday_remove(cmd)
    elif subcmd == "list":
        birthday_list(cmd)
    else:
        raise CommandSyntaxError(cmd, "Invalid subcommand.")


async def birthday_list(cmd):
    today = datetime.now()
    bdays = []
    for (p, b) in bot.data[cmd.guild.id]['birthdays'].items():
        bday = datetime.strptime(b, "%m/%d")
        if bday.month > today.month or (bday.month == today.month and bday.day >= today.day):
            bdays.append((p, datetime(today.year, bday.month, bday.day)))
        else:
            bdays.append((p, datetime(today.year + 1, bday.month, bday.day)))

    bdays.sort(key=lambda x: x[1])

    send_msg = ""
    for (p, b) in bdays:
        send_msg += p + ": " + b.strftime("%B %d") + "\n"

    if send_msg == "":
        raise CommandError(cmd, "I don't know anyone's birthdays yet.")
    await cmd.channel.send(send_msg)


@restrict(ADMIN_ONLY)
@require_args(2)
@update_database
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
    bot.data[cmd.guild.id]['birthdays'][bdayperson] = bday.strftime("%m/%d")
    await send_success(cmd.message)


@restrict(ADMIN_ONLY)
@require_args(1)
@update_database
async def birthday_remove(cmd):
    person = cmd.args[0]
    if person not in bot.data[cmd.guild.id]['birthdays']:
        raise CommandError(cmd, "{} doesn't have a registered birthday.".format(person))
    bot.data[cmd.guild.id]['birthdays'].pop(person)
    await send_success(cmd.message)
    bot.save_data()


@on_event('ready')
async def birthday_check():
    today = datetime.now()
    for server in bot.client.guilds:
        if server.id in bot.data and 'birthdays' in bot.data[server.id]:
            for p, b in bot.data[server.id]['birthdays'].items():
                bday = datetime.strptime(b, "%m/%d")
                if bday.day == today.day and bday.month == today.month:
                    bot.send_message(get_channel(server.channels, is_default=True), "Today is {}'s birthday!".format(p))

