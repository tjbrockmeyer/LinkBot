
from commands.cmd_utils import *
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
        await deck_setup(cmd, session_obj)
    elif subcmd == "draw":
        await deck_draw(cmd, session_obj)
    elif subcmd == "status":
        await deck_status(cmd, session_obj)
    elif subcmd == "shuffle":
        await deck_shuffle(cmd, session_obj)
    else:
        raise CommandSyntaxError(cmd, cmd.args[0] + " is not a valid 'deck' sub-command.")


@require_args(1)
async def deck_setup(cmd, session_obj):
    arg = cmd.args[0]
    if arg == "none" or arg == "clear":
        session_obj.deck = []
        session_obj.original_deck = []
        await send_success(cmd.message)
    elif arg == "add":
        for x in cmd.args:
            session_obj.deck.append(x)
            if x not in session_obj.original_deck:
                session_obj.original_deck.append(x)
        await send_success(cmd.message)
    elif arg == "preset":
        # TODO: Create preset decks to use.
        pass
    elif arg == "custom":
        session_obj.original_deck = cmd.args
        session_obj.deck = cmd.args
        await send_success(cmd.message)
    else:
        raise CommandSyntaxError(cmd, arg + " is not a valid setup.")


def deck_status(cmd, deck_obj):
    bot.send_message(
        cmd.channel,
        "The original deck had {} cards in it.\n"
        "The deck is down to {} cards right now."
        .format(len(deck_obj.original_deck), len(deck_obj.deck)))


async def deck_draw(cmd, session_obj):
    if len(session_obj.deck) == 0:
        raise CommandError(cmd, "There are no cards in the deck to draw. Consider setting up a new one.")

    card = session_obj.deck.pop()
    if len(cmd.args) != 0 and cmd.args[1].lower() == "public":
        await cmd.channel.send("You drew " + str(card) + ".")
    else:
        await cmd.author.send("You drew " + str(card) + ".")
        await send_success(cmd.message)


async def deck_shuffle(cmd, session_obj):
    rand = Random()
    for i in range(len(session_obj.deck)):
        j = rand.randrange(0, len(session_obj.deck))
        temp = session_obj.deck[i]
        session_obj.deck[i] = session_obj.deck[j]
        session_obj.deck[j] = temp
    await send_success(cmd.message)


@on_event('ready')
async def build_decks():
    global decks
    decks = {g: Deck() for g in bot.client.guilds}

