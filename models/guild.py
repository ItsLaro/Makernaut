from typing import TypedDict
from datetime import datetime
from enum import Enum

class GuildState(Enum):
    """
    Enum for the guild state
    """
    NEW = "NEW"
    PROMOTED = "PROMOTED"
    DEMOTED = "DEMOTED"

class MessageMetadata(TypedDict):
    """
    MessageMetadata model for the database
    """
    timestamp: datetime
    message_location_id: int
    message_location_type: str
    user_id: int

class Guild(TypedDict):
    """
    Guild model for the database
    """
    channel_id: int
    forum_post_id: int
    level: int
    guild_state: GuildState
