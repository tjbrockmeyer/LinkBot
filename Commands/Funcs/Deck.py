from Commands.CmdHelper import *
from random import Random


@restrict(SERVER_ONLY)
@require_args(1)
@command
def deck(cmd: Command):
    session_obj = bot.session_objects[cmd.guild]
    subcmd = cmd.args[0].lower()
    cmd.shiftargs()
    if subcmd == "setup":
        deck_setup(cmd, session_obj)
    elif subcmd == "draw":
        deck_draw(cmd, session_obj)
    elif subcmd == "status":
        deck_status(cmd, session_obj)
    elif subcmd == "shuffle":
        deck_shuffle(cmd, session_obj)
    else:
        cmd.on_syntax_error(cmd.args[0] + " is not a valid 'deck' sub-command.")


@require_args(1)
def deck_setup(cmd, session_obj):
    arg = cmd.args[0]
    if arg == "none" or arg == "clear":
        session_obj.deck = []
        session_obj.original_deck = []
        bot.send_message(cmd.channel, "Deck cleared.")
        logging.info("Clearing the deck.")
    elif arg == "add":
        for x in cmd.args:
            session_obj.deck.append(x)
            if x not in session_obj.original_deck:
                session_obj.original_deck.append(x)
        bot.send_message(cmd.channel, "Added card(s) to the deck.")
        logging.info("Added card(s) to the deck.")
    elif arg == "preset":
        # TODO: Create preset decks to use.

        logging.info("Setting preset")
    elif arg == "custom":
        session_obj.original_deck = cmd.args
        session_obj.deck = cmd.args
        bot.send_message(cmd.channel, "Created custom deck.")
        logging.info("Created custom deck.")
    else:
        cmd.on_syntax_error(arg + " is not a valid setup.")


def deck_status(cmd, session_obj):
    bot.send_message(
        cmd.channel,
        "The original deck had {} cards in it. "
        "The deck is down to {} cards right now."
        .format(len(session_obj.original_deck), len(session_obj.deck)))


def deck_draw(cmd, session_obj):
    if len(session_obj.deck) == 0:
        bot.send_message(cmd.channel, "There are no cards in the deck to draw. Consider setting up a new one.")
        return

    card = session_obj.deck.pop()
    if len(cmd.args) != 0 and cmd.args[1].lower() == "public":
        bot.send_message(cmd.channel, "You drew " + str(card) + ".")
    else:
        bot.send_message(cmd.author, "You drew " + str(card) + ".")
        bot.send_message(cmd.channel, "Here you go.")


def deck_shuffle(cmd, session_obj):
    rand = Random()
    for i in range(len(session_obj.deck)):
        j = rand.randrange(0, len(session_obj.deck))
        temp = session_obj.deck[i]
        session_obj.deck[i] = session_obj.deck[j]
        session_obj.deck[j] = temp
    bot.send_message(cmd.channel, "Deck shuffled.")
