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

    def getGuilds(self):
        pass

    def add_day_to_database(self):
        categoryNames= ['Guilds', 'Parties']
        excludeChannelName = 'townhall'
        guilds = [] # all channels within both guilds and parties category

        for guild in guilds:
            dailyAnalytics = None # document to be inserted
            collection = self.db[guild]
            collection.insert_one(dailyAnalytics) 

    # method designed to push into the airtable interface
    def fetch_all(self):
        # using the db.list_collection_names() instead of channel IDs because this is a purely fetch from database function
        collectionNames= self.db.list_collection_names()

        for guild in collectionNames:
            collection = self.db[guild]
            documents = collection.find({})
            for document in documents:
                pass # TODO: add a place to store all fetched docs