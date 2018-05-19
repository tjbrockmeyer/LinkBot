import asyncio
from Commands.CmdHelper import *
from Main.Helper import FormatAsColumn
from RiotAPI import *


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


def FormatAsLoLPlayerOutput(p):
    """
    Formats a player's in-game information into columns for outputting in monospace.

    :param p: The player whose output should be formatted.
    :type p: PlayerOutput
    :return: A string with the formatting applied.
    :rtype: str
    """
    string = FormatAsColumn(p.name, 17, alignment=1) \
             + ' ' \
             + FormatAsColumn(p.rank, 15, alignment=-1) \
             + FormatAsColumn(str(p.lp), 6, alignment=-1) \
             + FormatAsColumn(p.series, 6, alignment=0) \
             + FormatAsColumn(p.champion.name, 15, alignment=0) \
             + FormatAsColumn(str(p.games), 6, alignment=0) \
             + FormatAsColumn(str(p.winrate) + '%', 8, alignment=0) \
             + '\n'
    return string


def NotifyOfUnknownError(channel, error):
    SendErrorMessage('Error code: ' + str(error.status_code) + '\n' + error.url + '\n' + error.message)
    SendMessage(channel, "An error occurred. Aborting the lookup.")


# write relavent info about the provided player's league of legends game
@disabled_command("Need a project API key.")
def cmd_lolgame(cmd: Command):
    logging.info('Command: lolgame')

    # check for invalid argument count
    if len(cmd.args) < 1:
        cmd.OnSyntaxError('You must provide a summoner name.')
        return

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
            link_bot.riotClient.region = arg_region
    else:
        link_bot.riotClient.region = 'na'

    # get summoner
    try:
        summoner = link_bot.riotClient.get_summoner(arg_summoner)
    except RiotAPIError as e:
        if e.status_code == 404:
            SendMessage(cmd.channel, "{} does not exist on the {} server.".format(arg_summoner, link_bot.riotClient.region))
        else:
            NotifyOfUnknownError(cmd.channel, e)
        return

    # get summoner's game
    try:
        game = link_bot.riotClient.get_active_game(summoner.id)
    except RiotAPIError as e:
        if e.status_code == 404:
            SendMessage(cmd.channel, "{} is not in a game.".format(summoner.name))
        else:
            NotifyOfUnknownError(cmd.channel, e)
        return

    # begin organizing data
    SendMessage(cmd.channel, "Looking up {}'s game on the {} server...".format(summoner.name, link_bot.riotClient.region.upper()))
    asyncio.run_coroutine_threadsafe(link_bot.discordClient.send_typing(cmd.channel), cmd.loop)

    # get full list of champions in league of legends
    try:
        champions = link_bot.riotClient.get_champion_static_all()
    except RiotAPIError as e:
        NotifyOfUnknownError(cmd.channel, e)
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
                for entry in link_bot.riotClient.get_league_entries(player.summoner_id):
                    if entry.queue_type == game.ranked_queue:
                        p.rank = entry.tier + ' ' + entry.rank
                        p.streak = entry.hot_streak
                        if entry.series is not None:
                            p.series = entry.series.progress.replace('N', '-')
                        p.lp = entry.points
                        p.games = entry.wins + entry.losses
                        p.winrate = "{:0.2f}".format(entry.wins / float(p.games) if p.games != 0 else entry.wins)
            except RiotAPIError as e:
                NotifyOfUnknownError(cmd.channel, e)

    # begin formatting output
    gamestring = '```League of Legends Game for {}:\n'.format(summoner.name) + \
            game.full_game_type + \
            '\n\nBLUE TEAM (Bottom Left):\n' + \
            FormatAsColumn('Summoner Name', 17, alignment=1) + \
            FormatAsColumn('Rank', 16, alignment=0) + \
            FormatAsColumn('LP', 6, alignment=-1) + \
            FormatAsColumn('Series', 6, alignment=-1) + \
            FormatAsColumn('Champion', 15, alignment=0) + \
            FormatAsColumn('Games', 6, alignment=0) + \
            FormatAsColumn('Win%', 8, alignment=0) + '\n'
    for p in blueteam:
        gamestring += FormatAsLoLPlayerOutput(p)
    gamestring += '\nRED TEAM (Top Right):\n' + \
            FormatAsColumn('Summoner Name', 17, alignment=1) + \
            FormatAsColumn('Rank', 16, alignment=0) + \
            FormatAsColumn('LP', 6, alignment=-1) + \
            FormatAsColumn('Series', 6, alignment=-1) + \
            FormatAsColumn('Champion', 15, alignment=0) + \
            FormatAsColumn('Games', 6, alignment=0) + \
            FormatAsColumn('Win%', 8, alignment=0) + '\n'
    for p in redteam:
        gamestring += FormatAsLoLPlayerOutput(p)
    gamestring += '```'

    SendMessage(cmd.channel, gamestring)
    logging.info("Sent League of Legends game info.")

