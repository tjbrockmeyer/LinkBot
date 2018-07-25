from Commands.CmdHelper import *
from random import Random

def cmd_deck(cmd: Command):
    logging.info("Command: deck")
    if len(cmd.args) == 0:
        cmd.on_syntax_error('')
        return

    if cmd.guild is None:
        bot.send_message(cmd.channel, "This command may only be used on a server.")
        return

    session_obj = bot.session_object[cmd.guild]

    if cmd.args[0].lower() == "setup":
        if len(cmd.args) < 2:
            cmd.on_syntax_error("You must specify how to setup the deck.")
            return

        if cmd.args[1].lower() == "none" or cmd.args[1].lower() == "clear":
            session_obj.deck = []
            session_obj.original_deck = []
            bot.send_message(cmd.channel, "Deck cleared.")
            logging.info("Clearing the deck.")
        elif cmd.args[1].lower() == "add":
            for x in cmd.args[2:]:
                session_obj.deck.append(x)
                if x not in session_obj.original_deck:
                    session_obj.original_deck.append(x)
            bot.send_message(cmd.channel, "Added card(s) to the deck.")
            logging.info("Added card(s) to the deck.")
        elif cmd.args[1].lower() == "preset":
            # TODO: Create preset decks to use.

            logging.info("Setting preset")
        elif cmd.args[1].lower() == "custom":
            session_obj.original_deck = cmd.args[2:]
            session_obj.deck = cmd.args[2:]
            bot.send_message(cmd.channel, "Created custom deck.")
            logging.info("Created custom deck.")
        else:
            cmd.on_syntax_error(cmd.args[1] + " is not a valid setup.")

    elif cmd.args[0].lower() == "draw":
        if len(session_obj.deck) == 0:
            bot.send_message(cmd.channel, "There are no cards in the deck to draw. Consider setting up a new one.")
            return

        card = session_obj.deck.pop()
        if len(cmd.args) > 1 and cmd.args[1].lower() == "public":
            bot.send_message(cmd.channel, "You drew " + str(card) + ".")
        else:
            bot.send_message(cmd.author, "You drew " + str(card) + ".")
            bot.send_message(cmd.channel, "Here you go.")
        logging.info("Drew a card.")

    elif cmd.args[0].lower() == "status":
        bot.send_message(
            cmd.channel,
            "The original deck had {} cards in it. "
            "The deck is down to {} cards right now."
            .format(len(session_obj.original_deck), len(session_obj.deck))
        )
        logging.info("Sent deck status.")

    elif cmd.args[0].lower() == "shuffle":
        rand = Random()
        for i in range(len(session_obj.deck)):
            j = rand.randrange(0, len(session_obj.deck))
            temp = session_obj.deck[i]
            session_obj.deck[i] = session_obj.deck[j]
            session_obj.deck[j] = temp
        bot.send_message(cmd.channel, "Deck shuffled.")
        logging.info("Deck shuffled.")

    else:
        cmd.on_syntax_error(cmd.args[0] + " is not a valid 'deck' sub-command.")
