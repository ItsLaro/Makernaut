class DataSchema:
    def __init__(self) -> None:
        pass


class Database:

    def __init__(self) -> None:
        self.client = None  # MongoDB Client

    def add_day_to_database(channelID):
        raw_data = None  # Calls function from analytics.py to get the data
