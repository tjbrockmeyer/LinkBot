from Commands.CmdHelper import *
from Main.Funcs import format_as_column
from RiotAPI import *


@command(
    ["{c} <player> [region]"],
    "Sends info to the channel about `summoner`'s current League of Legends game.",
    [
        ("{c} The Booty Toucher",
         "Looks up and posts information in the chat about The Booty Toucher's league of legends game."),
        ("{c} thebootytoucher", "Summoner names are not case sensitive, nor are the spaces mandatory."),
        ("{c} thebootytoucher, kr",
         "Will look on the Korean servers for the player's game. You can specify any region, but you'll need to know the region ID yourself.")
    ]
)
@restrict(0)
@require_args(1)
async def lolgame(cmd: Command):
    args = cmd.argstr.split(',')

    # get args
    arg_summoner = args[0]
    arg_region = ''
    for a in range(0, len(args)):
        args[a] = args[a].strip()
    if len(args) > 1:
        arg_region = args[1]

    # set region
    if arg_region is not '':
        if arg_region in PLATFORMS:
            bot.riotClient.region = arg_region
    else:
        bot.riotClient.region = 'na'

    # get summoner
    try:
        summoner = bot.riotClient.get_summoner(arg_summoner)
    except RiotAPIError as e:
        if e.status_code == 404:
            bot.send_message(cmd.channel, "{} does not exist on the {} server.".format(arg_summoner, bot.riotClient.region))
        else:
            _notify_of_unknown_error(cmd.channel, e)
        return

    # get summoner's game
    try:
        game = bot.riotClient.get_active_game(summoner.id)
    except RiotAPIError as e:
        if e.status_code == 404:
            bot.send_message(cmd.channel, "{} is not in a game.".format(summoner.name))
        else:
            _notify_of_unknown_error(cmd.channel, e)
        return

    # begin organizing data
    bot.send_message(cmd.channel, "Looking up {}'s game on the {} server...".format(summoner.name, bot.riotClient.region.upper()))
    await asyncio.sleep(0.5)

    async with cmd.channel.typing():
        # get full list of champions in league of legends
        try:
            champions = bot.riotClient.get_champion_static_all()
        except RiotAPIError as e:
            _notify_of_unknown_error(cmd.channel, e)
            return

        # list for both teams and the output string.
        blueteam = []
        redteam = []

        for player in game.participants:
            p = PlayerOutput(player.name, champions[player.champion_id])

            if player.team_id == 100:
                redteam.append(p)
            else:
                blueteam.append(p)

            if game.ranked_queue is not None:
                try:
                    for entry in bot.riotClient.get_league_entries(player.summoner_id):
                        if entry.queue_type == game.ranked_queue:
                            p.rank = entry.tier + ' ' + entry.rank
                            p.streak = entry.hot_streak
                            if entry.series is not None:
                                p.series = entry.series.progress.replace('N', '-')
                            p.lp = entry.points
                            p.games = entry.wins + entry.losses
                            p.winrate = "{:0.2f}".format(entry.wins / float(p.games) if p.games != 0 else entry.wins)
                except RiotAPIError as e:
                    _notify_of_unknown_error(cmd.channel, e)

        # begin formatting output
        gamestring = '```League of Legends Game for {}:\n'.format(summoner.name) + \
                game.full_game_type + \
                '\n\nBLUE TEAM (Bottom Left):\n' + \
                     format_as_column('Summoner Name', 17, alignment=1) + \
                     format_as_column('Rank', 16, alignment=0) + \
                     format_as_column('LP', 6, alignment=-1) + \
                     format_as_column('Series', 6, alignment=-1) + \
                     format_as_column('Champion', 15, alignment=0) + \
                     format_as_column('Games', 6, alignment=0) + \
                     format_as_column('Win%', 8, alignment=0) + '\n'
        for p in blueteam:
            gamestring += _format_as_lolplayer_output(p)
        gamestring += '\nRED TEAM (Top Right):\n' + \
                      format_as_column('Summoner Name', 17, alignment=1) + \
                      format_as_column('Rank', 16, alignment=0) + \
                      format_as_column('LP', 6, alignment=-1) + \
                      format_as_column('Series', 6, alignment=-1) + \
                      format_as_column('Champion', 15, alignment=0) + \
                      format_as_column('Games', 6, alignment=0) + \
                      format_as_column('Win%', 8, alignment=0) + '\n'
        for p in redteam:
            gamestring += _format_as_lolplayer_output(p)
        gamestring += '```'

        bot.send_message(cmd.channel, gamestring)


class PlayerOutput:
    def __init__(self, name, champion):
        self.name = name
        self.champion = champion
        self.rank = 'UNRANKED'
        self.lp = ''
        self.series = ''
        self.streak = '-'
        self.games = '-'
        self.winrate = '-'


def _format_as_lolplayer_output(p):
    """
    Formats a player's in-game information into columns for outputting in monospace.

    :param p: The player whose output should be formatted.
    :type p: PlayerOutput
    :return: A string with the formatting applied.
    :rtype: str
    """
    string = format_as_column(p.name, 17, alignment=1) \
             + ' ' \
             + format_as_column(p.rank, 15, alignment=-1) \
             + format_as_column(str(p.lp), 6, alignment=-1) \
             + format_as_column(p.series, 6, alignment=0) \
             + format_as_column(p.champion.name, 15, alignment=0) \
             + format_as_column(str(p.games), 6, alignment=0) \
             + format_as_column(str(p.winrate) + '%', 8, alignment=0) \
             + '\n'
    return string


def _notify_of_unknown_error(channel, error):
    bot.send_error_message('Error code: ' + str(error.status_code) + '\n' + error.url + '\n' + error.message)
    bot.send_message(channel, "An error occurred. Aborting the lookup.")

