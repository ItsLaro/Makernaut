from dataclasses import dataclass


"""
Every week, this updates
"""


@dataclass
class WeeklyDatapoint:
    channel_id: str
    weekly_active_users: int
    weekly_unique_users: int
    user_data: dict(str, int)
