from datetime import datetime
from Commands.CmdHelper import *
from Main.FileWriting import save_data


# set the birthday for someone, or
def cmd_birthday(cmd):
    logging.info("Command: birthday")

    # if not on a server, invalid usage.
    if cmd.server is None:
        SendMessage(cmd.channel, "This command can only be used on a server.")
        return

    # if no args, invalid usage.
    if len(cmd.args) == 0:
        cmd.OnSyntaxError('')
        return

    # create dict for server if it doesn't exist.
    if cmd.server.id not in link_bot.data:
        link_bot.data[cmd.server.id] = {}
    if 'birthdays' not in link_bot.data[cmd.server.id]:
        link_bot.data[cmd.server.id]['birthdays'] = {}

    # birthday set <person> <birthday>
    if cmd.args[0].lower() == "set":

        # check that there are at least 2 args.
        if len(cmd.args) < 3:
            cmd.OnSyntaxError('Setting a birthday requires a person and a month/day combination.')
            return

        # if specified that today is the birthday, set it.
        if cmd.args[2].lower() == "today":
            bday = datetime.now()
        # otherwise, we'll have to parse it out manually.
        else:

            # Try 09/02
            try:
                f = "%m/%d"
                bday = datetime.strptime(cmd.args[2], f)
            except ValueError:

                # Try 09-02
                try:
                    f = "%m-%d"
                    bday = datetime.strptime(cmd.args[2], f)
                except ValueError:

                    # Try Sep 02
                    try:
                        f = "%b %d"
                        bday = datetime.strptime(cmd.args[2].lower().capitalize() + " " + cmd.args[3], f)
                    except (ValueError, IndexError):

                        # Try September 02
                        try:
                            f = "%B %d"
                            bday = datetime.strptime(cmd.args[2].lower().capitalize() + " " + cmd.args[3], f)
                        except (ValueError, IndexError):

                            # Send error: Invalid format.
                            cmd.OnSyntaxError('To set a birthday, it must be in the '
                                            'format of TB 09/02, TB 09-02, TB Sep 02 or TB September 02.')
                            return

        # set the birthday for the server and person.
        link_bot.data[cmd.server.id]['birthdays'][cmd.args[1]] = bday.strftime("%m/%d")
        SendMessage(cmd.channel, "Set birthday of {} to {}.".format(cmd.args[1], bday.strftime("%B %d")))
        save_data()
        logging.info("Set birthday.")

    # birthday remove <person>
    elif cmd.args[0].lower() == "remove":

        # Not enough args check
        if len(cmd.args) < 2:
            SendMessage(cmd.author, OnSyntaxError(
                'birthday', "Specify a person whose birthday should be removed from the database."))
            return

        if cmd.args[1] not in link_bot.data[cmd.server.id]['birthdays']:
            SendMessage(cmd.channel, "{} doesn't have a registered birthday.".format(cmd.args[1]))
            return

        link_bot.data[cmd.server.id]['birthdays'].pop(cmd.args[1])
        SendMessage(cmd.channel, "{}'s birthday successfully removed.".format(cmd.args[1]))
        save_data()
        logging.info("Removed birthday.")

    # birthday list
    elif cmd.args[0].lower() == "list":
        today = datetime.now()
        bdays = []
        for p, b in link_bot.data[cmd.server.id]['birthdays'].items():
            bday = datetime.strptime(b, "%m/%d")
            if bday.month > today.month or (bday.month == today.month and bday.day >= today.day):
                bdays.append((p, datetime(today.year, bday.month, bday.day)))
            else:
                bdays.append((p, datetime(today.year + 1, bday.month, bday.day)))

        bdays.sort(key=lambda x: x[1])

        send_msg = ""
        for b in bdays:
            send_msg += b[0] + ": " + b[1].strftime("%B %d") + "\n"

        if send_msg == "":
            SendMessage(cmd.channel, "I don't know anyone's birthdays yet.")
        else:
            SendMessage(cmd.channel, send_msg)

    # birthday ...
    else:
        cmd.OnSyntaxError("Invalid subcommand.")

