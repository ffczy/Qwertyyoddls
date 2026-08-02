from dataclasses import dataclass


@dataclass(frozen=True)
class FightSettings:
    # Health
    starting_health: int
    max_health: int
    starting_shield: int
    max_shield: int

    # Match
    rounds_to_win: int
    max_rounds: int
    cards_to_claim: int

    # Requirements
    minimum_cards_required: int
    minimum_level_required: int
    minimum_coins_required: int

    # Timers
    challenge_timeout: int
    turn_timeout: int
    inactivity_timeout: int
    round_start_delay: int

    # Turns
    random_first_turn: bool
    allow_skip_turn: bool
    allow_extra_turn: bool

    # Battle
    restore_health_each_round: bool
    restore_shield_each_round: bool
    restore_effects_each_round: bool

    # Cards
    consume_card_after_use: bool
    allow_duplicate_cards: bool
    allow_card_reuse: bool
    max_card_uses: int
    max_cards_per_turn: int

    # Effects
    max_active_effects: int
    default_effect_duration: int
    allow_effect_stack: bool

    # Fight Rules
    allow_private_fights: bool
    allow_group_fights: bool
    allow_surrender: bool
    allow_escape: bool
    allow_draw: bool

    # Limits
    max_active_fights: int
    max_daily_fights: int

    # Rewards
    winner_coins: int
    loser_coins: int
    winner_rank_points: int
    loser_rank_points: int

    # Statistics
    save_fight_history: bool
    save_statistics: bool
    save_card_usage: bool
    save_damage_log: bool

    # Ranking
    enable_ranking: bool
    enable_leaderboard: bool

    # Logs
    enable_logs: bool
    debug_mode: bool


DEFAULT_FIGHT_SETTINGS = FightSettings(
    # Health
    starting_health=2000,
    max_health=2000,
    starting_shield=0,
    max_shield=500,

    # Match
    rounds_to_win=3,
    max_rounds=5,
    cards_to_claim=3,

    # Requirements
    minimum_cards_required=3,
    minimum_level_required=0,
    minimum_coins_required=0,

    # Timers
    challenge_timeout=180,
    turn_timeout=60,
    inactivity_timeout=180,
    round_start_delay=5,

    # Turns
    random_first_turn=True,
    allow_skip_turn=False,
    allow_extra_turn=True,

    # Battle
    restore_health_each_round=True,
    restore_shield_each_round=True,
    restore_effects_each_round=False,

    # Cards
    consume_card_after_use=False,
    allow_duplicate_cards=True,
    allow_card_reuse=True,
    max_card_uses=999,
    max_cards_per_turn=1,

    # Effects
    max_active_effects=20,
    default_effect_duration=3,
    allow_effect_stack=True,

    # Fight Rules
    allow_private_fights=True,
    allow_group_fights=True,
    allow_surrender=True,
    allow_escape=False,
    allow_draw=False,

    # Limits
    max_active_fights=1,
    max_daily_fights=100,

    # Rewards
    winner_coins=250,
    loser_coins=50,
    winner_rank_points=25,
    loser_rank_points=-10,

    # Statistics
    save_fight_history=True,
    save_statistics=True,
    save_card_usage=True,
    save_damage_log=True,

    # Ranking
    enable_ranking=True,
    enable_leaderboard=True,

    # Logs
    enable_logs=True,
    debug_mode=False,
)
