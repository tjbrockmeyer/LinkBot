import linkbot.utils.menu as menu
import linkbot.utils.queries.management as management_queries
import linkbot.utils.queries.quote as queries
from linkbot.utils.cmd_utils import *
from linkbot.utils.search import search_members, resolve_search_results


@command(
    [
        "{c} say <author>: <start of quote>",
        "{c} list [author]",
        "{c} add <author>: <full quote>",
        "{c} remove <author>: <start of quote>",
        "{c} say <quote reference>",
        "{c} ref add <ref text>: <author>: <start of quote>",
        "{c} ref remove <ref text>"
    ],
    "Say a quote, list them all or add/remove a quotes/quote refs.",
    [
        ("{c} say Jimbob: I wanna", "Says the quote by Jimbob that starts with 'I wanna'."),
        ("{c} say monkey", "Says the quote that has been given the reference text 'monkey'."),
        ("{c} list", "Lists all quote for the server."),
        ("{c} list LocalIdiot", "This will show all quotes from LocalIdiot."),
        ("{c} add Dawson: Hey, it's me!", "This will add \"Hey, it's me\" as a quote from Dawson."),
        ("{c} add Dawson: (anyone) Hey Daws.\n(Dawson) Seeya!",
         "You can separate different parts of a quote using a new line (shift+enter)."),
        ("{c} remove Jimbob: I used to", "Deletes the quote by Jimbob that starts with 'I used to'"),
        ("{c} remove monkey", "Deletes the quote that was given the reference text 'monkey'."),
        ("{c} ref add monkey: Jimbob: I'm a",
         "Associates the quote by Jimbob that starts with 'I'm a' with the reference text 'monkey'."),
        ("{c} ref remove monkey",
         "Disassociates the reference text 'monkey' from the quote that it currently references.")
    ],
    aliases=['quotes']
)
@restrict(SERVER_ONLY)
@require_args(1)
async def quote(cmd: Command):
    subcmd = cmd.args[0].lower()
    cmd.shiftargs()
    if subcmd in ['say', 'get']:
        await quote_say(cmd)
    elif subcmd == "list":
        await quote_list(cmd)
    elif subcmd in ['add', 'create']:
        await quote_add(cmd)
    elif subcmd in ['remove', 'delete']:
        await quote_remove(cmd)
    elif subcmd in ['ref', 'reference']:
        await quote_ref(cmd)
    else:
        raise CommandSyntaxError(cmd, f"Invalid sub-command: '{subcmd}'")


def quote_to_message(person, said, ref=None):
    r = f" __{{{ref}}}__" if ref else ''
    return f"**{person}**{r}: {said}"


@require_args(1)
async def quote_say(cmd: Command):

    async def set_member(m):
        nonlocal member
        member = m

    if ':' not in cmd.argstr:
        async with await db.Session.new() as sess:
            q = await queries.get_quote_with_ref(sess, cmd.guild.id, cmd.argstr)
        if not q:
            raise CommandError(cmd, f"'{cmd.argstr} is not a valid quote reference.")
        q = quote_to_message(cmd.guild.get_member(q[0]).display_name, q[1], cmd.argstr)
    else:
        member = None
        break_index = cmd.argstr.index(':')
        person, said = cmd.argstr[:break_index].strip(), cmd.argstr[break_index + 1:].strip()
        results = search_members(person, cmd.guild)
        await resolve_search_results(results, person, 'members', cmd.author, cmd.channel, set_member)
        if not member:
            return
        async with await db.Session.new() as sess:
            result = await queries.get_quote_starts_with(sess, cmd.guild.id, member.id, said)
        if not result:
            raise CommandError(cmd, f"{member.display_name} has no quotes that start with '{said}'.")
        q = quote_to_message(member.display_name, result[0], result[1])

    await cmd.channel.send(embed=bot.embed(
        c=discord.Color.dark_green(),
        title="Quote",
        description=q))


async def quote_list(cmd: Command):

    async def set_member(m):
        nonlocal member
        member = m

    if cmd.args:
        # List for single member of the guild.
        member = None
        results = search_members(cmd.argstr, cmd.guild)
        await resolve_search_results(results, cmd.argstr, 'members', cmd.author, cmd.channel, set_member)
        if not member:
            return
        async with await db.Session.new() as sess:
            results = await queries.get_quotes_from_member(sess, cmd.guild.id, member.id)
        if not results:
            raise CommandError(cmd, f"I don't know any quotes by {member.display_name}.")
        await menu.send_list(
            cmd.channel,
            [quote_to_message("  ", r[0], r[1]) for r in results],
            lambda: bot.embed(c=discord.Color.dark_green(), title="Quote List"),
            f"By {member.display_name}:")

    else:
        # List for full guild.
        async with await db.Session.new() as sess:
            results = await queries.get_guild_quotes(sess, cmd.guild.id)
        if not results:
            raise CommandError(cmd, f"I don't know any quotes from {cmd.guild.name}.")
        await menu.send_list(
            cmd.channel,
            [quote_to_message(cmd.guild.get_member(r[0]).display_name, r[1], r[2]) for r in results],
            lambda: bot.embed(c=discord.Color.dark_green(), title="Quote List"),
            f"For {cmd.guild.name}")


@restrict(ADMIN_ONLY)
@require_args(2)
async def quote_add(cmd: Command):

    async def set_member(m):
        nonlocal member
        member = m

    member = None
    if not ':' in cmd.argstr:
        raise CommandSyntaxError(cmd, "A ':' is required to show who said the quote.")
    break_index = cmd.argstr.index(':')
    person, said = cmd.argstr[:break_index].strip(), cmd.argstr[break_index + 1:].strip()
    results = search_members(person, cmd.guild)
    await resolve_search_results(results, person, 'members', cmd.author, cmd.channel, set_member)
    if not member:
        return
    async with await db.Session.new() as sess:
        await queries.create_quote(sess, cmd.guild.id, member.id, said)
    await send_success(cmd.message)


@restrict(ADMIN_ONLY)
@require_args(1)
async def quote_remove(cmd: Command):

    async def set_member(m):
        nonlocal member
        member = m

    if ':' not in cmd.argstr:
        async with await db.Session.new() as sess:
            result = await queries.get_quote_with_ref(sess, cmd.guild.id, cmd.argstr)
            if not result:
                raise CommandError(cmd, f"'{cmd.argstr} is not a valid quote reference.")
            do_it = await menu.send_confirmation(
                cmd.channel,
                bot.embed(
                    c=discord.Color.dark_green(),
                    title="Delete this quote?",
                    description=quote_to_message(cmd.guild.get_member(result[0]).display_name, result[1], cmd.argstr)),
                only_accept=cmd.author)
            if do_it:
                await management_queries.delete_node_with_id(sess, result[2])
                await send_success(cmd.message)
    else:
        member = None
        break_index = cmd.argstr.index(':')
        person, said = cmd.argstr[:break_index].strip(), cmd.argstr[break_index + 1:].strip()
        results = search_members(person, cmd.guild)
        await resolve_search_results(results, person, 'members', cmd.author, cmd.channel, set_member)
        if not member:
            return
        async with await db.Session.new() as sess:
            result = await queries.get_quote_starts_with(sess, cmd.guild.id, member.id, said)
            if not result:
                raise CommandError(cmd, f"{member.display_name} has no quotes that start with '{said}'.")
            do_it = await menu.send_confirmation(
                cmd.channel,
                bot.embed(
                    c=discord.Color.dark_green(),
                    title="Delete this quote?",
                    description=quote_to_message(member.display_name, result[0], result[1])),
                only_accept=cmd.author)
            if do_it:
                await management_queries.delete_node_with_id(sess, result[2])
                await send_success(cmd.message)


@restrict(ADMIN_ONLY)
@require_args(2)
async def quote_ref(cmd: Command):

    async def set_member(m):
        nonlocal member
        member = m

    subcmd = cmd.args[0]
    cmd.shiftargs()
    if subcmd in ['add', 'set']:
        member = None
        try:
            ci1 = cmd.argstr.index(':')
            ci2 = cmd.argstr.index(':', ci1 + 1)
        except ValueError:
            raise CommandSyntaxError(cmd, "Arguments must be in the form of: \"reference: author: quote\"")
        ref, person, said = cmd.argstr[:ci1].strip(), cmd.argstr[ci1 + 1:ci2].strip(), cmd.argstr[ci2 + 1:].strip()
        results = search_members(person, cmd.guild)
        await resolve_search_results(results, person, 'members', cmd.author, cmd.channel, set_member)
        if not member:
            return
        async with await db.Session.new() as sess:
            await queries.set_quote_reference(sess, cmd.guild.id, member.id, said, ref)
        await send_success(cmd.message)

    elif subcmd in ['delete', 'remove']:
        async with await db.Session.new() as sess:
            await queries.remove_quote_reference(sess, cmd.guild.id, cmd.argstr)
        await send_success(cmd.message)

    else:
        raise CommandSyntaxError(cmd, f"Invalid subcommand: '{subcmd}'")


