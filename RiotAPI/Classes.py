
class Summoner:

    # CONSTRUCTOR
    def __init__(self, summ_json):
        """
        :members:
            string      name        //code-name of the summoner
            string      idealized   //display-name of the summoner
            int         id          //indexable id of the summoner
            int         icon        //id of the icon for this summoner
            int         level       //summoner level of this summoner
        """

        self.exists = True
        self.name = summ_json['name']
        self.id = summ_json['id']
        self.icon = summ_json['profileIconId']
        self.level = summ_json['summonerLevel']


class ChampionMastery:

    # CONSTRUCTOR
    def __init__(self, champ_mastery_json):
        """
        :members:
            int         id              //id of the champion
            int         points          //total amount of champ mastery points
            int         pts_next_level  //points to get to the next level for this champ
            int         pts_last_level  //points gained since leveling up last
            int         level           //level of this champion
            bool        chest           //has gotten a chest with this champ
        """

        self.id = champ_mastery_json['championId']
        self.points = champ_mastery_json['championPoints']
        self.pts_next_level = champ_mastery_json['championPointsUntilNextLevel']
        self.pts_last_level = champ_mastery_json['championPointsSinceLastLevel']
        self.level = champ_mastery_json['championLevel']
        self.chest = champ_mastery_json['chestGranted']


class Champion:

    # CONSTRUCTOR
    def __init__(self, champion_json):
        """
        :members:
            string      name        //code-name of the champ
            string      idealized   //display name for the champion
            int         id          //code-id of the champ
            string      title       //champion's title
        """

        self.id = champion_json['id']
        self.name = champion_json['key']
        self.idealized = champion_json['name']
        self.title = champion_json['title']


class InGameSummoner:

    # CONSTRUCTOR
    def __init__(self):
        self.name = ''
        self.champ_id = 0
        self.team = 0
        self.summoner = None
        self.champion = None

        self.rank = ''
        self.lp = ''
        self.series = ''

        self.games_champ = 0
        self.win_rate_champ = 0
        self.kda_champ = 0.00

        self.games = 0
        self.win_rate = 0
        self.kda = 0
