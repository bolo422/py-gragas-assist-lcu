from typing import List, Optional


class Action:
    def __init__(self, actor_cell_id: int, champion_id: int, completed: bool, action_id: int, 
                 is_ally_action: bool, is_in_progress: bool, action_type: str):
        self.actor_cell_id = actor_cell_id
        self.champion_id = champion_id
        self.completed = completed
        self.id = action_id
        self.is_ally_action = is_ally_action
        self.is_in_progress = is_in_progress
        self.type = action_type


class BanRevealAction(Action):
    def __init__(self, actor_cell_id: int, champion_id: int, completed: bool, action_id: int,
                 is_ally_action: bool, is_in_progress: bool):
        super().__init__(actor_cell_id, champion_id, completed, action_id, is_ally_action, is_in_progress, "ten_bans_reveal")


class Ban(Action):
    def __init__(self, actor_cell_id: int, champion_id: int, completed: bool, action_id: int,
                 is_ally_action: bool, is_in_progress: bool):
        super().__init__(actor_cell_id, champion_id, completed, action_id, is_ally_action, is_in_progress, "ban")


class Pick(Action):
    def __init__(self, actor_cell_id: int, champion_id: int, completed: bool, action_id: int,
                 is_ally_action: bool, is_in_progress: bool):
        super().__init__(actor_cell_id, champion_id, completed, action_id, is_ally_action, is_in_progress, "pick")


class Bans:
    def __init__(self, my_team_bans: List[int], their_team_bans: List[int], num_bans: int):
        self.my_team_bans = my_team_bans
        self.their_team_bans = their_team_bans
        self.num_bans = num_bans


class MucJwtDto:
    def __init__(self, channel_claim: str, domain: str, jwt: str, target_region: str):
        self.channel_claim = channel_claim
        self.domain = domain
        self.jwt = jwt
        self.target_region = target_region


class ChatDetails:
    def __init__(self, muc_jwt_dto: MucJwtDto, multi_user_chat_id: str, multi_user_chat_password: str):
        self.muc_jwt_dto = muc_jwt_dto
        self.multi_user_chat_id = multi_user_chat_id
        self.multi_user_chat_password = multi_user_chat_password


class Session:
    def __init__(self, actions: List[List[Action]], allow_battle_boost: bool, allow_duplicate_picks: bool, 
                 allow_locked_events: bool, allow_rerolling: bool, allow_skin_selection: bool, bans: Bans, 
                 bench_champions: List[int], bench_enabled: bool, boostable_skin_count: int, 
                 chat_details: ChatDetails, counter: int, game_id: int, has_simultaneous_bans: bool, 
                 has_simultaneous_picks: bool, is_custom_game: bool, is_spectating: bool, local_player_cell_id: int):
        self.actions = actions
        self.allow_battle_boost = allow_battle_boost
        self.allow_duplicate_picks = allow_duplicate_picks
        self.allow_locked_events = allow_locked_events
        self.allow_rerolling = allow_rerolling
        self.allow_skin_selection = allow_skin_selection
        self.bans = bans
        self.bench_champions = bench_champions
        self.bench_enabled = bench_enabled
        self.boostable_skin_count = boostable_skin_count
        self.chat_details = chat_details
        self.counter = counter
        self.game_id = game_id
        self.has_simultaneous_bans = has_simultaneous_bans
        self.has_simultaneous_picks = has_simultaneous_picks
        self.is_custom_game = is_custom_game
        self.is_spectating = is_spectating
        self.local_player_cell_id = local_player_cell_id
