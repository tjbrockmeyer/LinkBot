import requests
import time
import sys
from collections import deque
from RiotAPI.Classes import *
from RiotAPI.Consts import *


class APIResponse:
    def __init__(self, response):
        self.json = response.json()
        self.status_code = response.status_code
        self.url = response.url


class RiotAPIError(Exception):
    def __init__(self, response: APIResponse):
        self.url = response.url
        self.status_code = response.status_code
        self.message = response.json['status']['message']


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


class RequestTimer(object):
    def __init__(self, limit_10s, limit_10m):
        self.limit_10s = limit_10s
        self.limit_10m = limit_10m
        self.stack_10s = deque()
        self.stack_10m = deque()


    def add_request(self):
        """
        Adds a request timer to each stack
        """

        now = time.time()
        self.stack_10s.append(now)
        self.stack_10m.append(now)


    def remove_expired(self):
        """
        Removes request timers on each stacks that have lifetimes longer than their respective maximums.
        """

        now = time.time()
        while len(self.stack_10s) and now - self.stack_10s[0] > 10:
            self.stack_10s.popleft()
        while len(self.stack_10m) and now - self.stack_10m[0] > 600:
            self.stack_10m.popleft()


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


class Client(object):
    def __init__(self, api_key, region='na', production_key=False):
        """
        :param api_key: Your unique API Key for accessing Riot's API
        :param region: Optionally pass your region. Default = 'na'
        :param production_key: LEAVE FALSE, unless you have a special production key that increases request limits.
        """
        if production_key:
            limits = (REQUEST_LIMITS['production_10s'], REQUEST_LIMITS['production_10m'])
        else:
            limits = (REQUEST_LIMITS['normal_10s'], REQUEST_LIMITS['normal_10m'])
        self.api_key = api_key
        self.region = region
        self.requests = RequestTimer(*limits)
        self.ddversion = ('', 0)    # version number and time it was set at


    def _request(self, api_url, params=None, queue=True):
        """
        Request data from Riot's API
        :param str api_url: The URL to follow for what is asked for.
        :param dict params: Any other parameters that need to be passed
        :return: The server's response.
        :rtype: APIResponse
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
        response = APIResponse(requests.get(api_url, params=args))
        if queue:
            self.requests.add_request()
        if response.status_code != 200:
            raise RiotAPIError(response)
        return response

    def _basic_format(self, api_section):
        url = API_URL['base'] + API_URL[api_section]
        return url.format(region=PLATFORMS[self.region], version=API_VERSION[api_section])

    # -----------------------------
    #      CHAMPION MASTERY
    # -----------------------------

    def _champion_mastery_format(self, destination):
        return self._request(self._basic_format('championmastery') + destination)

    def get_champion_mastery_all(self, summoner_id):
        response = self._champion_mastery_format('champion-masteries/by-summoner/{}'.format(summoner_id))
        return [ChampionMastery(d) for d in response.json]

    def get_champion_mastery(self, summoner_id, champion_id):
        response = self._champion_mastery_format('champion-masteries/by-summoner/{}/by-champion/{}'.format(summoner_id, champion_id))
        return ChampionMastery(response.json)

    def get_champion_mastery_score(self, summoner_id):
        response = self._champion_mastery_format('scores/by-summoner/{}'.format(summoner_id))
        return response.json

    # -----------------------------
    #          CHAMPION
    # -----------------------------

    def _champion_client_format(self, destination, **kwargs):
        return self._request(self._basic_format('champion') + destination, kwargs, queue=False)

    def get_champion_client_all(self, free_to_play=False):
        response = self._champion_client_format('champions/', freeToPlay=free_to_play)
        return [ChampionClientInfo(d) for d in response.json['champions']]

    def get_champion_client_by_id(self, champ_id):
        response = self._champion_client_format('champions/{}'.format(champ_id))
        return ChampionClientInfo(response.json)

    # -----------------------------
    #           LEAGUE
    # -----------------------------

    def _league_format(self, destination):
        return self._request(self._basic_format('league') + destination)

    def get_league_entries(self, player_id):
        response = self._league_format( 'positions/by-summoner/{}'.format(player_id))
        return [LeagueEntry(e) for e in response.json]

    # -----------------------------
    #        STATIC DATA
    # -----------------------------

    # https://tr1.api.riotgames.com/lol/league/v3/positions/by-summoner/238407
    # https://TR1.api.riotgames.com/lol/league/v3/positions/by-summoner/238407

    def _static_data_format(self, destination, **kwargs):
        return self._request(self._basic_format('lol-static-data') + destination, kwargs, queue=False)

    def get_champion_static_all(self, tag=""):
        """ - tag="" (default)
        - tag=all
        - tag=(allytips, blurb, enemytips, image, info, lore, partype,
                passive, recommended, skins, spells, stats, tags)"""
        if tag == '':
            response = self._static_data_format('champions')
        else:
            response = self._static_data_format('champions', tags=tag)
        return {v['id']: Champion(v) for v in response.json['data'].values()}

    def get_champion_static(self, champ_id, tag=""):
        """ - tag="" (default)
        - tag=all
        - tag=(allytips, blurb, enemytips, image, info, lore, partype,
                passive, recommended, skins, spells, stats, tags)"""
        if tag == '':
            response = self._static_data_format('champions/{}'.format(champ_id))
        else:
            response = self._static_data_format('champions/{}'.format(champ_id), tags=tag)
        return Champion(response.json)

    # -----------------------------
    #           STATUS
    # -----------------------------



    # -----------------------------
    #           MATCH
    # -----------------------------



    # -----------------------------
    #          SPECTATOR
    # -----------------------------

    def _spectator_format(self, destination):
        return self._request(self._basic_format('spectator') + destination)

    def get_active_game(self, summoner_id):
        response = self._spectator_format('active-games/by-summoner/{}'.format(summoner_id))
        return ActiveGame(response.json)

    # -----------------------------
    #          SUMMONER
    # -----------------------------

    def _summoner_format(self, destination):
        return self._request(self._basic_format('summoner') + destination)

    def get_summoner_by_id(self, summoner_id):
        response = self._summoner_format('summoners/' + str(summoner_id))
        return Summoner(response.json)

    def get_summoner(self, summoner_name):
        response = self._summoner_format('summoners/by-name/' + summoner_name)
        return Summoner(response.json)

    def get_summoner_by_account_id(self, account_id):
        response = self._summoner_format('summoners/by-account/' + str(account_id))
        return Summoner(response.json)

    # -----------------------------
    #         DATA DRAGON
    # -----------------------------

    def _ddragon_url(self, include_version=True):
        now = time.time()
        if now - self.ddversion[1] > 1800:
            response = self._request(self._basic_format('lol-static-data') + '/versions', queue=False)
            if response.status_code == 200:
                self.ddversion = (list(response.json)[0], now)

        if include_version:
            return API_URL['data-dragon'] + '{}/'.format(self.ddversion[0])
        else:
            return API_URL['data-dragon']

    def get_summoner_icon(self, icon_id):
        return self._ddragon_url() + 'img/profileicon/{}.png'.format(icon_id)

    def get_champion_splash(self, champ_name, skin_num=0):
        return self._ddragon_url(include_version=False) + "img/champion/splash/{}_{}.jpg".format(champ_name, skin_num)

    def get_champion_load_screen(self, champ_name, skin_num=0):
        return self._ddragon_url(include_version=False) + "img/champion/loading/{}_{}.jpg".format(champ_name, skin_num)

    def get_champion_square(self, champion_name):
        return self._ddragon_url() + "img/champion/{}.png".format(champion_name)

    def get_champion_passive_img(self, image_info: ImageInfo):
        return self._ddragon_url() + "img/passive/{}".format(image_info.full)

    def get_champion_ability_img(self, image_info: ImageInfo):
        return self._ddragon_url() + "img/spell/{}".format(image_info.full)

    def get_summoner_spell_img(self, ss_name):
        return self._ddragon_url() + "img/spell/Summoner{}.png".format(ss_name)

    def get_item_img(self, image_info: ImageInfo):
        return self._ddragon_url() + "img/item/{}".format(image_info.full)

    def get_mastery_img(self, image_info: ImageInfo):
        return self._ddragon_url() + "img/mastery/{}".format(image_info.full)

    def get_rune_img(self, image_info: ImageInfo):
        return self._ddragon_url() + "img/rune/{}".format(image_info.full)

    def get_sprite_img(self, image_info):
        return self._ddragon_url() + "img/sprite/spell{}.png".format(image_info)

    def get_minimap_img(self, map_id):
        return self._ddragon_url() + "img/map/map{}.png".format(map_id)

    def get_scoreboard_icon(self, icon_name):
        return self._ddragon_url(include_version=False) + "/5.5.1/img/ui/{}.png".format(icon_name)
