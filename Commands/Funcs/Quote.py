
import random
import re

from Commands.CmdHelper import *


@restrict(SERVER_ONLY)
@require_args(1)
@command
async def quote(cmd: Command):
    # if there have not been any registered quotes yet, create the list.
    if not cmd.guild.id in bot.data:
        bot.data[cmd.guild.id] = {}
    if not 'quotes' in bot.data[cmd.guild.id]:
        bot.data[cmd.guild.id]['quotes'] = []

    subcmd = cmd.args[0]
    cmd.shiftargs()
    if subcmd.isdigit():
        await quote_id(cmd)
    elif subcmd.lower() == "random":
        await quote_random(cmd)
    elif subcmd.lower() == "list":
        await quote_list(cmd)
    elif subcmd.lower() == "add":
        await quote_add(cmd)
    elif subcmd.lower() == "remove":
        await quote_remove(cmd)
    else:
        cmd.on_syntax_error('Invalid sub-command.')


@require_args(1)
def quote_id(cmd):
    qid = int(cmd.args[0])

    # check that quote id is within bounds
    if 0 <= qid < len(bot.data[cmd.guild.id]['quotes']):
        (author, text) = bot.data[cmd.guild.id]['quotes'][qid]
        if author != '':
            bot.send_message(cmd.channel, '{}\n\t\t\t-{}'.format(_nlrepl(text), author))
            logging.info("Quote sent by ID.")
        else:
            cmd.on_syntax_error(str(qid) + ' is not a valid quote ID.')
    else:
        cmd.on_syntax_error(str(qid) + ' is not a valid quote ID.')


def quote_list(cmd):
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
            bot.send_message(cmd.channel, "I don't know any quotes from {}".format(cmd.args[0]))
        else:
            bot.send_message(cmd.channel, "I don't know any quotes yet.")
        return

    # if quotes were found for the author/on the server
    if authorArg == '':
        bot.send_message(cmd.channel, "Quotes from this server:\n{}".format(_nlrepl(quoteList)))
    else:
        bot.send_message(cmd.channel, "Quotes from {}:\n{}".format(cmd.args[1], _nlrepl(quoteList)))


def quote_random(cmd):
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
            bot.send_message(cmd.channel, "I don't know any quotes from {}.".format(cmd.args[1]))
        else:
            bot.send_message(cmd.channel, "I don't know any quotes yet.")
        return

    # seed the random number generator and return a random quote from our choices.
    random.seed()
    author, text = quoteChoices[random.randrange(0, len(quoteChoices))]
    bot.send_message(cmd.channel, "{}\n\t\t\t-{}".format(_nlrepl(text), author))


@restrict(ADMIN_ONLY)
@require_args(2)
@updates_database
def quote_add(cmd):
    q_args = cmd.argstr
    match = re.search('( -\w)', q_args)

    # Author of Quote check
    if match is None:
        cmd.on_syntax_error('To add a quote, include a quote followed by -Author\'s Name.')
        return

    author, text = (q_args[match.start() + 2:], q_args[:match.start()].replace('\n', '\\n'))

    # check to see if there's a missing quote. If so, replace it with the new quote.
    for i in range(0, len(bot.data[cmd.guild.id]['quotes'])):
        if bot.data[cmd.guild.id]['quotes'][i][1] == '':
            bot.data[cmd.guild.id]['quotes'][i] = (author, text.lstrip())
            bot.send_message(cmd.channel, "Added quote with ID {}: \n{} -{}"
                             .format(i, _nlrepl(text), author))
            break

    # if there's not an empty quote, add this quote on the end.
    else:
        bot.data[cmd.guild.id]['quotes'].append((author, text.lstrip()))
        bot.send_message(cmd.channel, "Added quote with ID {}: \n{} -{}"
                         .format(len(bot.data[cmd.guild.id]['quotes']) - 1, _nlrepl(text), author))


@restrict(ADMIN_ONLY)
@require_args(1)
@updates_database
def quote_remove(cmd):
    # ID type-check
    try:
        q_id = int(cmd.args[0])
    except TypeError:
        cmd.on_syntax_error(str(cmd.args[0]) + ' is not a valid quote ID.')
        return
    except IndexError:
        cmd.on_syntax_error("You must provide a quote ID to remove.")
        return

    # Range check, and check that the quote author in the system is not blank (a deleted quote)
    if q_id < 0 or q_id >= len(bot.data[cmd.guild.id]['quotes']) or bot.data[cmd.guild.id]['quotes'][q_id][1] == '':
        bot.send_message(cmd.channel, "That quote ID is not valid. Use `quote list` to find valid IDs.")
        return

    author, text = bot.data[cmd.guild.id]['quotes'][q_id]
    bot.data[cmd.guild.id]['quotes'][q_id] = ('', '')
    bot.send_message(cmd.channel, "Quote removed: {}\n\t\t\t-{}".format(_nlrepl(text), author))


def _nlrepl(q):
    return q.replace('\\n', '\n')
