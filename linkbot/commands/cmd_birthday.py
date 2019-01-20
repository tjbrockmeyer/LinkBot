
from linkbot.utils.cmd_utils import *
from linkbot.commands.cmd_info_channel import get_guild_info_channel
from linkbot.utils.misc import english_listing, parse_date
from linkbot.utils.search import search_members, resolve_search_results
from datetime import date, datetime


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


async def birthday_list(cmd: Command):
    now = datetime.now()
    with db.Session() as sess:
        results = sess.get_guild_birthdays(cmd.guild.id)
    bdays = []
    for (p, b) in results:
        if b.month > now.month or (b.month == now.month and b.day >= now.day):
            bdays.append([cmd.guild.get_member(p), datetime(now.year, b.month, b.day)])
        else:
            bdays.append([cmd.guild.get_member(p), datetime(now.year + 1, b.month, b.day)])
    if len(bdays) == 0:
        raise CommandError(cmd, "I don't know anyone's birthdays yet.")
    bdays.sort(key=lambda x: x[1])

    await cmd.channel.send(embed=bot.embed(
        c=discord.Color.purple(),
        title=f"Birthdays for {cmd.guild.name}",
        description="\n".join(f"{p.display_name}: {b.strftime('%B %d')}" for (p, b) in bdays)))


@restrict(ADMIN_ONLY)
@require_args(2)
async def birthday_set(cmd):

    async def set_member(m):
        nonlocal member
        member = m

    person_search = cmd.args[0]
    bdayarg = cmd.args[1]
    # if specified that today is the birthday, set it.
    if bdayarg == "today":
        bday = date.today()
    # otherwise, we'll have to parse it out manually.
    else:
        try:
            bday = parse_date(bdayarg, cmd.args[2] if len(cmd.args) > 2 else "")
        except ValueError:
            # Send error: Invalid format.
            raise CommandSyntaxError(
                cmd, 'Birthdays must be in the format of TB 09/02, TB 09-02, TB Sep 02 or TB September 02.')

    # set the birthday for the server and person.
    member = None
    bday = date(1, bday.month, bday.day)
    s_results = search_members(person_search, cmd.guild)
    await resolve_search_results(s_results, person_search, 'members', cmd.author, cmd.channel, set_member)
    if not member:
        return
    with db.Session() as sess:
        sess.set_birthday(cmd.guild.id, member.id, bday)
    await send_success(cmd.message)



@restrict(ADMIN_ONLY)
@require_args(1)
async def birthday_remove(cmd):

    async def set_member(m):
        nonlocal member
        member = m

    member = None
    person_search = cmd.args[0]
    s_results = search_members(person_search, cmd.guild)
    await resolve_search_results(s_results, person_search, 'members', cmd.author, cmd.channel, set_member)
    if not member:
        return
    with db.Session() as sess:
        sess.remove_birthday(cmd.guild.id, member.id)
    await send_success(cmd.message)


@background_task
async def birthday_check():
    while True:
        for guild in client.guilds:
            with db.Session() as sess:
                m_ids = sess.get_unrecognized_birthdays(guild.id)
                if m_ids:
                    names = [guild.get_member(m_id).display_name for m_id in m_ids]
                    people = english_listing(names)
                    channel = get_guild_info_channel(guild)
                    await channel.send(f"{emoji.Symbol.congratulations}", embed=bot.embed(
                        c=discord.Color.purple(),
                        footer_text=f"Love, Link Bot {emoji.Symbol.heart}",
                        title=f"{emoji.Symbol.birthday} Happy Birthday to {people}! {emoji.Symbol.cake}"))
                    sess.set_birthday_recognition(guild.id, m_ids)
        await asyncio.sleep(900)

