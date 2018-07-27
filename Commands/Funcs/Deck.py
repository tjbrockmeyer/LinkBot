
from Commands.CmdHelper import *
from random import Random


class Deck:
    def __init__(self):
        self.original_deck = []
        self.deck = []


decks = {}


@command(
    ["{c} status", "{c} setup preset <preset>", "{c} setup (clear|none)",
    "{c} setup add <list of cards>", "{c} setup custom <list of cards>",
    "{c} shuffle", "{c} draw [public]"],
    "Create a deck of cards and draw from it.",
    [
        ("{c} status", "Show how many cards were in the deck at the start, and how many there are now."),
        ("{c} setup preset standard", "Setup a deck with the standard 52 cards and no jokers."),
        ("{c} setup clear", "Throw away all cards in the deck."),
        ("{c} setup custom 1 2 3 4 a b c d", "Create a new deck with the cards being 1, 2, 3, 4, a, b, c, and d."),
        ("{c} setup add 5 6 e f", "Adds 5, 6, e, and f to the currently setup deck."),
        ("{c} shuffle", "Shuffle the current deck."),
        ("{c} draw public", "One card is removed from the deck and is shown in the channel chat."),
        ("{c} draw", "One card is removed from the deck, but public was not specified, so it is shown to you in a DM.")
    ]
)
@restrict(SERVER_ONLY)
@require_args(1)
async def deck(cmd: Command):
    session_obj = decks.get(cmd.guild)
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


@on_event('ready')
async def build_decks():
    global decks
    decks = {g: Deck() for g in bot.client.guilds}

