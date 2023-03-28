from pymongo import MongoClient

class DataSchema:
    def __init__(self) -> None:
        pass                                                 

class Database:

    def __init__(self) -> None:
        uri = "" # TODO: Figure out URI
        databaseName = ""
        self.client = MongoClient(uri)  # MongoDB Client
        self.db = self.client[databaseName]

    def add_day_to_database(self, channelID):
        raw_data = None  # Calls function from analytics.py to get the data
        