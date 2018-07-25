import random
import re

from Commands.CmdHelper import *


# get, list, add or remove quotes from a server.
def cmd_quote(cmd: Command):
    logging.info('Command: quote')

    # if not on a server, invalid usage.
    if cmd.guild is None:
        bot.send_message(cmd.channel, "This command can only be used on a server.")
        return

    # if no args, invalid usage.
    if len(cmd.args) == 0:
        cmd.on_syntax_error('')
        return

    # if there have not been any registered quotes yet, create the list.
    if not cmd.guild.id in bot.data:
        bot.data[cmd.guild.id] = {}
    if not 'quotes' in bot.data[cmd.guild.id]:
        bot.data[cmd.guild.id]['quotes'] = []

    # if "quote <id>"
    if cmd.args[0].isdigit():
        qid = int(cmd.args[0])

        # check that quote id is within bounds
        if 0 <= qid < len(bot.data[cmd.guild.id]['quotes']):
            q = bot.data[cmd.guild.id]['quotes'][qid]
            if q[1] != '':
                bot.send_message(cmd.channel, '{0}\n\t\t\t-{1}'.format(q[1].replace('\\n', '\n'), q[0]))
                logging.info("Quote sent by ID.")
            else:
                cmd.on_syntax_error(str(qid) + ' is not a valid quote ID.')
        else:
            cmd.on_syntax_error(str(qid) + ' is not a valid quote ID.')

    # if "quote random [author]"
    elif cmd.args[0].lower() == "random":

        authorArg = cmd.args[1] if len(cmd.args) > 1 else ''

        # compile a list of quotes by the author, or all quotes if not specified.
        quoteChoices = list()
        for q in bot.data[cmd.guild.id]['quotes']:
            # if we are looking to get a random quote from any author, or the quote's author is the one we're looking for...
            if q[1] != '' and (authorArg == '' or authorArg == q[0].lower()):
                quoteChoices.append(q)

        # if we dont have any quotes after going through all of them...
        if len(quoteChoices) == 0:
            if authorArg != '':
                bot.send_message(cmd.channel, "I don't know any quotes from {0}.".format(cmd.args[1]))
            else:
                bot.send_message(cmd.channel, "I don't know any quotes yet.")
            return

        # seed the random number generator and return a random quote from our choices.
        random.seed()
        q = quoteChoices[random.randrange(0, len(quoteChoices))]
        bot.send_message(cmd.channel, "{0}\n\t\t\t-{1}".format(q[1].replace('\\n', '\n'), q[0]))
        logging.info("Sent a random quote.")

    # if "quote list [author]"
    elif cmd.args[0].lower() == "list":

        authorArg = cmd.args[1] if len(cmd.args) > 1 else ''

        i = 0
        quoteList = ''
        for q in bot.data[cmd.guild.id]['quotes']:
            if q[1] != '' and (authorArg == '' or authorArg == q[0].lower()):
                quoteList += "`{0}`: {1}   -{2}\n".format(i, q[1], q[0])
            i += 1

        # if no quotes were found for the author...
        if quoteList == '':
            if authorArg != '':
                bot.send_message(cmd.channel, "I don't know any quotes from {0}".format(cmd.args[1]))
            else:
                bot.send_message(cmd.channel, "I don't know any quotes yet.")
            return

        # if quotes were found for the author/on the server
        if authorArg == '':
            bot.send_message(cmd.channel, "Quotes from this server:\n{0}".format(quoteList.replace('\\n', '\n')))
        else:
            bot.send_message(cmd.channel, "Quotes from {0}:\n{1}".format(cmd.args[1], quoteList.replace('\\n', '\n')))
        logging.info("Sent list of quotes.")

    # if "quote add <quote -author>"
    elif cmd.args[0].lower() == "add":

        # Admin check
        if not bot.is_admin(cmd.author):
            bot.send_message(cmd.author, "You must be an admin to use this command.")
            return

        q_args = cmd.argstr[len('add'):].lstrip()
        match = re.search('( -\w)', q_args)

        # Author of Quote check
        if match is None:
            cmd.on_syntax_error('To add a quote, include a quote followed by -Author\'s Name.')
            return

        # q_args[0] = author, q_args[1] = quote
        q_args = (q_args[match.start() + 2:], q_args[:match.start()].replace('\n', '\\n'))

        # check to see if there's a missing quote. If so, replace it with the new quote.
        for i in range(0, len(bot.data[cmd.guild.id]['quotes'])):
            if bot.data[cmd.guild.id]['quotes'][i][1] == '':
                bot.data[cmd.guild.id]['quotes'][i] = (q_args[0], q_args[1].lstrip())
                bot.send_message(cmd.channel, "Added quote with ID {0}: \n{1} -{2}"
                                 .format(i, q_args[1].replace('\\n', '\n'), q_args[0]))
                break

        # if there's not an empty quote, add this quote on the end.
        else:
            bot.data[cmd.guild.id]['quotes'].append((q_args[0], q_args[1].lstrip()))
            bot.send_message(cmd.channel, "Added quote with ID {0}: \n{1} -{2}"
                             .format(len(bot.data[cmd.guild.id]['quotes']) - 1, q_args[1].replace('\\n', '\n'), q_args[0]))

        save_data()
        logging.info("Added a new quote.")


    # if "@quote remove <id>@"
    elif cmd.args[0].lower() == "remove":

        # Admin Check
        if not bot.is_admin(cmd.author):
            bot.send_message(cmd.author, "You must be an admin to use this command.")
            return

        # ID type-check and Arg count check
        try:
            cmd.args[1] = int(cmd.args[1])
        except TypeError:
            cmd.on_syntax_error(str(cmd.args[1]) + ' is not a valid quote ID.')
            return
        except IndexError:
            cmd.on_syntax_error("You must provide a quote ID to remove.")
            return

        # Range check, and check that the quote author in the system is not blank (a deleted quote)
        if cmd.args[1] < 0 \
                or cmd.args[1] >= len(bot.data[cmd.guild.id]['quotes']) \
                or bot.data[cmd.guild.id]['quotes'][cmd.args[1]][1] == '':
            bot.send_message(cmd.channel, "That quote ID is not valid. Use 'quote list' to find valid IDs.")
            return

        q = bot.data[cmd.guild.id]['quotes'][cmd.args[1]]
        bot.data[cmd.guild.id]['quotes'][cmd.args[1]] = ('', '')
        bot.send_message(cmd.channel, "Quote removed: {0}\n\t\t\t-{1}".format(q[1].replace('\\n', '\n'), q[0]))
        bot.save_data()
        logging.info("Quote removed.")

    # if "quote <unknown args>"
    else:
        cmd.on_syntax_error('Invalid sub-command.')

