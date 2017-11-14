from Commands.CmdHelper import *
from random import Random

def cmd_deck(cmd: Command):
    logging.info("Command: deck")
    if len(cmd.args) == 0:
        cmd.OnSyntaxError('')
        return

    if cmd.server is None:
        SendMessage(cmd.channel, "This command may only be used on a server.")
        return

    server_obj = link_bot.server_object[cmd.server]

    if cmd.args[0].lower() == "setup":
        if len(cmd.args) < 2:
            cmd.OnSyntaxError("You must specify how to setup the deck.")
            return

        if cmd.args[1].lower() == "none" or cmd.args[1].lower() == "clear":
            server_obj.deck = []
            server_obj.original_deck = []
            SendMessage(cmd.channel, "Deck cleared.")
            logging.info("Clearing the deck.")
        elif cmd.args[1].lower() == "add":
            for x in cmd.args[2:]:
                server_obj.deck.append(x)
                if x not in server_obj.original_deck:
                    server_obj.original_deck.append(x)
            SendMessage(cmd.channel, "Added card(s) to the deck.")
            logging.info("Added card(s) to the deck.")
        elif cmd.args[1].lower() == "preset":
            # TODO: Create preset decks to use.

            logging.info("Setting preset")
        elif cmd.args[1].lower() == "custom":
            server_obj.original_deck = cmd.args[2:]
            server_obj.deck = cmd.args[2:]
            SendMessage(cmd.channel, "Created custom deck.")
            logging.info("Created custom deck.")
        else:
            cmd.OnSyntaxError(cmd.args[1] + " is not a valid setup.")

    elif cmd.args[0].lower() == "draw":
        if len(server_obj.deck) == 0:
            SendMessage(cmd.channel, "There are no cards in the deck to draw. Consider setting up a new one.")
            return

        card = server_obj.deck.pop()
        if len(cmd.args) > 1 and cmd.args[1].lower() == "public":
            SendMessage(cmd.channel, "You drew " + str(card) + ".")
        else:
            SendMessage(cmd.author, "You drew " + str(card) + ".")
            SendMessage(cmd.channel, "Here you go.")
        logging.info("Drew a card.")

    elif cmd.args[0].lower() == "status":
        SendMessage(
            cmd.channel,
            "The original deck had {} cards in it. "
            "The deck is down to {} cards right now."
            .format(len(server_obj.original_deck), len(server_obj.deck))
        )
        logging.info("Sent deck status.")

    elif cmd.args[0].lower() == "shuffle":
        rand = Random()
        for i in range(len(server_obj.deck)):
            j = rand.randrange(0, len(server_obj.deck))
            temp = server_obj.deck[i]
            server_obj.deck[i] = server_obj.deck[j]
            server_obj.deck[j] = temp
        SendMessage(cmd.channel, "Deck shuffled.")
        logging.info("Deck shuffled.")

    else:
        cmd.OnSyntaxError(cmd.args[0] + " is not a valid 'deck' sub-command.")
