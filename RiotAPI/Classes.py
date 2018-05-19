
from RiotAPI.Consts import *


class ChampionClientInfo:
    def __init__(self, data):
        self.ranked_play_enabled = bool(data['rankedPlayEnabled'])
        self.bot_enabled = bool(data['botEnabled'])
        self.bot_mm_enabled = bool(data['botMmEnabled'])
        self.active = bool(data['active'])
        self.free_to_play = bool(data['freeToPlay'])
        self.id = data['id']


class ChampionMastery:
    def __init__(self, data):
        self.chest = bool(data['chestGranted'])
        self.level = int(data['championLevel'])
        self.points = int(data['championPoints'])
        self.id = data['championId']
        self.player_id = data['playerId']
        self.pts_to_next_level = int(data['championPointsUntilNextLevel'])
        self.tokens_earned = int(data['tokensEarned'])
        self.pts_from_prev_level = int(data['championPointsSinceLastLevel'])
        self.last_play_time = int(data['lastPlayTime'])


class Series:
    def __init__(self, data):
        self.wins = int(data['wins'])
        self.losses = int(data['losses'])
        self.target = int(data['target'])
        self.progress = data['progress']


class LeagueEntry:
    def __init__(self, data):
        self.queue_type = data['queueType']
        self.hot_streak = bool(data['hotStreak'])
        self.wins = int(data['wins'])
        self.veteran = bool(data['veteran'])
        self.losses = int(data['losses'])
        self.player_or_team_id = data['playerOrTeamId']
        self.player_or_team_name = data['playerOrTeamName']
        self.league_name = data['leagueName']
        self.inactive = bool(data['inactive'])
        self.rank = data['rank']
        self.fresh_blood = bool(data['freshBlood'])
        self.league_id = data['leagueId']
        self.tier = data['tier']
        self.points = int(data['leaguePoints'])
        self.series = None if 'miniSeries' not in data else Series(data['miniSeries'])


class ChampionOverview:
    def __init__(self, data):
        self.difficulty = int(data['difficulty'])
        self.attack = int(data['attack'])
        self.defense = int(data['defense'])
        self.magic = int(data['magic'])


class Stats:
    def __init__(self, data):
        self.move_speed = float(data['movespeed'])
        self.attack_range = float(data['attackrange'])

        self.hp = float(data['hp'])
        self.hp_per_level = float(data['hpperlevel'])
        self.hp_regen = float(data['hpregen'])
        self.hp_regen_per_level = float(data['hpregenperlevel'])

        self.mana = float(data['mp'])
        self.mana_per_level = float(data['mpperlevel'])
        self.mana_regen = float(data['mpregen'])
        self.mana_regen_per_level = float(data['mpregenperlevel'])

        self.armor = float(data['armor'])
        self.armor_per_level = float(data['armorperlevel'])
        self.magic_resist = float(data['spellblock'])
        self.magic_resist_per_level = float(data['spellblockperlevel'])

        self.attack_damage = float(data['attackdamage'])
        self.attack_damage_per_level = float(data['attackdamageperlevel'])
        self.attack_speed_offset = float(data['attackspeedoffset'])
        self.attack_speed_per_level = float(data['attackspeedperlevel'])
        self.crit = float(data['crit'])
        self.crit_per_level = float(data['critperlevel'])


class ImageInfo:
    def __init__(self, data):
        self.full = data['full']
        self.group = data['group']
        self.sprite = data['sprite']
        self.x = int(data['x'])
        self.y = int(data['y'])
        self.w = int(data['w'])
        self.h = int(data['h'])


class Skin:
    def __init__(self, data):
        self.number = data['num']
        self.id = data['id']
        self.name = data['name']


class Passive:
    def __init__(self, data):
        self.name = data['name']
        self.image = ImageInfo(data['image'])
        self.description = data['description']
        self.clean_description = data['sanitizedDescription']


class Spell:
    def __init__(self, data):
        self.name = data['name']
        self.image = ImageInfo(data['image'])
        self.tooltip = data['tooltip']
        self.clean_tooltip = data['sanitizedTooltip']
        self.description = data['description']
        self.clean_description = data['sanitizedDescription']

        self.max_rank = int(data['maxrank'])
        self.resource = data['resource']
        self.cost_type = data['costType']

        self.cooldown = data['cooldown']
        self.cost = data['cost']
        self.range = data['range']
        self.effect = data['effect']  # TODO: Maybe implement this?

        self.cd_burn = data['cooldownBurn']
        self.cost_burn = data['costBurn']
        self.range_burn = data['rangeBurn']
        self.effect_burn = data['effectBurn']

        self.level_tip = data['leveltip']  # TODO: Implement this.
        self.vars = data['vars']  # TODO: Implement this.


class Champion:
    def __init__(self, data):
        self.name = data['name']
        self.title = data['title']
        self.id = data['id']
        self.key = data['key']
        self.info = None if 'info' not in data else ChampionOverview(data['info'])
        self.enemy_tips = None if 'enemytips' not in data else data['enemytips']
        self.stats = None if 'stats' not in data else Stats(data['stats'])
        self.image = None if 'image' not in data else ImageInfo(data['image'])
        self.tags = None if 'tags' not in data else data['tags']
        self.par_type = None if 'partype' not in data else data['partype']
        self.skins = None if 'skins' not in data else [Skin(d) for d in data['skins']]
        self.passive = None if 'passive' not in data else Passive(data['passive'])
        self.recommended = None if 'recommended' not in data else data['recommended']  # TODO: Implement this.
        self.ally_tips = None if 'allytips' not in data else data['allytips']
        self.lore = None if 'lore' not in data else data['lore']
        self.blurb = None if 'blurb' not in data else data['blurb']
        self.spells = None if 'spells' not in data else [Spell(d) for d in data['spells']]


class BannedChampion:
    def __init__(self, data):
        self.team_id = data['teamId']
        self.champion_id = data['championId']
        self.pick_turn = data['pickTurn']


class Perks:
    def __init__(self, data):
        self.style = int(data['perkStyle'])
        self.ids = [int(d) for d in data['perkIds']]
        self.sub_style = int(data['perkSubStyle'])


class Participant:
    def __init__(self, data):
        self.icon_id = data['profileIconId']
        self.champion_id = data['championId']
        self.name = data['summonerName']
        self.game_customization_objects = data['gameCustomizationObjects']
        self.bot = bool(data['bot'])
        self.perks = Perks(data['perks'])
        self.spell1_id = data['spell1Id']
        self.spell2_id = data['spell2Id']
        self.team_id = data['teamId']
        self.summoner_id = data['summonerId']


class ActiveGame:
    def __init__(self, data):
        self.game_id = data['gameId']
        self.game_start_time = data['gameStartTime']
        self.platform_id = data['platformId']
        self.game_mode = data['gameMode']
        self.game_mode_name = GAME_MODES[self.game_mode]
        self.map_id = data['mapId']
        self.map_name = MAPS[self.map_id]
        self.game_type = data['gameType']
        self.game_type_name = GAME_TYPES[self.game_type]
        self.queue_id = data['gameQueueConfigId']
        self.queue_name = QUEUE_TYPES[self.queue_id]
        self.ranked_queue = RANKED_QUEUES[self.queue_id] if self.queue_id in RANKED_QUEUES else None
        self.observer_encryption_key = data['observers']['encryptionKey']
        self.participants = [Participant(p) for p in data['participants']]
        self.game_length = int(data['gameLength'])
        self.banned_champions = [BannedChampion(bc) for bc in data['bannedChampions']]
        self.full_game_type = self.game_type_name + ' ' + self.game_mode_name + ' ' \
                              + self.queue_name + ' on ' + self.map_name


class Summoner:
    def __init__(self, data):
        self.id = data['id']
        self.account_id = data['accountId']
        self.name = data['name']
        self.level = data['summonerLevel']
        self.icon_id = data['profileIconId']
        self.revision_date = data['revisionDate']
