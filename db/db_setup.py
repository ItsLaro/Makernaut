import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from dotenv import load_dotenv
from datetime import datetime

Base = declarative_base()
load_dotenv()

class GuildStateEnum(Enum):
    """
    Enum for the guild state
    """
    NEW = "NEW"
    PROMOTED = "PROMOTED"
    DEMOTED = "DEMOTED"

class Guild(Base):
    """
    MySQl table for the guilds
    """
    __tablename__ = 'guilds'

    channel_id = Column(Integer, primary_key=True, autoincrement=False)
    forum_post_id = Column(Integer)
    level = Column(Integer)
    guild_state = Column(Enum(GuildStateEnum))

    messages = relationship("MessageMetadata", back_populates="guilds")

class MessageMetadata(Base):
    """
    MySQl table for the messages
    """
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    message_location_id = Column(Integer)
    message_location_type = Column(String)
    user_id = Column(Integer)

    channel_id = Column(Integer, ForeignKey('Guilds.channel_id'))
    guild = relationship("Guild", back_populates="messages")

SQL_SERVER = os.getenv("SQL_SERVER")
SQL_DATABASE = os.getenv("SQL_DATABASE")
SQL_USER = os.getenv("SQL_USER")
SQL_PASS = os.getenv("SQL_PASS")

DATABASE_URL = f"mysql+pymysql://{SQL_USER}:{SQL_PASS}@{SQL_SERVER}/{SQL_DATABASE}"

# Initialize database
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
