
from commands.cmd_utils import *
from random import Random


class Deck:
    def __init__(self):
        self.original_deck = []
        self.deck = []


decks = {}


@command(
    ["{c} status", "{c} setup <preset>", "{c} setup (clear|none)",
    "{c} setup add <list of cards>", "{c} setup custom <list of cards>",
    "{c} shuffle", "{c} draw"],
    "Create a deck of cards and draw from it.",
    [
        ("{c} status", "Show how many cards were in the deck at the start, and how many there are now."),
        ("{c} setup standard | {c} setup d6", "Setup a 52 card deck, or a 1-6 die."),
        ("{c} setup clear", "Throw away all cards in the deck."),
        ("{c} setup custom 1 2 3 4 a b c d", "Create a new deck with the cards being 1, 2, 3, 4, a, b, c, and d."),
        ("{c} setup add 5 6 e f", "Adds 5, 6, e, and f to the currently setup deck."),
        ("{c} shuffle", "Shuffle the current deck."),
        ("{c} draw", "One card is removed from the deck and it is shown to you in a DM.")
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
        raise CommandSyntaxError(cmd, "`{}` is not a valid subcommand.".format(subcmd))


@require_args(1)
async def deck_setup(cmd, deck_obj):
    arg = cmd.args[0]
    cmd.shiftargs()
    if arg == "none" or arg == "clear":
        deck_obj.deck = []
        deck_obj.original_deck = []
        await send_success(cmd.message)
    elif arg == "add":
        for x in cmd.args:
            deck_obj.deck.append(x)
            if x not in deck_obj.original_deck:
                deck_obj.original_deck.append(x)
        await send_success(cmd.message)
    elif arg == 'd6':
        deck_obj.original_deck = [i for i in range(1, 7)]
        deck_obj.deck = [i for i in deck_obj.original_deck]
        await send_success(cmd.message)
    elif arg == 'standard':
        deck_obj.original_deck = []
        for suit in ['Spades', 'Clubs', 'Hearts', 'Diamonds']:
            for val in ['Ace'] + [str(i) for i in range(2, 11)] + ['Jack', 'Queen', 'King']:
                deck_obj.original_deck.append("{} of {}".format(val, suit))
        deck_obj.original_deck = list(reversed(deck_obj.original_deck))
        deck_obj.deck = [i for i in deck_obj.original_deck]
        await send_success(cmd.message)
    elif arg == "custom":
        if len(cmd.args) == 0:
            raise CommandSyntaxError(cmd, "You must specify a list of cards to use in the deck.")
        deck_obj.original_deck = cmd.args
        deck_obj.deck = [i for i in cmd.args]
        await send_success(cmd.message)
    else:
        raise CommandSyntaxError(cmd, "`{}` is not a valid setup.".format(arg))


async def deck_status(cmd, deck_obj):
    await cmd.channel.send(
        "The original deck had {} cards in it.\n"
        "The deck is down to {} cards right now."
        .format(len(deck_obj.original_deck), len(deck_obj.deck)))


async def deck_draw(cmd, deck_obj):
    if len(deck_obj.deck) == 0:
        raise CommandError(cmd, "There are no cards in the deck to draw. Consider setting up a new one.")

    card = deck_obj.deck.pop()
    await cmd.author.send("You drew " + str(card) + ".")
    await send_success(cmd.message)


async def deck_shuffle(cmd, deck_obj):
    rand = Random()
    for i in range(len(deck_obj.deck)):
        j = rand.randrange(0, len(deck_obj.deck))
        temp = deck_obj.deck[i]
        deck_obj.deck[i] = deck_obj.deck[j]
        deck_obj.deck[j] = temp
    await send_success(cmd.message)


@on_event('ready')
async def build_decks():
    global decks
    decks = {g: Deck() for g in client.guilds}

