import RiotAPI_classes, RiotAPI_consts
import logging, asyncio, random, re
from LinkBot import send_message, send_error_message
from FileWriting import update_config, SUGGESTION_FILE, DATA_FOLDER, save_admins, save_quotes
from Helper import *


# write a particular help panel to the chat.
def help(message: discord.Message, argstr: str, loop):
    logging.info('Command: help   Sending to {0}.'.format(message.author))

    # if just "help"
    if len(argstr) == 0:
        send_message(message.author, HELP.format(link_bot.prefix))
    else:
        # get optional arguments. If first arg is 'here' or 'admin',
        args = argstr.split(' ')
        cmd = args[1] if len(args) > 1 and (args[0] == 'here' or args[0] == 'admin') else args[0]

        # modify cmd if necessary
        cmd = 'yt' if cmd == 'youtube' else cmd
        cmd = 'img' if cmd == 'image' else cmd
        cmd = 'logout' if cmd == 'logoff' else cmd

        # if "help here [command]"
        if args[0] == 'here':
            if len(args) == 1:
                send_message(message.channel, HELP.format(link_bot.prefix))
            elif cmd in COMMAND_HELP.keys():
                send_message(message.channel, COMMAND_HELP[cmd])
            else:
                send_message(message.channel, onSyntaxError('help', cmd + ' is not a valid command.'))

        # if "help [command]
        else:
            if cmd in COMMAND_HELP.keys():
                send_message(message.author, COMMAND_HELP[cmd])
            else:
                send_message(message.channel, onSyntaxError('help', cmd + ' is not a valid command.'))

    logging.info('Help has been sent.')


# move all members in a particular voice chat to a different one
def migrate(message: discord.Message, argstr: str, loop):
    logging.info("Command: migrate")
    channel1 = None
    channel2 = None
    if len(argstr) == 0:
        send_message(message.channel, onSyntaxError('migrate', 'Provide two voice channels as arguments.'))
    else:
        # get args, check for correct number, strip whitespace
        args = argstr.split(',')
        if len(args) < 2:
            send_message(message.channel, onSyntaxError('migrate', 'Provide two voice channels as arguments.'))
        else:
            args[0] = args[0].strip()
            args[1] = args[1].strip()
            # find the two channels.
            for channel in message.channel.server.channels:
                if channel.type == discord.ChannelType.voice:
                    if channel.name.lower() == args[0]:
                        channel1 = channel
                    elif channel.name.lower() == args[1]:
                        channel2 = channel
                    # once they are both found, break the loop.
                    if channel1 != None and channel2 != None:
                        break
            else:
                send_message(message.channel, onSyntaxError('migrate', "One or both of the channels provided do not exist. Check your spelling."))
                return
            # move each member from the first channel to the second channel.
            for member in channel.voice_members:
                asyncio.run_coroutine_threadsafe(client.move_member(member, channel2), loop)
            send_message(message.channel, 'Members in {0} have been migrated to {1}.'.format(channel1.name, channel2.name))


def quotes(message: discord.Message, argstr: str, loop):
    """Get, list, add or remove quotes for the server."""
    logging.info('Command: quotes')

    # if not on a server, invalid usage.
    if message.channel.is_private:
        send_message(message.channel, "This command can only be used on a server.")
        return

    # if no args, invalid usage.
    if len(argstr) == 0:
        send_message(message.channel, onSyntaxError('quotes', ''))
        return

    server = message.channel.server

    # if there have not been any registered quotes yet, create the list.
    if not server.id in link_bot.quotes.keys():
        link_bot.quotes[server.id] = list()

    # if "quotes <id>"
    if argstr.isdigit():
        id = int(argstr)
        if 0 <= id < len(link_bot.quotes[server.id]):
            q = link_bot.quotes[server.id][id]
            if q[1] != '':
                send_message(message.channel, '{0}\n\t\t\t-{1}'.format(q[1].replace('\\n', '\n'), q[0]))
                logging.info("Quote sent by ID.")
            else:
                send_message(message.channel, onSyntaxError('quotes', str(id) + ' is not a valid quote ID.'))
        else:
            send_message(message.channel, onSyntaxError('quotes', str(id) + ' is not a valid quote ID.'))

    # if "quotes random [author]"
    elif argstr.startswith('random'):
        authorArg = argstr[len('random '):].lstrip()
        authorCaps = message.content[len(link_bot.prefix):] if message.content.startswith(link_bot.prefix) else message.content
        authorCaps = authorCaps[len('quotes '):].lstrip()[len('random '):].lstrip()

        # compile a list of quotes by the author, or all quotes if not specified.
        quoteChoices = list()
        for q in link_bot.quotes[server.id]:
            # if we are looking to get a random quote from any author, or the quote's author is the one we're looking for...
            if q[1] != '' and (authorArg == '' or authorArg == q[0].lower()):
                quoteChoices.append(q)

        # if we dont have any quotes after going through all of them...
        if len(quoteChoices) == 0:
            if authorArg != '':
                send_message(message.channel, "I don't know any quotes from {0}.".format(authorCaps))
            else:
                send_message(message.channel, "I don't know any quotes yet.")
            return

        # seed the random number generator and return a random quote from our choices.
        random.seed()
        q = quoteChoices[random.randrange(0, len(quoteChoices))]
        send_message(message.channel, "{0}\n\t\t\t-{1}".format(q[1].replace('\\n', '\n'), q[0]))
        logging.info("Sent a random quote.")

    # if "quotes list [author]"
    elif argstr.startswith('list'):
        authorArg = argstr[len('list '):].lstrip()
        authorCaps = message.content[len(link_bot.prefix):] if message.content.startswith(link_bot.prefix) else message.content
        authorCaps = authorCaps[len('quotes '):].lstrip()[len('list '):].lstrip()

        i = 0
        quoteList = ''
        for q in link_bot.quotes[server.id]:
            if q[1] != '' and (authorArg == '' or authorArg == q[0].lower()):
                quoteList += "`{0}`: {1}   -{2}\n".format(i, q[1], q[0])
            i += 1

        # if no quotes were found for the author...
        if quoteList == '':
            if authorArg == '':
                send_message(message.channel, "I don't know any quotes yet.")
            else:
                send_message(message.channel, "I don't know any quotes from {0}".format(authorCaps))
            return

        if authorArg == '':
            send_message(message.channel, "Quotes from this server:\n{0}".format(quoteList.replace('\\n', '\n')))
        else:
            send_message(message.channel, "Quotes from {0}:\n{1}".format(authorCaps, quoteList.replace('\\n', '\n')))
        logging.info("Sent list of quotes.")

    # if "quotes add <quote -author>"
    elif argstr.startswith('add '):
        if not is_admin(message.author):
            send_message(message.author, "You must be an admin to use this command.")
            return

        args = message.content[len(link_bot.prefix):] if message.content.startswith(link_bot.prefix) else message.content
        args = args[len('quotes '):].lstrip()[len('add '):].lstrip()
        match = re.search('( -\w)', args)

        if match is None:
            send_message(message.channel, onSyntaxError('quotes', 'To add a quote, include a quote followed by -Author\'s Name.'))
            return

        # args[0] = author, args[1] = quote
        args = (args[match.start() + 2:], args[:match.start()].replace('\n', '\\n'))

        # check to see if there's a missing quote. If so, replace it with the new quote.
        for i in range(0, len(link_bot.quotes[server.id]) - 1):
            if link_bot.quotes[server.id][i][1] == '':
                link_bot.quotes[server.id][i] = (args[0], args[1])
                send_message(message.channel, "Added quote with ID {0}: \n{1} -{2}".format(len(link_bot.quotes[server.id]) - 1, args[1].replace('\\n', '\n'), args[0]))
                break
        # if there's not an empty quote, add this quote on the end.
        else:
            link_bot.quotes[server.id].append((args[0], args[1].lstrip()))
            send_message(message.channel, "Added quote with ID {0}: \n{1} -{2}".format(len(link_bot.quotes[server.id]) - 1, args[1].replace('\\n', '\n'), args[0]))

        save_quotes()
        logging.info("Added a new quote.")

    # if "@quotes remove <id>@"
    elif argstr.startswith('remove '):
        if not is_admin(message.author):
            send_message(message.author, "You must be an admin to use this command.")
            return

        id = argstr[len('remove '):].lstrip()
        try:
            id = int(id)
        except TypeError:
            send_message(message.channel, onSyntaxError('quotes', str(id) + ' is not a valid quote ID.'))
            return

        # if id is valid, delete the quote.
        if 0 <= id < len(link_bot.quotes[server.id]):
            q = link_bot.quotes[server.id][id]
            if link_bot.quotes[server.id][id][1] != '':
                link_bot.quotes[server.id][id] = ('', '')
                send_message(message.channel, "Removing quote: {0}\n\t\t\t-{1}".format(q[1].replace('\\n', '\n'), q[0]))
                save_quotes()
                logging.info("Quote removed.")
            else:
                send_message(message.channel, onSyntaxError('quotes', str(id) + ' is not a valid quote ID.'))

    # if "quotes <unknown args>"
    else:
        send_message(message.channel, onSyntaxError('quotes', 'Unknown sub-command.'))


# write relavent info about the provided player's league of legends game
def lolgame(message: discord.Message, argstr: str, loop):
    logging.info('Command: lolgame')

    # check for invalid argument count
    if len(argstr) == 0:
        send_message(message.channel, onSyntaxError('lolgame', 'You must provide a summoner name.'))
        return

    args = argstr.split(',')

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
            riot_api.region = arg_region
    else:
        riot_api.region = 'na'

    # get summoner
    api_request = riot_api.get_summoner(arg_summoner)

    # check that the summoner exists on the specified server
    if api_request.status_code != 200:
        if api_request.status_code == 404:
            send_message(message.channel, "{0} does not exist on the {1} server."
                                           .format(arg_summoner, riot_api.region))
        else:
            send_message(link_bot.owner,
                                           RiotAPI.get_status_code_string(api_request.status_code) + "\n" + api_request.url)
            send_message(message.channel, "An error occurred. Aborting the lookup."
                                           .format(arg_summoner, riot_api.region))
        return
    summoner = RiotAPI_classes.Summoner(api_request.json[arg_summoner])

    # get summoner's game
    api_request = riot_api.get_current_game(summoner.id)

    # check that the summoner is in a game
    if api_request.status_code != 200:
        if api_request.status_code == 404:
            send_message(message.channel, "{0} is not in a game."
                                           .format(summoner.name))
        else:
            send_message(link_bot.owner,
                                           RiotAPI.get_status_code_string(api_request.status_code) + "\n" + api_request.url)
            send_message(message.channel, "An error occurred. Aborting the lookup."
                                           .format(arg_summoner, riot_api.region))
        return
    playergame = api_request.json

    # begin organizing data
    send_message(message.channel, "Looking up {0}'s game on the {1} server..."
                                   .format(summoner.name, riot_api.region.upper()))
    asyncio.run_coroutine_threadsafe(client.send_typing(message.channel), loop)

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
    api_request = riot_api.get_summoner_by_id(player_ids)
    if api_request.status_code != 200:
        send_message(link_bot.owner,
                                       RiotAPI.get_status_code_string(api_request.status_code) + "\n" + api_request.url)
        send_message(message.channel, "An error occurred. Aborting the lookup."
                                       .format(arg_summoner, riot_api.region))
        return
    player_list = api_request.json

    # get each summoner's info
    for player in players:
        if str(player.id) in player_list:
            player.summoner = RiotAPI_classes.Summoner(player_list[str(player.id)])

    # get full list of champions in league of legends
    api_request = riot_api.get_all_champion_data(True)
    if api_request.status_code != 200:
        send_message(link_bot.owner,
                                       RiotAPI.get_status_code_string(api_request.status_code) + "\n" + api_request.url)
        send_message(message.channel, "An error occurred. Aborting the lookup."
                                       .format(arg_summoner, riot_api.region))
        return
    full_champ_list = api_request.json['data']

    # organize player info
    for player in players:

        # get player champion information
        player.champion = RiotAPI_classes.Champion(full_champ_list[str(player.champ_id)])

        # get player champion ranked stats
        acs = riot_api.get_champion_stats(player.id)
        if api_request.status_code != 200:
            if api_request.status_code == 404:
                logging.info("{0} has no ranked champion stats.".format(player.summoner.name))
            else:
                send_message(link_bot.owner,
                                               RiotAPI.get_status_code_string(api_request.status_code) + "\n" + api_request.url)
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
    api_request = riot_api.get_player_league_entry(player_ids)
    if api_request.status_code != 200:
        send_message(link_bot.owner,
                                       RiotAPI.get_status_code_string(api_request.status_code) + "\n" + api_request.url)
        send_message(message.channel, "An error occurred. Aborting the lookup."
                                       .format(arg_summoner, riot_api.region))
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
                                              RiotAPI_consts.MAPS[playergame['mapId']])\
        + format_as_column(' ', 58)\
        + format_as_column('|   Champion   | |', 17)\
        + format_as_column(' In Queue | |Total|', 16)\
        + '\n'\
        + format_as_column('Summoner Name', 17)\
        + format_as_column('Rank', 27)\
        + format_as_column('Champion', 15)\
        + format_as_column('Games', 6)\
        + format_as_column('Win%', 5)\
        + format_as_column('KDA', 6)\
        + format_as_column('Games', 6)\
        + format_as_column('Win%', 8)\
        + format_as_column('KDA', 5)\
        + '\n\nBLUE TEAM (Bottom Left):\n\n'
    for player in blueteam:
        gamestring += format_as_lol_player_output(player)
    gamestring += '\nRED TEAM (Top Right):\n\n'
    for player in redteam:
        gamestring += format_as_lol_player_output(player)
    gamestring += '```'
    send_message(message.channel, gamestring)
    logging.info("Sent League of Legends game info.")


# link the first youtube video found using the provided query
def youtube(message: discord.Message, argstr: str, loop):
    logging.info('Command: youtube')

    # check for missing args
    if len(argstr) == 0:
        send_message(message.channel, onSyntaxError('yt', 'You must provide a query to search for.'))
        return

    # get the search results
    api_request = google_api.search_for_video(argstr, 1)

    # check for bad status code
    if api_request.status_code != 200:
        send_message(message.channel, "An unknown error occurred. The quota limit may have been reached.")
        send_message(link_bot.owner, "Google API Error: \n" + api_request.url)
        return

    # send link to first search result
    logging.info(api_request.url)
    if len(api_request.json['items']) == 0:
        send_message(message.channel, "No results were found.")
    else:
        send_message(message.channel, "https://youtube.com/watch?v=" + api_request.json['items'][0]['id']['videoId'])
        logging.info("Sent YouTube video link.")


# link the first image found using the provided query
def image(message: discord.Message, argstr: str, loop):
    logging.info('Command: image')

    # check for missing args
    if len(argstr) == 0:
        send_message(message.channel, onSyntaxError('img', 'You must provide a query to search for.'))
        return

    # get the search results
    api_request = google_api.google_image_search(argstr)

    # check for bad status code
    if api_request.status_code != 200:
        send_message(message.channel, "An error occurred. The quota limit may have been reached.")
        send_error_message("Google API Error: \n" + api_request.url)
        return

    # send link to first search result
    if 'items' in api_request.json:
        send_message(message.channel, api_request.json['items'][0]['link'])
    else:
        send_message(message.channel, "No results were found.")
    logging.info("Sent Google image link.")


# play something in voice chat
def play(message: discord.Message, argstr: str, loop):
    if message.channel.is_private:
        send_message(message.channel, "This command may only be used in a server.")
        return

    voice = message.author.voice # type: discord.VoiceState
    if voice.voice_channel == None:
        send_message(message.channel, "You need to be in a voice channel.")
        return

    inSameServer = False # type: bool
    vc = None # type: typing.Optional[discord.VoiceClient]
    inSameChannel = False # type: bool

    # find out if we're in the same server/channel as our inviter.
    for voiceClient in client.voice_clients:
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
            client.join_voice_channel(voice.voice_channel)

    send_message(message.channel, "Kay, I joined.")


# suggest a new feature for the bot
def suggest(message: discord.Message, argstr: str, loop):
    logging.info('Command: suggest')
    if len(argstr) != 0:
        with link_bot.lock:
            suggestion_file = open(DATA_FOLDER + SUGGESTION_FILE, 'a')
            suggestion_file.write(argstr + '\n')
            suggestion_file.close()
        send_message(message.channel, 'Your suggestion has been noted!')
        logging.info('Suggestion has been noted.')
    else:
        send_message(message.channel, onSyntaxError('suggest', 'You should probably suggest something.'))


# enable/disable nsfw content in google searches
def nsfw(message: discord.Message, argstr: str, loop):
    logging.info('Command: nsfw')
    if message.channel.is_private:
        send_message(message.author, "You can only use this command on a server.")
        return
    elif not is_admin(message.author):
        send_message(message.author, "You must be an admin to use this command.")
        return

    if argstr == 'on':
        google_api.set_safe_search(False)
        client.send_message(message.author, "NSFW is now ON.")
        update_config()
    elif argstr == 'off':
        google_api.set_safe_search(True)
        client.send_message(message.author, "NSFW is now OFF.")
        update_config()
    elif len(argstr) == 0:
        if link_bot.nsfw:
            send_message(message.author, "NSFW is ON")
        else:
            send_message(message.author, "NSFW is OFF")
    else:
        send_message(message.author, onSyntaxError('nsfw', 'Specify on or off.'))
    logging.info('NSFW has been set/queried.')


# add/remove/list admins for the server in which the message was received
def admin(message: discord.Message, argstr: str, loop):
    logging.info('Command: admin')
    if len(argstr) == 0:
        send_message(message.channel, onSyntaxError('admin', ''))
        return
    if message.channel.is_private:
        send_message(message.channel, 'You can only use this command in a server.')
        return

    server = message.channel.server # type: discord.Server
    if server.id not in link_bot.admins.keys():
        link_bot.admins[server.id] = list()

    # if "admin list"
    if argstr == 'list':
        if len(link_bot.admins[server.id]) == 0:
            send_message(message.channel, 'There are no admins on this server.')
            return

        # get the admin names from their IDs, save them to a string, then send it to the channel.
        admins = 'Admins: '
        needs_comma = False
        for member in server.members:
            if member.id in link_bot.admins[server.id]:
                if needs_comma:
                    admins += ', '
                admins += member.name
                needs_comma = True
        send_message(message.channel, admins)
        logging.info("Listed admins.")

    # if "admin add"
    elif argstr.startswith('add'):
        if not is_admin(message.author):
            send_message(message.author, "You must be an admin to use this command.")
            return

        # the output message at the end.
        msg = ''
        # if there is a member mention, add them as an admin.
        for member in message.mentions:
            if member.id in link_bot.admins[server.id]:
                msg += get_name(member) + " is already an admin.\n"
            else:
                link_bot.admins[server.id].append(member.id)
                msg += "Added " + get_name(member) + " as an admin.\n"
        # if there is a role mention, add all members with that role as an admin.
        for role in message.role_mentions:
            for member in message.channel.server.members:
                if role in member.roles:
                    if member.id in link_bot.admins[server.id]:
                        msg += get_name(member) + " is already an admin.\n"
                    else:
                        link_bot.admins[server.id].append(member.id)
                        msg += "Added " + get_name(member) + " as an admin.\n"
        # output
        save_admins()
        send_message(message.channel, msg)
        logging.info("Added admins.")

    # if "admin remove"
    elif argstr.startswith('remove'):
        if not is_admin(message.author):
            send_message(message.author, "You must be an admin to use this command.")
            return
        # the output message at the end.
        msg = ''
        # if there is a member mention, add them as an admin.
        for member in message.mentions:
            if member.id not in link_bot.admins[server.id]:
                msg += get_name(member) + " is not an admin.\n"
            else:
                link_bot.admins[server.id].remove(member.id)
                msg += "Removed " + get_name(member) + " from the admin list.\n"
        # if there is a role mention, add all members with that role as an admin.
        for role in message.role_mentions:
            for member in message.channel.server:
                if role in member.roles:
                    if member.id not in link_bot.admins[server.id]:
                        msg += get_name(member) + " is not an admin.\n"
                    else:
                        link_bot.admins[server.id].remove(member.id)
                        msg += "Removed " + get_name(member) + " from the admin list.\n"
        # output
        save_admins()
        send_message(message.channel, msg)
        logging.info("Removed admins.")

    # if "admin <unknown args>"
    else:
        send_message(message.channel, '{0} is not a valid argument.'.format(argstr))


# log the bot out
def logout(message: discord.Message, argstr: str, loop):
    logging.info("Command: logout")
    link_bot.requestedStop = True  # prevent a restart
    if not is_owner(message.author):
        send_message(message.channel, "You must be the bot's owner to use this command.")
        return

    # disable message reading
    link_bot.isStopping = True

    logging.info('Waiting for command threads to finish.')
    for thread in threading.enumerate():
        if thread.name.startswith('cmd') and thread.is_alive() and thread.name != 'cmd_logout':
            logging.info('Currently waiting on: ' + thread.name)
            thread.join()

    send_message(link_bot.owner, "Logging out.")
    link_bot.active = False
