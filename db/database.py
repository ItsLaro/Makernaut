import os
import pyodbc
from loguru import logger
from dotenv import load_dotenv
from typing import List, Optional, Dict
from ..models.guild import MessageMetadata, Guild, GuildState
from contextlib import contextmanager

load_dotenv()
class Database:
    """
    Class that handles all database interactions.
    """
    @contextmanager
    def _db_connection(self):
        """
        Establish a connection to SQL and yield a cursor for executing queries.

        Yields:
            pyodbc.Cursor: A cursor for executing SQL commands

        Raises:
            pyodbc.DatabaseError: If an error occurs while executing SQL commands
        """
        conn_str = (
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={os.getenv("SQL_SERVER")};'
            f'DATABASE={os.getenv("SQL_DATABASE")};'
            f'UID={os.getenv("SQL_USER")};'
            f'PWD={os.getenv("SQL_PASS")}'
        )

        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        try:
            yield cursor
        except pyodbc.DatabaseError as error:
            logger.error(
                f'Failed connecting to database | Error: {error}'
            )
        finally:
            conn.commit()
            conn.close()

    def execute_query(self, query, params=None) -> pyodbc.Cursor:
        """
        Execute a query and return the cursor.

        Args:
            query (str): The SQL query to execute
            params (Tuple[Any]): The parameters to pass to the query

        Returns:
            pyodbc.Cursor: A cursor for executing SQL commands
        """
        with self._db_connection() as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()

    def set_guild(self, new_guild: Guild) -> None:
        """
        Adds a new channel to the guilds table in SQL.

        Args:
            new_guild (TrackedChannel): A type representing the new channel. 
        """
        try:
            query = '''
                    INSERT INTO 
                        guilds (channel_id, guild_name) 
                        VALUES (?, ?)
                    '''
            params = (new_guild.channel_id, new_guild.guild_name)
            with self._db_connection() as cursor:
                cursor.execute(query, params)
                cursor.commit()

            logger.success(
                f'''{self.set_guild.__name__} executed 
                successfully for channel_id: {new_guild.channel_id}'''
            )
        except pyodbc.DatabaseError as error:
            logger.error(
                f'{self.set_guild.__name__} executed with an error: {error}'
            )

    def set_message(
            self,
            channel_id: str,
            channel_type: str,
            new_message: MessageMetadata
        ) -> None:
        """
        Adds a new message to the messages table in SQL.

        Args:
            new_message (MessageMetadata): A type representing the new message.
        """
        try:
            query = '''
                    INSERT INTO
                        messages 
                            (channel_id, 
                            channel_type, 
                            timestamp,
                            message_location_id, 
                            message_location_type, 
                            user_id) 
                            VALUES (?, ?, ?, ?, ?, ?)
                    '''
            params = (channel_id,
                      channel_type,
                      new_message["timestamp"],
                      new_message["message_location_id"],
                      new_message["message_location_type"],
                      new_message["user_id"]
                    )
            self.execute_query(query, params)
            logger.success(
                f'''{self.set_message.__name__} executed successfully
                for channel_id, message_id: [{channel_id}]'''
            )
        except pyodbc.DatabaseError as error:
            logger.error(
                f'{self.set_message.__name__} executed with an error: {error}'
            )

    def get_all_guilds(self) -> List[Guild]:
        """
        Retrieves all guilds from the guilds table in SQL.

        Returns:
            guilds (List[Guild]): a list of all guilds stored in SQL,
                each guild is represented as a Guild object
        """
        try:
            query = '''
                    SELECT
                        * 
                    FROM 
                        guilds
                    '''
            cursor = self.execute_query(query)
            rows = cursor.fetchall()
            guilds: List[Guild] = [
                {
                    'channel_id': row.channel_id,
                    'forum_post_id': row.forum_post_id,
                    'level': row.level,
                    'guild_state': GuildState(row.guild_state)
                }
                for row in rows
            ]
            logger.success(
                f'{self.get_all_guilds.__name__} executed successfully!'
            )
            return guilds
        except pyodbc.DatabaseError as error:
            logger.error(
                f'{self.get_all_guilds.__name__} executed with an error: {error}'
            )

    def set_state(self, channel_id: int, state: GuildState) -> Optional[Guild]:
        """
        Set the state of a guild.

        Args:
            channel_id (int): integer representing the id of the channel
            state (GuildState): Enum representing the new state of the guild

        Returns:
            guild (Guild): an object of the guild modified
        """
        try:
            update_query = '''
                            UPDATE 
                                guilds 
                            SET 
                                guild_state = ? 
                            WHERE 
                                channel_id = ?
                            '''

            self.execute_query(update_query, (state.value, channel_id))

            select_query = "SELECT * FROM guilds WHERE channel_id = ?"

            cursor = self.execute_query(select_query, (channel_id,))

            row = cursor.fetchone()
            if not row:
                logger.error(f"No guild found with channel_id: {channel_id}")
                return None

            updated_guild = {
                'channel_id': row.channel_id,
                'forum_post_id': row.forum_post_id,
                'level': row.level,
                'guild_state': GuildState(row.guild_state)
            }

            logger.success(
                f'''{self.set_state.__name__} executed 
                successfully for channel_id: {channel_id}'''
            )
            return updated_guild

        except pyodbc.DatabaseError as error:
            logger.error(f'{self.set_state.__name__} executed with an error: {error}')
            return None

    def get_message_data_per_week_by_guild(self) -> List[Dict[str, int]]:
        """
        Fetches the number of messages sent in each guild every week.

        Returns:
            List[Dict[str, int]]: A list of dictionaries, each containing
            the guild ID, and the count of messages for each week.
        """
        try:
            query = '''
                SELECT
                    channel_id,
                    DATEPART(week, timestamp) as week,
                    COUNT(*) as message_count
                FROM
                    messages
                GROUP BY
                    channel_id,
                    DATEPART(week, timestamp)
                ORDER BY
                    channel_id,
                    DATEPART(week, timestamp)
            '''
            rows = self.execute_query(query)
            message_data_per_week: List[Dict[str, int]] = [
                {
                    'channel_id': row.channel_id,
                    'week': row.week,
                    'message_count': row.message_count
                }
                for row in rows
            ]
            logger.success(
                f'''{self.get_message_data_per_week_by_guild.__name__} 
                executed successfully!'''
            )
            return message_data_per_week
        except pyodbc.DatabaseError as error:
            logger.error(
                f'''{self.get_message_data_per_week_by_guild.__name__} 
                executed with an error: {error}'''
            )
            return []
    def get_unique_users_by_week_by_guild(self) -> List[Dict[str, int]]:
        """
        Fetches the count of unique users who sent a message by week by guild.

        Returns:
            List[Dict[str, int]]: A list of dictionaries containing the guild id, week starting date, 
                                   and the count of unique users for that week.
        """
        try:
            query = """
                    SELECT 
                        guild_id, 
                        DATEPART(wk, timestamp) as week_number, 
                        COUNT(DISTINCT user_id) as unique_users
                    FROM 
                        messages
                    GROUP BY 
                        guild_id, 
                        DATEPART(wk, timestamp)
                    ORDER BY 
                        guild_id, 
                        week_number
                    """
            
            cursor = self.execute_query(query)
            rows = cursor.fetchall()
            result = [
                {
                    'guild_id': row.guild_id,
                    'week_number': row.week_number,
                    'unique_users': row.unique_users
                }
                for row in rows
            ]
            logger.success(
                f'''{self.get_unique_users_by_week_by_guild.__name__} 
                executed successfully!'''
            )
            return result
        except pyodbc.DatabaseError as error:
            logger.error(
                f'''{self.get_unique_users_by_week_by_guild.__name__} 
                executed with an error: {error}'''
            )
            return []
