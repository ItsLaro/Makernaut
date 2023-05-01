from dataclasses import dataclass


@dataclass
class Daily_Guild_Data:
    channel_id: str
    daily_active_users: int
    daily_unique_users: int
    user_data: dict(str, int)
