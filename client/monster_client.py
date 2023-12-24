import json

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


class MonsterClient:
    def __init__(self, uri):
        self.client = MongoClient(uri, server_api=ServerApi('1'))
        self.database = self.client["pathfighter"]
        self.collection = self.database["monsters"]

    def aggregate_pipeline(self, pipeline):
        return self.collection.aggregate(pipeline)

    def generate_monsters_dataset(self):

        json_file_path = 'assets/monsters.json'

        print(f"Deleted {self.collection.delete_many({}).deleted_count} documents.")
        print("Initializing new collection...")

        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        for obj in data:
            obj['meta'].pop('aonId', None)
            obj['meta'].pop('aonUrl', None)
            self.collection.insert_one(obj)

        print("Monsters collection initialized.")
