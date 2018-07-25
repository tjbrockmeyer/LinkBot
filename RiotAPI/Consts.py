
LEGAL = "\
{application_name} isn't endorsed by Riot Games and doesn't reflect the views or opinions of \
Riot Games or anyone officially involved in producing or managing League of Legends. League of Legends and Riot Games \
are trademarks or registered trademarks of Riot Games, Inc. League of Legends © Riot Games, Inc."

API_VERSION = {
    'champion': '3',
    'championmastery': '3',
    'league': '3',
    'lol-static-data': '3',
    'lol-status': '3',
    'match': '3',
    'spectator': '3',
    'summoner': '3',
    'third-party-code': '3',
    'tournament-stub': '3',
    'tournament': '3'
}

API_URL = {
    'base': 'https://{region}.api.riotgames.com/',

    'championmastery': 'lol/champion-mastery/v{version}/',
    'champion': 'lol/platform/v{version}/',
    'league': 'lol/league/v{version}/',
    'lol-static-data': 'lol/static-data/v{version}/',
    'lol-status': 'lol/status/v{version}/',
    'match': 'lol/match/v{version}/',
    'spectator': 'lol/spectator/v{version}/',
    'summoner': 'lol/summoner/v{version}/',
    'third-party-code': 'lol/platform/v{version}/third-party-code/',
    'tournament-stub': 'lol/tournament-stub/v{version}/',
    'tournament': 'lol/tournament/v{version}/',

    'data-dragon': 'http://ddragon.leagueoflegends.com/cdn/'
}

REQUEST_LIMITS = {
    'normal_10s': 60,
    'normal_10m': 300,
    'production_10s': 3000,
    'production_10m': 180000
}

PLATFORMS = {
    'br': 'BR1',
    'eune': 'EUN1',
    'euw': 'EUW1',
    'jp': 'JP1',
    'kr': 'KR',
    'lan': 'LA1',
    'las': 'LA2',
    'na': 'NA1',
    'oce': 'OC1',
    'tr': 'TR1',
    'ru': 'RU',
    'pbe': 'PBE1'
}

ERRORS = {
    200: 'No Error',
    400: 'Bad request',
    401: 'Unauthorized',
    403: 'Forbidden',
    404: 'Not found',
    415: 'Unsupported media type',
    429: 'API key rate limit exceeded',
    500: 'Internal server error',
    503: 'Service unavailable',
    504: 'Gateway timeout'
}

QUEUE_TYPES = {
    0: 'Custom Game',
    72: '1v1',
    73: '2v2',
    75: 'Hexakill',
    76: 'URF',
    78: 'One For All Mirror 5v5',
    83: 'Coop vs AI URF',
    98: 'Hexakill TT',
    100: 'Bilgewater ARAM',
    310: 'Nemesis Draft',
    313: 'Black Market Brawlers',
    317: 'Definitely not Dominion',
    400: 'Normal Flex 5v5',
    420: 'Ranked Solo/Duo',
    440: 'Ranked Flex 5v5',
    450: 'ARAM',
    460: '3v3 (Blind Pick)',
    470: 'Ranked Flex 3v3',
    600: 'Blood Hunt Assassin',
    610: 'Dark Star: Singularity',
    700: 'Clash',
    800: 'Coop vs AI TT (Intermediate)',
    810: 'Coop vs AI TT (Intro)',
    820: 'Coop vs AI TT (Beginner)',
    830: 'Coop vs AI (Intro)',
    840: 'Coop vs AI (Beginner)',
    850: 'Coop vs AI (Intermediate)',
    900: 'ARURF',
    910: 'Ascension',
    920: 'Legend of the Poro King',
    940: 'Nexus Siege',
    950: 'Doom Bots (Voting)',
    960: 'Doom Bots',
    980: 'Star Guardian Invasion (Normal)',
    990: 'Star Guardian Invasion (Onslaught)',
    1000: 'Overcharge',
    1010: 'Snow ARURF',
    1020: 'One for All',
}

RANKED_QUEUES = {
    420: 'RANKED_SOLO_5x5',
    440: 'RANKED_FLEX_SR',
    470: 'RANKED_FLEX_TT',
}

GAME_MODES = {
    'CLASSIC': 'Classic',
    'ODIN': 'Dominion',
    'ARAM': 'ARAM',
    'TUTORIAL': 'Tutorial',
    'ONEFORALL': 'One For All',
    'ASCENSION': 'Ascension',
    'FIRSTBLOOD': 'Snowdown Showdown',
    'KINGPORO': 'Legend of the Poro King',
    'SIEGE': 'Nexus Siege'
}

MAPS = {
    1: "Summoner's Rift (Old Version)",
    2: "Summoner's Rift (Winter)",
    3: "The Proving Grounds",
    4: "Twisted Treeline",
    8: "The Crystal Scar",
    10: "Twisted Treeline",
    11: "Summoner's Rift",
    12: "Howling Abyss",
    14: "Butcher's Bridge"
}

GAME_TYPES = {
    'MATCHED_GAME': 'Matchmade',
    'CUSTOM_GAME': 'Custom',
    'TUTORIAL_GAME': 'Tutorial'
}