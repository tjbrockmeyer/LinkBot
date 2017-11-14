import asyncio
from Commands.CmdHelper import *
from Main.Helper import FormatAsColumn, FormatAsLoLPlayerOutput
from RiotAPI import *


# write relavent info about the provided player's league of legends game
@disabled_command("Needs updates to follow Riot's API.")
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
    api_request = link_bot.riotClient.get_summoner(arg_summoner)

    # check that the summoner exists on the specified server
    if api_request.status_code != 200:
        if api_request.status_code == 404:
            SendMessage(cmd.channel, "{0} does not exist on the {1} server."
                        .format(arg_summoner, link_bot.riotClient.region))
        else:
            SendErrorMessage(link_bot.riotClient.get_status_code_string(api_request.status_code) +
                             "\n" + api_request.url)
            SendMessage(cmd.channel, "An error occurred. Aborting the lookup.")
        return
    summoner = Summoner(api_request.json[arg_summoner])

    # get summoner's game
    api_request = link_bot.riotClient.get_current_game(summoner.id)

    # check that the summoner is in a game
    if api_request.status_code != 200:
        if api_request.status_code == 404:
            SendMessage(cmd.channel, "{0} is not in a game."
                        .format(summoner.name))
        else:
            SendErrorMessage(link_bot.riotClient.get_status_code_string(api_request.status_code) +
                             "\n" + api_request.url)
            SendMessage(cmd.channel, "An error occurred. Aborting the lookup.")
        return
    playergame = api_request.json

    # begin organizing data
    SendMessage(cmd.channel, "Looking up {0}'s game on the {1} server..."
                .format(summoner.name, link_bot.riotClient.region.upper()))
    asyncio.run_coroutine_threadsafe(link_bot.discordClient.send_typing(cmd.channel), cmd.loop)

    # lists of the players and the string to be printed as output
    blueteam = []
    redteam = []
    gamestring = ''

    # organize json into a list of InGameSummoners
    players = []
    for participant in playergame['participants']:
        player = InGameSummoner()
        player.id = participant['summonerId']
        player.champ_id = participant['championId']
        player.team = participant['teamId']
        players.append(player)
    player_ids = ''

    # add player's id to the list of players to look up
    for player in players:
        player_ids += str(player.id)
        player_ids += ','

    # remove the extra ','.
    player_ids = player_ids[:-1]

    # get each player's summoner info
    api_request = link_bot.riotClient.get_summoner_by_id(player_ids)
    if api_request.status_code != 200:
        SendErrorMessage(link_bot.riotClient.get_status_code_string(api_request.status_code) +
                         "\n" + api_request.url)
        SendMessage(cmd.channel, "An error occurred. Aborting the lookup.")
        return
    player_list = api_request.json

    # get each summoner's info
    for player in players:
        if str(player.id) in player_list:
            player.summoner = Summoner(player_list[str(player.id)])

    # get full list of champions in league of legends
    api_request = link_bot.riotClient.get_all_champion_data(True)
    if api_request.status_code != 200:
        SendErrorMessage(link_bot.riotClient.get_status_code_string(api_request.status_code) +
                         "\n" + api_request.url)
        SendMessage(cmd.channel, "An error occurred. Aborting the lookup.")
        return
    full_champ_list = api_request.json['data']

    # organize player info
    for player in players:

        # get player champion information
        player.champion = Champion(full_champ_list[str(player.champ_id)])

        # get player champion ranked stats
        acs = link_bot.riotClient.get_champion_stats(player.id)
        if api_request.status_code != 200:
            if api_request.status_code == 404:
                logging.info("{0} has no ranked champion stats.".format(player.summoner.name))
            else:
                SendErrorMessage(link_bot.riotClient.get_status_code_string(api_request.status_code) +
                                 "\n" + api_request.url)
            player.games_champ = 0
            player.kda_champ = 0
            player.win_rate_champ = 0
            continue

        # find player's current champion in their all champ stats list.
        if 'champions' in acs.json:
            all_champ_stats = acs.json['champions']
            kills = 0
            assists = 0
            deaths = 0
            for champ in all_champ_stats:

                # add to total kills, assists and deaths
                kills += champ['stats']['totalChampionKills']
                assists += champ['stats']['totalAssists']
                deaths += champ['stats']['totalDeathsPerSession']

                if champ['id'] == player.champ_id:

                    # get total champion games and win rate
                    player.games_champ = champ['stats']['totalSessionsPlayed']
                    player.win_rate_champ = format(champ['stats']['totalSessionsWon'] /
                                                   player.games_champ * 100, '.0f')

                    # get champion kda
                    if champ['stats']['totalDeathsPerSession'] != 0:
                        player.kda_champ = format((champ['stats']['totalChampionKills'] +
                                                  champ['stats']['totalAssists']) /
                                                  champ['stats']['totalDeathsPerSession'], '.2f')

                    # perfect champion kda
                    else:
                        player.kda_champ = "Inf"

                    # stop searching the champ list.
                    break
            else:
                # player's current champ was not found
                logging.info("{0} has no ranked games on their current champion.".format(player.summoner.name))
                player.games_champ = 0
                player.kda_champ = 0
                player.win_rate_champ = 0

            # calculate kda
            if deaths != 0:
                player.kda = format((kills + assists) / deaths, '.2f')
            else:
                player.kda = "Inf"

        else:
            # player has no champions played in ranked
            logging.info("{0} has no ranked games on any champion.".format(player.summoner.name))
            player.games_champ = 0
            player.kda_champ = 0
            player.win_rate_champ = 0

    # get each player's ranked league info
    api_request = link_bot.riotClient.get_player_league_entry(player_ids)
    if api_request.status_code != 200:
        SendErrorMessage(link_bot.riotClient.get_status_code_string(api_request.status_code) +
                         "\n" + api_request.url)
        SendMessage(cmd.channel, "An error occurred. Aborting the lookup.")
        return
    league_info_list = api_request.json

    for player in players:

        # get summoner rank info
        if str(player.id) in league_info_list:
            rank = league_info_list[str(player.id)][0]
            player.rank = rank['tier'] + ' ' + rank['entries'][0]['division']
            rank = league_info_list[str(player.id)][0]['entries'][0]
            player.lp = str(rank['leaguePoints']) + 'LP'

            # calculate total games
            if 'wins' in rank:
                wins = rank['wins']
            else:
                wins = 0
            if 'losses' in rank:
                losses = rank['losses']
            else:
                losses = 0

            # get series info
            if 'miniSeries' in rank:
                player.series = rank['miniSeries']['progress'].replace('N', '-')

            # calculate win rate
            player.games = wins + losses
            if player.games != 0:
                player.win_rate = format(wins / player.games * 100, '.0f')
            else:
                player.win_rate = 0

        # if the summoner's id is not included in the league information, assume that they have no rank.
        else:
            player.rank = 'UNRANKED'

        # divide the players into their teams
        if player.team == 100:
            blueteam.append(player)
        else:
            redteam.append(player)

    # begin formatting output
    gamestring += '```League of Legends Game for {0}:\n' \
                  '{1} {2} on {3}\n\n'.format(summoner.name,
                                              GAME_MODES[playergame['gameMode']],
                                              QUEUE_TYPES[playergame['gameQueueConfigId']]['idealized'],
                                              MAPS[playergame['mapId']]) \
                  + FormatAsColumn(' ', 58) \
                  + FormatAsColumn('|   Champion   | |', 17) \
                  + FormatAsColumn(' In Queue | |Total|', 16)\
        + '\n' \
                  + FormatAsColumn('Summoner Name', 17) \
                  + FormatAsColumn('Rank', 27) \
                  + FormatAsColumn('Champion', 15) \
                  + FormatAsColumn('Games', 6) \
                  + FormatAsColumn('Win%', 5) \
                  + FormatAsColumn('KDA', 6) \
                  + FormatAsColumn('Games', 6) \
                  + FormatAsColumn('Win%', 8) \
                  + FormatAsColumn('KDA', 5)\
        + '\n\nBLUE TEAM (Bottom Left):\n\n'
    for player in blueteam:
        gamestring += FormatAsLoLPlayerOutput(player)
    gamestring += '\nRED TEAM (Top Right):\n\n'
    for player in redteam:
        gamestring += FormatAsLoLPlayerOutput(player)
    gamestring += '```'
    SendMessage(cmd.channel, gamestring)
    logging.info("Sent League of Legends game info.")

