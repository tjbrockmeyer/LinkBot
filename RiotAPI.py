import requests
import time
import sys
from collections import deque
from RiotAPI_consts import *


def wait_with_updates(wait_time):
    """
    Waits for the specified amount of seconds while placing a '.' in the console every second
    :param wait_time: The amount of time to wait
    """

    for i in range(1, int(wait_time) + 1):      # Wait for the integer time,
        time.sleep(1)
        print('.', end='')
        sys.stdout.flush()
        if i % 10 == 0:
            print('')
    time.sleep(wait_time % 1)                   # Wait for the fractional time
    if wait_time >= 1:
        print('')


def get_status_code_string(code):
    if code in ERRORS:
        return 'Error ' + str(code) + ': ' + ERRORS[code]
    else:
        return 'Error ' + str(code) + ': An unknown error occurred.'


class RequestTimer(object):

    # CONSTRUCTOR
    def __init__(self, limit_10s, limit_10m):
        self.limit_10s = limit_10s
        self.limit_10m = limit_10m
        self.stack_10s = deque()
        self.stack_10m = deque()

    # PULBIC
    def add_request(self):
        """
        Adds a request timer to each stack
        """

        now = time.time()
        self.stack_10s.append(now)
        self.stack_10m.append(now)

    # PUBLIC
    def remove_expired(self):
        """
        Removes request timers on each stacks that have lifetimes longer than their respective maximums.
        """

        now = time.time()
        while len(self.stack_10s) and now - self.stack_10s[0] > 10:
            self.stack_10s.popleft()
        while len(self.stack_10m) and now - self.stack_10m[0] > 600:
            self.stack_10m.popleft()

    # PUBLIC
    def get_wait_time(self):
        """
        Waits for the remaining duration of the first item in a stack that is full.
        Requires a run of remove_expired() for effectivity first.
        :return: The time to wait until making another request.
        """

        now = time.time()
        wait_time = 0
        if len(self.stack_10m) >= self.limit_10m:
            wait_time = 600 - (now - self.stack_10m[0])
        if len(self.stack_10s) >= self.limit_10s:
            wait_time += 10 - (now - self.stack_10s[0])
        return wait_time


class APIRequest:

    def __init__(self, json, status_code, url):
        self.json = json
        self.status_code = status_code
        self.url = url


class Client(object):
    """
    :members:
        string              api_key     //api_key used to access Riot's API
        string              region      //region located in
        RequestTimer        requests    //timer for requests. has limits and queues for 10s and 10m.
        tuple(str, float)   ddversion   //version of data dragon. str is version number, float is time when last set

    :functions:
        get_champion_client_data()
        get_champions_client_data()

        get_champion_mastery()
        get_all_champion_mastery()
        get_champion_mastery_score()
        get_top_champions()

        get_all_champion_data()
        get_champion_data()
        get_locales()

        get_summoner_icon()
        get_champion_splash()
        get_champion_load_screen()
        get_champion_square()
        get_champion_passive_img()
        get_champion_ability_img()
        get_summoner_spell_img()
        get_item_img()
        get_mastery_img()
        get_rune_img()
        get_sprite_img()
        get_minimap_img()
        get_scoreboard_icon()

        get_summoner()
    """

    # CONSTRUCTOR
    def __init__(self, api_key, region='na', production_key=False):
        """
        :param api_key: Your unique API Key for accessing Riot's API
        :param region: Optionally pass your region. Default = 'na'
        :param production_key: LEAVE FALSE, unless you have the special production key that increases request limits.
        """

        if production_key:
            limits = (REQUEST_LIMITS['production_10s'], REQUEST_LIMITS['production_10m'])
        else:
            limits = (REQUEST_LIMITS['normal_10s'], REQUEST_LIMITS['normal_10m'])
        self.api_key = api_key
        self.region = region
        self.requests = RequestTimer(*limits)
        self.ddversion = ('', 0)    # version number and time it was set at

    # PRIVATE
    def _request(self, api_url, params=None, queue=True):
        """
        Request data from Riot's API
        :param api_url: The URL to follow for what is asked for.
        :param params: Any other parameters that need to be passed
        :return: The server's response as a Dictionary
        """

        if params is None:
            params = {}

        # Places the api key into the args
        args = {'api_key': self.api_key}

        # Adds any other items in params that are not duplicates into args.
        for key, value in params.items():
            if key not in args:
                args[key] = value

        self.requests.remove_expired()
        wait_with_updates(self.requests.get_wait_time())
        response = requests.get(api_url, params=args)
        if queue:
            self.requests.add_request()

        return APIRequest(response.json(), response.status_code, response.url)

    # PRIVATE
    def _basic_format(self, api_section, alt_proxy=None):
        """
        Returns a formatted version of the requested section of the api.
        Formats {proxy}, {region}, {version}
        :param api_section: The section of the api being requested
        :param alt_proxy: Specify a different proxy if the method requires it.
        :return: The formatted string.
        """

        if alt_proxy is None:
            alt_proxy = self.region
        string = API_URL['base'] + API_URL[api_section]
        return string.format(proxy=alt_proxy, region=self.region, version=API_VERSION[api_section])

    # -----------------------------
    #          CHAMPION
    # -----------------------------
    # PRIVATE
    def _champion_format(self, destination, args=None):

        if args is None:
            args = {}

        return self._request(self._basic_format('champion') + destination, args)

# PUBLIC
    def get_champions_client_data(self):
        """
        Get the full list of champions.
        Includes: ID, bot-matchmaking-enabled, bot-enabled, active, freetoplay.
        :return: Dictionary with the full list of champs
        """

        return self._champion_format('')

    # PUBLIC
    def get_champion_client_data(self, champ_id):
        """
        Returns the specified champion
        :param champ_id: The ID of the champion desired
        :return: Dictionary with the champion's info
        """

        return self._champion_format('/{id}'.format(id=champ_id))

    # -----------------------------
    #      CHAMPION MASTERY
    # -----------------------------
    # PRIVATE
    def _champion_mastery_format(self, player_id, destination, args=None):

        if args is None:
            args = {}

        return self._request(self._basic_format('championmastery') +
                             '/location/{platform}/player/{player}'.format(platform=PLATFORMS[self.region],
                                                                           player=player_id) + destination, args)

    # PUBLIC
    def get_champion_mastery(self, player_id, champion_id):
        """
        Get's player's champion mastery info for specified champion.
        :param player_id: The player to get champion mastery from
        :param champion_id: The champion to get mastery info about
        :return: A Dictionary [ChampionMasteryDTO]
        """

        return self._champion_mastery_format(player_id, '/champion/' + champion_id)

    # PUBLIC
    def get_all_champion_mastery(self, player_id):
        """
        Gets all of the player's champion mastery datum
        :param player_id: The player to get champ mastery info for
        :return: A DictionaryOf[ChampionMasteryDTO]
        """

        return self._champion_mastery_format(player_id, '/champions')

    # PUBLIC
    def get_champion_mastery_score(self, player_id):
        """
        Gets the player's total mastery score: the sum of all of their levels on all champs
        :param player_id: the player to get the mastery score of
        :return: A Dictionary containing the mastery score of the player [int]
        """

        return self._champion_mastery_format(player_id, '/score')

    # PUBLIC
    def get_top_champions(self, player_id, count=3):
        """
        Get the player's 'amount' highest scoring champions by mastery points and all of their mastery info.
        :param player_id: Player to get mastery info for
        :param count: Amount of top champions to get info for
        :return: A DictionaryOf[ChampionMasteryDTO]
        """

        args = {'count': count}
        return self._champion_mastery_format(player_id, '/topchampions', args)

    # -----------------------------
    #        CURRENT GAME
    # -----------------------------

    def get_current_game(self, player_id):
        return self._request(self._basic_format('current-game') + '/{0}/{1}'.format(PLATFORMS[self.region], player_id))

    # -----------------------------
    #        STATIC DATA
    # -----------------------------
    # PRIVATE
    def _static_data_format(self, destination, args=None):

        if args is None:
            args = {}

        return self._request(self._basic_format('lol-static-data', 'global') + destination, args, queue=False)

    # PUBLIC
    def get_all_champion_data(self, data_by_id=False, data=None):
        """
        Gets the data for all champions
        :param data: Extra specific data to be added [string]
        :param data_by_id: specify to set the tags as the champs' ids instead of their names.
        :return: All info provided in a Dictionary. See Riot API Documentation.
        """

        if data is None:
            args = {'dataById': data_by_id}
        else:
            args = {
                'champData': str(data),
                'dataById': data_by_id
            }
        return self._static_data_format('/champion', args)

    # PUBLIC
    def get_champion_data(self, champ_id, data=None):
        """
        Gets the data for the champion whose ID is provided.
        :param champ_id: ID of champ to get name for
        :param data: Extra specific data to be added [string]
            SA: https://developer.riotgames.com/api/methods#!/1055/3622
        :return: Champ info provided in a Dictionary. See Riot API Documentation.
        """

        if data is None:
            args = {}
        else:
            args = {'champData': str(data)}
        return self._static_data_format('/champion/{id}'.format(id=champ_id), args)

    # PUBLIC
    def get_locales(self):
        """
        Gets a list of all supported locales
        :return: All locales in List form
        """

        return self._static_data_format('/languages')

    # -----------------------------
    #         DATA DRAGON
    # -----------------------------
    # PRIVATE
    def _ddragon_url(self, include_version=True):
        """
        Checks the data dragon version and updates it if the lifetime is too long.
        :param include_version: Currently, champion splash, and loading screen do not require a version in the url
        """

        now = time.time()
        if now - self.ddversion[1] > 1800:
            versions = list(self._request(self._basic_format('lol-static-data') + '/versions', queue=False))
            self.ddversion = (versions[0], now)

        if include_version:
            return API_URL['data-dragon'] + '/{version}'.format(version=self.ddversion[0])
        else:
            return API_URL['data-dragon']

    # PUBLIC
    def get_summoner_icon(self, icon_id):
        """
        Gets the image to go with the icon id provided.
        :param icon_id: The ID of the icon to be retrieved
        :return: A link to the image as a string.
        """

        return self._ddragon_url() + '/img/profileicon/{icon_id}.png'.format(icon_id=icon_id)

    # PUBLIC
    def get_champion_splash(self, champ_name, skin_num=0):
        """
        Gets the splash art of the champion whose name is provided
        :param champ_name: Name of champion desired.
        :param skin_num: Number of the skin to get the splash for. Default: 0 = classic skin.
            SA: https://developer.riotgames.com/docs/static-data
        :return: A link to the image as a string.
        """

        return self._ddragon_url(include_version=False) + \
            "/img/champion/splash/{name}_{skin}.jpg".format(name=champ_name, skin=skin_num)

    # PUBLIC
    def get_champion_load_screen(self, champ_name, skin_num=0):
        """
        Gets the load screen art of the champion whose name is provided
        :param champ_name: Name of champion desired.
        :param skin_num: Number of the skin to get the load screen art for. Default: 0 = classic skin.
            SA: https://developer.riotgames.com/docs/static-data
        :return: A link to the image as a string.
        """

        return self._ddragon_url(include_version=False) + \
            "/img/champion/loading/{name}_{skin}.jpg".format(name=champ_name, skin=skin_num)

    # PUBLIC
    def get_champion_square(self, champ_name):
        """
        Gets the square art of the champion whose name is provided
        :param champ_name: Name of champion desired.
        :return: A link to the image as a string.
        """

        return self._ddragon_url() + "/img/champion/{name}.png".format(name=champ_name)

    # PUBLIC
    def get_champion_passive_img(self, passive_name):
        """
        Gets the art for the passive whose name is provided.
        :param passive_name: Full name of passive ability AND EXTENSION (.png) requested.
            SA: https://developer.riotgames.com/docs/static-data
        :return: A link to the image as a string.
        """

        return self._ddragon_url() + "/img/passive/{name}".format(name=passive_name)

    # PUBLIC
    def get_champion_ability_img(self, ability_name):
        """
        Gets the art for the ability whose name is provided.
        :param ability_name: Full name of QWER ability AND EXTENSION (.png) requested.
            SA: https://developer.riotgames.com/docs/static-data
        :return: A link to the image as a string.
        """

        return self._ddragon_url() + "/img/spell/{name}".format(name=ability_name)

    # PUBLIC
    def get_summoner_spell_img(self, ability_name):
        """
        Gets the art for the summoner spell whose name is provided.
        :param ability_name: Full name of summoner spell requested. Format: "Summoner[Spell]"
        :return: A link to the image as a string.
        """

        return self._ddragon_url() + "/img/spell/Summoner{name}.png".format(name=ability_name)

    # PUBLIC
    def get_item_img(self, item_id):
        """
        Gets the art for the item whose ID is provided.
        :param item_id: ID of the item to get the image for
        :return: A link to the image as a string.
        """

        return self._ddragon_url() + "/img/item/{id}.png".format(id=item_id)

    # PUBLIC
    def get_mastery_img(self, mastery_id):
        """
        Gets the art for the mastery whose ID is provided.
        :param mastery_id: ID of the mastery to get the image for
        :return: A link to the image as a string.
        """

        return self._ddragon_url() + "/img/mastery/{id}.png".format(id=mastery_id)

    # PUBLIC
    def get_rune_img(self, rune_id):
        """
        Gets the art for the rune whose ID is provided.
        :param rune_id: ID of the rune to get the image for
        :return: A link to the image as a string.
        """

        return self._ddragon_url() + "/img/rune/{id}.png".format(id=rune_id)

    # PUBLIC
    def get_sprite_img(self, page_id):
        """
        Gets the art for the sprite page whose ID is provided.
        :param page_id: ID of the sprite page to get the image for
        :return: A link to the image as a string.
        """

        return self._ddragon_url() + "/img/sprite/spell{id}.png".format(id=page_id)

    # PUBLIC
    def get_minimap_img(self, minimap_id):
        """
        Gets the art for the minimap whose ID is provided.
        :param minimap_id: ID of the minimap to get the image for
        :return: A link to the image as a string.
        """

        return self._ddragon_url() + "/img/map/map{id}.png".format(id=minimap_id)

    # PUBLIC
    def get_scoreboard_icon(self, icon_name):
        """
        Gets the art for the scoreboard icon whose ID is provided.
        :param icon_name: Name of the scoreboard icon to get the image for
        :return: A link to the image as a string.
        """

        return self._ddragon_url(include_version=False) + "/5.5.1/img/ui/{name}.png".format(name=icon_name)

    # -----------------------------
    #           LEAGUE
    # -----------------------------

    def get_player_league_entry(self, player_id):

        return self._request(self._basic_format('league') + '/by-summoner/{0}/entry'.format(player_id))

    # -----------------------------
    #        MATCH HISTORY
    # -----------------------------

    # -----------------------------
    #           STATS
    # -----------------------------

    def get_champion_stats(self, player_id):

        return self._request(self._basic_format('stats') + '/by-summoner/{0}/ranked'.format(player_id))

    def get_player_stats(self, player_id):

        return self._request(self._basic_format('stats') + '/by-summoner/{0}/summary'.format(player_id))

    # -----------------------------
    #          SUMMONER
    # -----------------------------
    # PRIVATE
    def _summoner_format(self, destination, args=None):

        return self._request(self._basic_format('summoner') + destination, args)

    # PUBLIC
    def get_summoner_by_id(self, ids):
        """
        Supply a Summoner ID, or a comma delimited list of Summoner IDs and be given their info by Dictionary
        :param ids: Summoner ID(s) to get the info of, comma-seperated, max of 40 at one time.
        :return: The summoner's info in a Dictionary [SummonerDto]
        """

        return self._summoner_format('/' + ids)

    # PUBLIC
    def get_summoner(self, names):
        """
        Supply a Summoner Name, or a comma delimited list of Summoner Names and be given their info by Dictionary
        :param names: Summoner name(s) to get the info of, comma-seperated, max of 40 at one time.
        :return: The summoner's info in a Dictionary [SummonerDto]
        """

        return self._summoner_format('/by-name/' + names)
