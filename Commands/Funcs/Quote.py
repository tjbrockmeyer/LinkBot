import random
import re

from Commands.CmdHelper import *
from Main.FileWriting import save_quotes


# get, list, add or remove quotes from a server.
def cmd_quote(cmd):
    logging.info('Command: quote')

    # if not on a server, invalid usage.
    if cmd.server is None:
        SendMessage(cmd.channel, "This command can only be used on a server.")
        return

    # if no args, invalid usage.
    if len(cmd.args) == 0:
        cmd.OnSyntaxError('')
        return

    # if there have not been any registered quotes yet, create the list.
    if not cmd.server.id in link_bot.quotes.keys():
        link_bot.quotes[cmd.server.id] = list()

    # if "quote <id>"
    if cmd.args[0].isdigit():
        qid = int(cmd.args[0])

        # check that quote id is within bounds
        if 0 <= qid < len(link_bot.quotes[cmd.server.id]):
            q = link_bot.quotes[cmd.server.id][qid]
            if q[1] != '':
                SendMessage(cmd.channel, '{0}\n\t\t\t-{1}'.format(q[1].replace('\\n', '\n'), q[0]))
                logging.info("Quote sent by ID.")
            else:
                cmd.OnSyntaxError(str(qid) + ' is not a valid quote ID.')
        else:
            cmd.OnSyntaxError(str(qid) + ' is not a valid quote ID.')

    # if "quote random [author]"
    elif cmd.args[0].lower() == "random":

        authorArg = cmd.args[1] if len(cmd.args) > 1 else ''

        # compile a list of quotes by the author, or all quotes if not specified.
        quoteChoices = list()
        for q in link_bot.quotes[cmd.server.id]:
            # if we are looking to get a random quote from any author, or the quote's author is the one we're looking for...
            if q[1] != '' and (authorArg == '' or authorArg == q[0].lower()):
                quoteChoices.append(q)

        # if we dont have any quotes after going through all of them...
        if len(quoteChoices) == 0:
            if authorArg != '':
                SendMessage(cmd.channel, "I don't know any quotes from {0}.".format(cmd.args[1]))
            else:
                SendMessage(cmd.channel, "I don't know any quotes yet.")
            return

        # seed the random number generator and return a random quote from our choices.
        random.seed()
        q = quoteChoices[random.randrange(0, len(quoteChoices))]
        SendMessage(cmd.channel, "{0}\n\t\t\t-{1}".format(q[1].replace('\\n', '\n'), q[0]))
        logging.info("Sent a random quote.")

    # if "quote list [author]"
    elif cmd.args[0].lower() == "list":

        authorArg = cmd.args[1] if len(cmd.args) > 1 else ''

        i = 0
        quoteList = ''
        for q in link_bot.quotes[cmd.server.id]:
            if q[1] != '' and (authorArg == '' or authorArg == q[0].lower()):
                quoteList += "`{0}`: {1}   -{2}\n".format(i, q[1], q[0])
            i += 1

        # if no quotes were found for the author...
        if quoteList == '':
            if authorArg != '':
                SendMessage(cmd.channel, "I don't know any quotes from {0}".format(cmd.args[1]))
            else:
                SendMessage(cmd.channel, "I don't know any quotes yet.")
            return

        # if quotes were found for the author/on the server
        if authorArg == '':
            SendMessage(cmd.channel, "Quotes from this server:\n{0}".format(quoteList.replace('\\n', '\n')))
        else:
            SendMessage(cmd.channel, "Quotes from {0}:\n{1}".format(cmd.args[1], quoteList.replace('\\n', '\n')))
        logging.info("Sent list of quotes.")

    # if "quote add <quote -author>"
    elif cmd.args[0].lower() == "add":

        # Admin check
        if not IsAdmin(cmd.author):
            SendMessage(cmd.author, "You must be an admin to use this command.")
            return

        q_args = cmd.argstr[len('add'):].lstrip()
        match = re.search('( -\w)', q_args)

        # Author of Quote check
        if match is None:
            cmd.OnSyntaxError('To add a quote, include a quote followed by -Author\'s Name.')
            return

        # q_args[0] = author, q_args[1] = quote
        q_args = (q_args[match.start() + 2:], q_args[:match.start()].replace('\n', '\\n'))
        print(q_args)

        # check to see if there's a missing quote. If so, replace it with the new quote.
        for i in range(0, len(link_bot.quotes[cmd.server.id])):
            if link_bot.quotes[cmd.server.id][i][1] == '':
                link_bot.quotes[cmd.server.id][i] = (q_args[0], q_args[1].lstrip())
                SendMessage(cmd.channel, "Added quote with ID {0}: \n{1} -{2}"
                            .format(i, q_args[1].replace('\\n', '\n'), q_args[0]))
                break

        # if there's not an empty quote, add this quote on the end.
        else:
            link_bot.quotes[cmd.server.id].append((q_args[0], q_args[1].lstrip()))
            SendMessage(cmd.channel, "Added quote with ID {0}: \n{1} -{2}"
                        .format(len(link_bot.quotes[cmd.server.id]) - 1, q_args[1].replace('\\n', '\n'), q_args[0]))

        save_quotes()
        logging.info("Added a new quote.")

    # if "@quote remove <id>@"
    elif cmd.args[0].lower() == "remove":

        # Admin Check
        if not IsAdmin(cmd.author):
            SendMessage(cmd.author, "You must be an admin to use this command.")
            return

        # ID type-check and Arg count check
        try:
            cmd.args[1] = int(cmd.args[1])
        except TypeError:
            cmd.OnSyntaxError(str(cmd.args[1]) + ' is not a valid quote ID.')
            return
        except IndexError:
            cmd.OnSyntaxError("You must provide a quote ID to remove.")
            return

        # Range check, and check that the quote author in the system is not blank (a deleted quote)
        if cmd.args[1] < 0 \
                or cmd.args[1] >= len(link_bot.quotes[cmd.server.id]) \
                or link_bot.quotes[cmd.server.id][cmd.args[1]][1] == '':
            SendMessage(cmd.channel, "That quote ID is not valid. Use 'quote list' to find valid IDs.")
            return

        q = link_bot.quotes[cmd.server.id][cmd.args[1]]
        link_bot.quotes[cmd.server.id][cmd.args[1]] = ('', '')
        SendMessage(cmd.channel, "Quote removed: {0}\n\t\t\t-{1}".format(q[1].replace('\\n', '\n'), q[0]))
        save_quotes()
        logging.info("Quote removed.")

    # if "quote <unknown args>"
    else:
        cmd.OnSyntaxError('Invalid sub-command.')

