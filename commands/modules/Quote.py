
from commands.cmd_utils import *

from utils.funcs import send_split_message
import random
import re


@command(
    ["{c} <#id>", "{c} list [author]", "{c} random [author]",
     "{c} add <quote -author>", "{c} remove <#id>"],
    "Get a quote, list them all or add/remove a quote.",
    [
        ("{c} 21", "Writes the quote with an ID of 21. If you don't know the quote ID, use:"),
        (
        "{c} list", "Lists all quote for the server. You can even filter it for only quotes from a particular author:"),
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
    # if there have not been any registered quotes yet, create the list.
    if not cmd.guild.id in bot.data:
        bot.data[cmd.guild.id] = {}
    if not 'quotes' in bot.data[cmd.guild.id]:
        bot.data[cmd.guild.id]['quotes'] = []

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


async def quote_id(cmd, qid):
    # check that quote id is within bounds
    if not 0 <= qid < len(bot.data[cmd.guild.id]['quotes']):
        raise CommandSyntaxError(cmd, str(qid) + ' is not a valid quote ID.')
    (author, text) = bot.data[cmd.guild.id]['quotes'][qid]
    if author == '':
        raise CommandSyntaxError(cmd, str(qid) + ' is not a valid quote ID.')

    await cmd.channel.send('{}\n\t\t\t-{}'.format(_nlrepl(text), author))


async def quote_list(cmd):
    authorArg = cmd.args[0] if len(cmd.args) > 0 else ''
    i = 0
    quoteList = ''
    for (author, text) in bot.data[cmd.guild.id]['quotes']:
        if author != '' and (authorArg == '' or authorArg == author.lower()):
            quoteList += "`{}`: {}   -{}\n".format(i, text, author)
        i += 1

    # if no quotes were found for the author...
    if quoteList == '':
        if authorArg != '':
            raise CommandError(cmd, "I don't know any quotes from {}".format(cmd.args[0]))
        raise CommandError(cmd, "I don't know any quotes yet.")

    # if quotes were found for the author/on the server
    if authorArg == '':
        msg = "Quotes from this server:\n{}".format(_nlrepl(quoteList))
    else:
        msg = "Quotes from {}:\n{}".format(cmd.args[1], _nlrepl(quoteList))
    await send_split_message(cmd.channel, msg)


async def quote_random(cmd):
    authorArg = cmd.args[0] if len(cmd.args) > 1 else ''

    # compile a list of quotes by the author, or all quotes if not specified.
    quoteChoices = list()
    for (author, text) in bot.data[cmd.guild.id]['quotes']:
        # if we are looking to get a random quote from any author, or the quote's author is the one we're looking for...
        if author != '' and (authorArg == '' or authorArg == author.lower()):
            quoteChoices.append((author, text))

    # if we dont have any quotes after going through all of them...
    if len(quoteChoices) == 0:
        if authorArg != '':
            raise CommandError(cmd, "I don't know any quotes from {}.".format(cmd.args[1]))
        raise CommandError(cmd, "I don't know any quotes yet.")

    # seed the random number generator and return a random quote from our choices.
    random.seed()
    author, text = quoteChoices[random.randrange(0, len(quoteChoices))]
    await cmd.channel.send("{}\n\t\t\t-{}".format(_nlrepl(text), author))


@restrict(ADMIN_ONLY)
@require_args(2)
@update_database
async def quote_add(cmd):
    q_args = cmd.argstr
    match = re.search('( -\w)', q_args)

    # Author of Quote check
    if match is None:
        raise CommandSyntaxError(cmd, 'To add a quote, include a quote followed by -Author\'s Name.')

    author, text = (q_args[match.start() + 2:], q_args[:match.start()].replace('\n', '\\n'))

    # check to see if there's a missing quote. If so, replace it with the new quote.
    for i in range(0, len(bot.data[cmd.guild.id]['quotes'])):
        if bot.data[cmd.guild.id]['quotes'][i][1] == '':
            bot.data[cmd.guild.id]['quotes'][i] = (author, text.lstrip())
            await cmd.channel.send("Added quote with ID {}: \n{} -{}".format(i, _nlrepl(text), author))
            break

    # if there's not an empty quote, add this quote on the end.
    else:
        bot.data[cmd.guild.id]['quotes'].append((author, text.lstrip()))
        await cmd.channel.send(
            "Added quote with ID {}: \n{} -{}".format(len(bot.data[cmd.guild.id]['quotes']) - 1, _nlrepl(text), author))


@restrict(ADMIN_ONLY)
@require_args(1)
@update_database
async def quote_remove(cmd):
    # ID type-check
    try:
        q_id = int(cmd.args[0])
    except TypeError:
        raise CommandSyntaxError(cmd, str(cmd.args[0]) + ' is not a valid quote ID.')
    except IndexError:
        raise CommandSyntaxError(cmd, "You must provide a quote ID to remove.")

    # Range check, and check that the quote author in the system is not blank (a deleted quote)
    if q_id < 0 or q_id >= len(bot.data[cmd.guild.id]['quotes']) or bot.data[cmd.guild.id]['quotes'][q_id][1] == '':
        raise CommandError(cmd, "That quote ID is not valid. Use `quote list` to find valid IDs.")

    author, text = bot.data[cmd.guild.id]['quotes'][q_id]
    bot.data[cmd.guild.id]['quotes'][q_id] = ('', '')
    await cmd.channel.send("Quote removed: ~~{}~~\n\t\t\t-~~{}~~".format(_nlrepl(text), author))


def _nlrepl(q):
    return q.replace('\\n', '\n')
