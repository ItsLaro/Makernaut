from dataclasses import dataclass


"""
this is all time guild stats
"""
@dataclass
class Guild:
    guild_level: int
    average_dau: float
    average_wau: float
    average_num_messages_all_time: float
    average_num_messages_daily: float
    average_num_messages_weekly: float
    most_active_users: list(str)
    