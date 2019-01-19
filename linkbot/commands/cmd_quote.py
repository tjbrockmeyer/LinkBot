
import random
import re

from linkbot.utils.cmd_utils import *
import linkbot.utils.menu as menu
from typing import Iterable, List, Any


@command(
    ["{c} <#id>", "{c} list [author]", "{c} random [author]",
     "{c} add <quote -author>", "{c} remove <#id>"],
    "Get a quote, list them all or add/remove a quote.",
    [
        ("{c} 21", "Writes the quote with an ID of 21. If you don't know the quote ID, use:"),
        ("{c} list", "Lists all quote for the server."),
        ("{c} list LocalIdiot", "This will show all quotes from LocalIdiot."),
        ("{c} random", "Gets a random quote from the server."),
        ("{c} random Jimbob", "gets a random quote from Jimbob."),
        ("{c} add Hey, it's me! -Dawson", "This will add \"Hey, it's me\" as a quote from Dawson."),
        ("{c} add Anyone: Hey Daws.\nDawson: Seeya!",
         "You can separate different parts of a quote using a new line (shift+enter)."),
        ("{c} remove 12",
         "This will remove the quote that has an ID of 12. Remember to check 'quote list' to get the ID!")
    ]
)
@restrict(SERVER_ONLY)
@require_args(1)
async def quote(cmd: Command):
    subcmd = cmd.args[0]
    cmd.shiftargs()
    if subcmd.isdigit():
        await quote_id(cmd, int(subcmd))
    elif subcmd.lower() == "random":
        await quote_random(cmd)
    elif subcmd.lower() == "list":
        await quote_list(cmd)
    elif subcmd.lower() == "add":
        await quote_add(cmd)
    elif subcmd.lower() == "remove":
        await quote_remove(cmd)
    else:
        raise CommandSyntaxError(cmd, 'Invalid sub-command.')


async def quote_id(cmd: Command, q_id: int):
    with db.Session() as sess:
        cur.execute("SELECT author, quote FROM quotes WHERE server_id = %s AND id = %s;", [cmd.guild.id, q_id])
        result: Tuple[str, str] = cur.fetchone()
    if not result:
        raise CommandSyntaxError(cmd, f'`{q_id}` is not a valid quote ID.')
    author, text = result
    await cmd.channel.send(embed=bot.embed(
        discord.Color.blue(), title=f"{q_id}: {author}", description=_nlrepl(text)))


async def quote_list(cmd: Command):
    with db.Session() as sess:
        if cmd.args:
            author = cmd.args[0]
            cur.execute("SELECT id, quote FROM quotes WHERE server_id = %s AND author = %s;",
                        [cmd.guild.id, author])
            result: List[Tuple[int, str]] = sorted(cur.fetchall(), key=lambda x: x[0])
            if not result:
                raise CommandError(cmd, f"I don't know any quotes from {author}.")
            await cmd.channel.send(embed=bot.embed(
                discord.Color.blue(), title=f"Quotes from {author}",
                description="\n".join([f"`{q_id}:`\n{_nlrepl(text)}" for (q_id, text) in result])
            ))
        else:
            cur.execute("SELECT id, author, quote FROM quotes WHERE server_id = %s;",
                        [cmd.guild.id])
            result: List[Tuple[int, str, str]] = sorted(cur.fetchall(), key=lambda x: x[0])
            if not result:
                raise CommandError(cmd, "I don't know any quotes from this server.")

            items = [f"**{q_id}:** {_nlrepl(text)}    -{author}" for (q_id, author, text) in result]
            await menu.send_list(cmd.channel, items, lambda: bot.embed(discord.Color.blue()), "Quotes for this Server")


async def quote_random(cmd: Command):
    random.seed()
    with db.Session() as sess:
        if cmd.args:
            author = cmd.args[0]
            cur.execute("SELECT id, quote FROM quotes WHERE server_id = %s AND author = %s;",
                        [cmd.guild.id, author])
            result = cur.fetchall()
            if not result:
                raise CommandError(cmd, f"I don't know any quotes from {author}.")
            (q_id, text) = random.choice(result)
            await cmd.channel.send(embed=bot.embed(
                discord.Color.blue(), title=f"{q_id}: {author}", description=_nlrepl(text)))
        else:
            cur.execute("SELECT id, author, quote FROM quotes WHERE server_id = %s;",
                        [cmd.guild.id])
            result = cur.fetchall()
            if not result:
                raise CommandError(cmd, "I don't know any quotes from this server.")
            (q_id, author, text) = random.choice(result)
            await cmd.channel.send(embed=bot.embed(
                discord.Color.blue(), title=f"{q_id}: {author}", description=_nlrepl(text)))


@restrict(ADMIN_ONLY)
@require_args(2)
async def quote_add(cmd: Command):
    q_args = cmd.argstr
    match = re.search('( -\w)', q_args)

    # Author of Quote check
    if match is None:
        raise CommandSyntaxError(cmd, 'To add a quote, include a quote followed by -Author\'s Name.')
    author, text = (q_args[match.start() + 2:], q_args[:match.start()].replace('\n', '\\n'))

    # TODO: not correctly identifying which id to use next.
    with db.Session() as sess:
        cur.execute("SELECT id FROM quotes WHERE server_id = %s ORDER BY id;", [cmd.guild.id])
        result = [r[0] for r in cur.fetchall()]
        for (i, j) in enumerate(result):
            if i != j:
                q_id = i
                break
        else:
            q_id = len(result)
        cur.execute(f"INSERT INTO quotes (server_id, id, author, quote) VALUES (%s, %s, %s, %s);",
                    [cmd.guild.id, q_id, author, text])
        conn.commit()
        await cmd.channel.send(embed=bot.embed(
            discord.Color.green(), title=f"Added Quote with ID: {q_id}", description=_nlrepl(text)))


@restrict(ADMIN_ONLY)
@require_args(1)
async def quote_remove(cmd: Command):
    try:
        q_id = int(cmd.args[0])
    except TypeError:
        raise CommandSyntaxError(cmd, str(cmd.args[0]) + ' is not a valid quote ID.')

    with db.Session() as sess:
        cur.execute("SELECT author, quote FROM quotes WHERE server_id = %s AND id = %s;", [cmd.guild.id, q_id])
        result = cur.fetchone()
        if not result:
            raise CommandError(cmd, f"There is not a quote for this server with an id of {q_id}.")
        (author, text) = result
        cur.execute("DELETE FROM quotes WHERE server_id = %s AND id = %s;", [cmd.guild.id, q_id])
        conn.commit()
        await cmd.channel.send(embed=bot.embed(
            discord.Color.blue(), title=f"Quote by {author} removed", description=f"~~{_nlrepl(text)}~~"))


def _nlrepl(q):
    return q.replace('\\n', '\n')
