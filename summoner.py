import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from dataclasses import dataclass
from typing import Optional
import requests

@dataclass
class RerollPoints:
    current_points: int
    max_rolls: int
    number_of_rolls: int
    points_cost_to_roll: int
    points_to_reroll: int

@dataclass
class Summoner:
    account_id: int
    display_name: str
    game_name: str
    internal_name: str
    name_change_flag: bool
    percent_complete_for_next_level: int
    privacy: str
    profile_icon_id: int
    puuid: str
    reroll_points: RerollPoints
    summoner_id: int
    summoner_level: int
    tag_line: str
    unnamed: bool
    xp_since_last_level: int
    xp_until_next_level: int

    @classmethod
    def from_dict(cls, data: dict) -> 'Summoner':
        return cls(
            account_id=data['accountId'],
            display_name=data['displayName'],
            game_name=data['gameName'],
            internal_name=data['internalName'],
            name_change_flag=data['nameChangeFlag'],
            percent_complete_for_next_level=data['percentCompleteForNextLevel'],
            privacy=data['privacy'],
            profile_icon_id=data['profileIconId'],
            puuid=data['puuid'],
            reroll_points=RerollPoints(
                current_points=data['rerollPoints']['currentPoints'],
                max_rolls=data['rerollPoints']['maxRolls'],
                number_of_rolls=data['rerollPoints']['numberOfRolls'],
                points_cost_to_roll=data['rerollPoints']['pointsCostToRoll'],
                points_to_reroll=data['rerollPoints']['pointsToReroll']
            ),
            summoner_id=data['summonerId'],
            summoner_level=data['summonerLevel'],
            tag_line=data['tagLine'],
            unnamed=data['unnamed'],
            xp_since_last_level=data['xpSinceLastLevel'],
            xp_until_next_level=data['xpUntilNextLevel']
        )

    @classmethod
    def get_current_summoner(cls, auth_info: dict) -> 'Summoner':
        try:
            response = requests.get(
                f"{auth_info['url']}/lol-summoner/v1/current-summoner",
                headers={"Authorization": f"Basic {auth_info['basic_token']}"},
                verify=False
            )
            if response.status_code == 200:
                summoner_data = response.json()
                return cls.from_dict(summoner_data)
            else:
                print(f"Error fetching current summoner: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error fetching current summoner: {e}")
            return None