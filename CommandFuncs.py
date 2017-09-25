import random
import re
import time
from datetime import datetime

import RiotAPI_classes, RiotAPI_consts
from FileWriting import SUGGESTION_FILE, DATA_FOLDER
from FileWriting import update_config, save_admins, save_quotes, save_birthdays
from Helper import *


def disabled_command(reason=""):
    """Decorator used to disable usage of a function."""
    def decorator(func):
        def wrapper(cmd):
            if reason != "":
                SendMessage(cmd.channel, "This command is currently disabled. Reason: " + reason)
            else:
                SendMessage(cmd.channel, "This command is currently disabled.")
        return wrapper
    return decorator


# write a particular help panel to the chat.
def cmd_help(cmd):
    logging.info('Command: help   Sending to {0}.'.format(cmd.author))

    # Prevents Circular dependency.
    from Command import Command, COMMANDS

    help_header = '\n' \
       "Argument syntax:  `<mandatory> [optional]`\n" \
       "Command prefix: '{prefix}'\n"\
       "Use `{help_syntax}` to get more info on a particular command, for example: 'help quote'\n\n"

    help_generator = ("\n-" + x[1]['syntax'] for x in Command.EnumerateCommands_abc())

    # if just "help"
    if len(cmd.args) == 0:

        # Get command syntax list
        send = ''
        for x in help_generator:
            send += x

        # Send to command author
        SendMessage(cmd.author, help_header.format(
            prefix=link_bot.prefix, help_syntax=Command.GetCommandInfo('help')['syntax']) + send)
        logging.info("Help sent.")
    else:
        # get optional arguments. If first arg is 'here', set command arg as arg[1]
        command = cmd.args[1].lower() if len(cmd.args) > 1 and cmd.args[0] == 'here' else cmd.args[0].lower()

        # help here [command]
        if cmd.args[0] == 'here':
            if len(cmd.args) == 1:

                # Get command syntax list
                send = ''
                for x in help_generator:
                    send += x

                # Send to channel.
                SendMessage(cmd.channel, help_header.format(
                    prefix=link_bot.prefix, help_syntax=Command.GetCommandInfo('help')['syntax']) + send)
                logging.info('Help sent.')

            elif command in COMMANDS:
                SendMessage(cmd.channel, Command.GetHelp(command))
                logging.info('Help sent.')
            else:
                cmd.OnSyntaxError(command + ' is not a valid command.')

        # help [command]
        else:
            if command in COMMANDS:
                SendMessage(cmd.author, Command.GetHelp(command))
                logging.info('Help sent.')
            else:
                cmd.OnSyntaxError(command + ' is not a valid command.')


# move all members in a particular voice chat to a different one
def cmd_migrate(cmd):
    logging.info("Command: migrate")

    # On Server check.
    if cmd.server is None:
        SendMessage(cmd.channel, "You can only use this command on a server.")
        return

    # Enough args check.
    if len(cmd.args) < 2:
        cmd.OnSyntaxError('Provide two voice channels as arguments.')
        return

    cmd.args = cmd.argstr.split(',')
    channels = []
    for c in cmd.args:
        channels.append(c.strip())

    channel1 = None
    channel2 = None

    # find the two channels.
    for channel in cmd.server.channels:
        if channel.type == discord.ChannelType.voice:
            if channel.name.lower() == channels[0].lower():
                channel1 = channel
            elif channel.name.lower() == channels[1].lower():
                channel2 = channel
            # once they are both found, break the loop.
            if channel1 is not None and channel2 is not None:
                break

    # Report that the loop did not break.
    else:
        if channel1 is None and channel2 is None:
            cmd.OnSyntaxError("Neither '{}' nor '{}' are channels in this server.".format(*channels))
        elif channel1 is None:
            cmd.OnSyntaxError(channels[0] + " is not a channel in this server.")
        elif channel2 is None:
            cmd.OnSyntaxError(channels[1] + " is not a channel in this server.")
        return

    # move each member from the first channel to the second channel.
    for member in channel.voice_members:
        asyncio.run_coroutine_threadsafe(link_bot.discordClient.move_member(member, channel2), cmd.loop)
    SendMessage(cmd.channel, 'Members in {0} have been migrated to {1}.'.format(channel1.name, channel2.name))
    time.sleep(3)


# get, list, add or remove quotes from a server.
def cmd_quote(cmd):
    logging.info('Command: quote')

    # if not on a server, invalid usage.
    if cmd.server is None:
        SendMessage(cmd.channel, "This command can only be used on a server.")
        return

    # if no args, invalid usage.
    if len(cmd.args) == 0:
        cmd.OnSyntaxError('')
        return

    # if there have not been any registered quotes yet, create the list.
    if not cmd.server.id in link_bot.quotes.keys():
        link_bot.quotes[cmd.server.id] = list()

    # if "quote <id>"
    if cmd.args[0].isdigit():
        qid = int(cmd.args[0])

        # check that quote id is within bounds
        if 0 <= qid < len(link_bot.quotes[cmd.server.id]):
            q = link_bot.quotes[cmd.server.id][qid]
            if q[1] != '':
                SendMessage(cmd.channel, '{0}\n\t\t\t-{1}'.format(q[1].replace('\\n', '\n'), q[0]))
                logging.info("Quote sent by ID.")
            else:
                cmd.OnSyntaxError(str(qid) + ' is not a valid quote ID.')
        else:
            cmd.OnSyntaxError(str(qid) + ' is not a valid quote ID.')

    # if "quote random [author]"
    elif cmd.args[0].lower() == "random":

        authorArg = cmd.args[1] if len(cmd.args) > 1 else ''

        # compile a list of quotes by the author, or all quotes if not specified.
        quoteChoices = list()
        for q in link_bot.quotes[cmd.server.id]:
            # if we are looking to get a random quote from any author, or the quote's author is the one we're looking for...
            if q[1] != '' and (authorArg == '' or authorArg == q[0].lower()):
                quoteChoices.append(q)

        # if we dont have any quotes after going through all of them...
        if len(quoteChoices) == 0:
            if authorArg != '':
                SendMessage(cmd.channel, "I don't know any quotes from {0}.".format(cmd.args[1]))
            else:
                SendMessage(cmd.channel, "I don't know any quotes yet.")
            return

        # seed the random number generator and return a random quote from our choices.
        random.seed()
        q = quoteChoices[random.randrange(0, len(quoteChoices))]
        SendMessage(cmd.channel, "{0}\n\t\t\t-{1}".format(q[1].replace('\\n', '\n'), q[0]))
        logging.info("Sent a random quote.")

    # if "quote list [author]"
    elif cmd.args[0].lower() == "list":

        authorArg = cmd.args[1] if len(cmd.args) > 1 else ''

        i = 0
        quoteList = ''
        for q in link_bot.quotes[cmd.server.id]:
            if q[1] != '' and (authorArg == '' or authorArg == q[0].lower()):
                quoteList += "`{0}`: {1}   -{2}\n".format(i, q[1], q[0])
            i += 1

        # if no quotes were found for the author...
        if quoteList == '':
            if authorArg != '':
                SendMessage(cmd.channel, "I don't know any quotes from {0}".format(cmd.args[1]))
            else:
                SendMessage(cmd.channel, "I don't know any quotes yet.")
            return

        # if quotes were found for the author/on the server
        if authorArg == '':
            SendMessage(cmd.channel, "Quotes from this server:\n{0}".format(quoteList.replace('\\n', '\n')))
        else:
            SendMessage(cmd.channel, "Quotes from {0}:\n{1}".format(cmd.args[1], quoteList.replace('\\n', '\n')))
        logging.info("Sent list of quotes.")

    # if "quote add <quote -author>"
    elif cmd.args[0].lower() == "add":

        # Admin check
        if not IsAdmin(cmd.author):
            SendMessage(cmd.author, "You must be an admin to use this command.")
            return

        q_args = cmd.argstr[len('add'):].lstrip()
        match = re.search('( -\w)', q_args)

        # Author of Quote check
        if match is None:
            cmd.OnSyntaxError('To add a quote, include a quote followed by -Author\'s Name.')
            return

        # q_args[0] = author, q_args[1] = quote
        q_args = (q_args[match.start() + 2:], q_args[:match.start()].replace('\n', '\\n'))
        print(q_args)

        # check to see if there's a missing quote. If so, replace it with the new quote.
        for i in range(0, len(link_bot.quotes[cmd.server.id])):
            if link_bot.quotes[cmd.server.id][i][1] == '':
                link_bot.quotes[cmd.server.id][i] = (q_args[0], q_args[1].lstrip())
                SendMessage(cmd.channel, "Added quote with ID {0}: \n{1} -{2}"
                            .format(i, q_args[1].replace('\\n', '\n'), q_args[0]))
                break

        # if there's not an empty quote, add this quote on the end.
        else:
            link_bot.quotes[cmd.server.id].append((q_args[0], q_args[1].lstrip()))
            SendMessage(cmd.channel, "Added quote with ID {0}: \n{1} -{2}"
                        .format(len(link_bot.quotes[cmd.server.id]) - 1, q_args[1].replace('\\n', '\n'), q_args[0]))

        save_quotes()
        logging.info("Added a new quote.")

    # if "@quote remove <id>@"
    elif cmd.args[0].lower() == "remove":

        # Admin Check
        if not IsAdmin(cmd.author):
            SendMessage(cmd.author, "You must be an admin to use this command.")
            return

        # ID type-check and Arg count check
        try:
            cmd.args[1] = int(cmd.args[1])
        except TypeError:
            cmd.OnSyntaxError(str(cmd.args[1]) + ' is not a valid quote ID.')
            return
        except IndexError:
            cmd.OnSyntaxError("You must provide a quote ID to remove.")
            return

        # Range check, and check that the quote author in the system is not blank (a deleted quote)
        if cmd.args[1] < 0 \
                or cmd.args[1] >= len(link_bot.quotes[cmd.server.id]) \
                or link_bot.quotes[cmd.server.id][cmd.args[1]][1] == '':
            SendMessage(cmd.channel, "That quote ID is not valid. Use 'quote list' to find valid IDs.")
            return

        q = link_bot.quotes[cmd.server.id][cmd.args[1]]
        link_bot.quotes[cmd.server.id][cmd.args[1]] = ('', '')
        SendMessage(cmd.channel, "Quote removed: {0}\n\t\t\t-{1}".format(q[1].replace('\\n', '\n'), q[0]))
        save_quotes()
        logging.info("Quote removed.")

    # if "quote <unknown args>"
    else:
        cmd.OnSyntaxError('Invalid sub-command.')


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
    if cmd.server.id not in link_bot.birthdays:
        link_bot.birthdays[cmd.server.id] = dict()

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
        link_bot.birthdays[cmd.server.id][cmd.args[1]] = bday
        SendMessage(cmd.channel, "Set birthday of {} to {}.".format(cmd.args[1], bday.strftime("%B %d")))
        save_birthdays()
        logging.info("Set birthday.")

    # birthday remove <person>
    elif cmd.args[0].lower() == "remove":

        # Not enough args check
        if len(cmd.args) < 2:
            SendMessage(cmd.author, OnSyntaxError(
                'birthday', "Specify a person whose birthday should be removed from the database."))
            return

        if cmd.args[1] not in link_bot.birthdays[cmd.server.id]:
            SendMessage(cmd.channel, "{} doesn't have a registered birthday.".format(cmd.args[1]))
            return

        link_bot.birthdays[cmd.server.id].pop(cmd.args[1])
        SendMessage(cmd.channel, "{}'s birthday successfully removed.".format(cmd.args[1]))
        save_birthdays()
        logging.info("Removed birthday.")

    # birthday list
    elif cmd.args[0].lower() == "list":
        send_msg = ""
        for person, bday in link_bot.birthdays[cmd.server.id].items():
            send_msg += person + ": " + bday.strftime("%B %d") + "\n"

        if send_msg == "":
            SendMessage(cmd.channel, "I don't know anyone's birthdays yet.")
        else:
            SendMessage(cmd.channel, send_msg)

    # birthday ...
    else:
        cmd.OnSyntaxError("Invalid subcommand.")


# write relavent info about the provided player's league of legends game
@disabled_command("Needs updates to follow Riot's API.")
def cmd_lolgame(cmd):
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
        if arg_region in RiotAPI_consts.PLATFORMS:
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
    summoner = RiotAPI_classes.Summoner(api_request.json[arg_summoner])

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
        player = RiotAPI_classes.InGameSummoner()
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
            player.summoner = RiotAPI_classes.Summoner(player_list[str(player.id)])

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
        player.champion = RiotAPI_classes.Champion(full_champ_list[str(player.champ_id)])

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
                                              RiotAPI_consts.GAME_MODES[playergame['gameMode']],
                                              RiotAPI_consts.QUEUE_TYPES[playergame['gameQueueConfigId']]['idealized'],
                                              RiotAPI_consts.MAPS[playergame['mapId']]) \
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


# link the first youtube video found using the provided query
def cmd_youtube(cmd):
    logging.info('Command: youtube')

    # check for missing args
    if len(cmd.args) == 0:
        cmd.OnSyntaxError('You must provide a query to search for.')
        return

    # get the search results
    api_request = link_bot.googleClient.search_for_video(cmd.argstr, 1)

    # check for bad status code
    if api_request.status_code != 200:
        SendErrorMessage("Google API Error: \n" + api_request.url)
        SendMessage(cmd.channel, "An unknown error occurred. The quota limit may have been reached.")
        return

    # send link to first search result
    logging.info(api_request.url)
    if len(api_request.json['items']) == 0:
        SendMessage(cmd.channel, "No results were found.")
    else:
        SendMessage(cmd.channel, "https://youtube.com/watch?v=" + api_request.json['items'][0]['id']['videoId'])
        logging.info("Sent YouTube video link.")


# link the first image found using the provided query
def cmd_image(cmd):
    logging.info('Command: image')

    # check for missing args
    if len(cmd.args) == 0:
        cmd.OnSyntaxError('You must provide a query to search for.')
        return

    # get the search results
    api_request = link_bot.googleClient.google_image_search(cmd.argstr)

    # check for bad status code
    if api_request.status_code != 200:
        SendErrorMessage("Google API Error: \n" + api_request.url)
        SendMessage(cmd.channel, "An error occurred. The quota limit may have been reached.")
        return

    # send link to first search result
    if 'items' in api_request.json:
        SendMessage(cmd.channel, api_request.json['items'][0]['link'])
    else:
        SendMessage(cmd.channel, "No results were found.")
    logging.info("Sent Google image link.")


# play something in voice chat
@disabled_command("Not currently implemented")
def cmd_play(cmd):
    if cmd.server is None:
        SendMessage(cmd.channel, "This command may only be used in a server.")
        return

    voice = cmd.author.voice
    if voice.voice_channel is None:
        SendMessage(cmd.channel, "You need to be in a voice channel.")
        return

    inSameServer = False
    vc = None
    inSameChannel = False

    # find out if we're in the same server/channel as our inviter.
    for voiceClient in link_bot.discordClient.voice_clients:
        if voiceClient.server == voice.voice_channel.server:
            inSameServer = True
            vc = voiceClient
        if voiceClient.channel == voice.voice_channel:
            inSameChannel = True

    # join the voice channel, either by moving from the current one, or by creating a new voice client.
    if not inSameChannel:
        if inSameServer:
            vc.move_to(voice.voice_channel)
        else:
            link_bot.discordClient.join_voice_channel(voice.voice_channel)

    SendMessage(cmd.channel, "Kay, I joined.")


# suggest a new feature for the bot
def cmd_suggest(cmd):
    logging.info('Command: suggest')

    # Check args exist.
    if len(cmd.args) == 0:
        cmd.OnSyntaxError('You should probably suggest something.')
        return

    with link_bot.lock:
        suggestion_file = open(DATA_FOLDER + SUGGESTION_FILE, 'a')
        suggestion_file.write(cmd.argstr + '\n')
        suggestion_file.close()
    SendMessage(cmd.channel, 'Your suggestion has been noted!')
    logging.info('Suggestion has been noted.')


# enable/disable nsfw content in google searches
@disabled_command("Not currently implemented.")
def cmd_nsfw(cmd):
    logging.info('Command: nsfw')
    if cmd.server is None:
        SendMessage(cmd.channel, "You can only use this command on a server.")
        return
    elif not IsAdmin(cmd.channel):
        SendMessage(cmd.channel, "You must be an admin to use this command.")
        return

    if cmd.args[0].lower() == 'on':
        link_bot.googleClient.set_safe_search(False)
        SendMessage(cmd.channel, "NSFW is now ON.")
        update_config()
    elif cmd.args[0].lower() == 'off':
        link_bot.googleClient.set_safe_search(True)
        link_bot.discordClient.send_message(cmd.channel, "NSFW is now OFF.")
        update_config()
    elif len(cmd.args) == 0:
        if link_bot.nsfw:
            SendMessage(cmd.channel, "NSFW is ON")
        else:
            SendMessage(cmd.channel, "NSFW is OFF")
    else:
        cmd.OnSyntaxError('Specify on or off.')
        return
    logging.info('NSFW has been set/queried.')


# add/remove/list admins for the server in which the cmd was received
def cmd_admin(cmd):
    logging.info('Command: admin')

    # Check for args
    if len(cmd.args) == 0:
        cmd.OnSyntaxError('')
        return

    # Check for using cmd on server.
    if cmd.server is None:
        SendMessage(cmd.channel, 'You can only use this command in a server.')
        return

    if cmd.server.id not in link_bot.admins.keys():
        link_bot.admins[cmd.server.id] = list()

    # if "admin list"
    if cmd.args[0].lower() == "list":

        # Check for existing admins
        if len(link_bot.admins[cmd.server.id]) == 0:
            SendMessage(cmd.channel, 'There are no admins on this server.')
            return

        # get the admin names from their IDs, save them to a string, then send it to the channel.
        admins = 'Admins: '
        needs_comma = False
        for member in cmd.server.members:
            if member.id in link_bot.admins[cmd.server.id]:
                if needs_comma:
                    admins += ', '
                admins += member.name
                needs_comma = True
        SendMessage(cmd.channel, admins)
        logging.info("Listed admins.")

    # if "admin add"
    elif cmd.args[0].lower() == "add":

        # Check that the sender is an admin
        if not IsAdmin(cmd.author):
            SendMessage(cmd.channel, "You must be an admin to use this command.")
            return

        # the output cmd at the end.
        msg = ''

        # if there is a member mention, add them as an admin.
        for member in cmd.message.mentions:
            if member.id in link_bot.admins[cmd.server.id]:
                msg += member.display_name + " is already an admin.\n"
            else:
                link_bot.admins[cmd.server.id].append(member.id)
                msg += "Added " + member.display_name + " as an admin.\n"

        # if there is a role mention, add all members with that role as an admin.
        for role in cmd.message.role_mentions:
            for member in cmd.server.members:
                if role in member.roles:
                    if member.id in link_bot.admins[cmd.server.id]:
                        msg += member.display_name + " is already an admin.\n"
                    else:
                        link_bot.admins[cmd.server.id].append(member.id)
                        msg += "Added " + member.display_name + " as an admin.\n"
        # output
        save_admins()
        SendMessage(cmd.channel, msg)
        logging.info("Added admins.")

    # if "admin remove"
    elif cmd.args[0].lower() == "remove":

        # Check that the sender is an admin.
        if not IsAdmin(cmd.author):
            SendMessage(cmd.channel, "You must be an admin to use this command.")
            return

        # the output message at the end.
        msg = ''

        # if there is a member mention, add them as an admin.
        for member in cmd.message.mentions:
            if member.id not in link_bot.admins[cmd.server.id]:
                msg += member.display_name + " is not an admin.\n"
            else:
                link_bot.admins[cmd.server.id].remove(member.id)
                msg += "Removed " + member.display_name + " from the admin list.\n"

        # if there is a role mention, add all members with that role as an admin.
        for role in cmd.message.role_mentions:
            for member in cmd.server.members:
                if role in member.roles:
                    if member.id not in link_bot.admins[cmd.server.id]:
                        msg += member.display_name + " is not an admin.\n"
                    else:
                        link_bot.admins[cmd.server.id].remove(member.id)
                        msg += "Removed " + member.display_name + " from the admin list.\n"
        # output
        save_admins()
        SendMessage(cmd.channel, msg)
        logging.info("Removed admins.")

    # if "admin ..."
    else:
        SendMessage(cmd.channel, '{0} is not a valid argument.'.format(cmd.args[0]))


# log the bot out
def cmd_logout(cmd):
    logging.info("Command: logout")
    link_bot.requestedStop = True  # prevent a restart
    if not IsOwner(cmd.author):
        SendMessage(cmd.channel, "You must be the bot's owner to use this command.")
        return

    # disable cmd reading
    link_bot.isStopping = True

    logging.info('Waiting for command threads to finish.')
    for thread in threading.enumerate():
        if thread.name.startswith('cmd') and thread.is_alive() and thread.name != 'cmd_logout':
            logging.info('Currently waiting on: ' + thread.name)
            thread.join()

    SendMessage(link_bot.owner, "Logging out.")
    link_bot.active = False