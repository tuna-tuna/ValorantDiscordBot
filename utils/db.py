import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv(override=True)

class DataBase():
    def __init__(self) -> None:
        self.client = MongoClient(os.environ['MONGO_URL'])
        self.db = self.client.userdata.puuid

    def register(self, author_id: str, gameid: str, gametag: str, puuid: str):
        data = {
            "gameid": gameid,
            "gametag": gametag,
            "puuid": puuid
        }
        self.db.update_one({'author_id': author_id}, {'$set': data}, upsert=True)

    def checkStats(self, author_id: str):
        userData = self.db.find_one({"author_id": author_id})
        if userData is None:
            return False, False, False
        id = userData['gameid']
        tag = userData['gametag']
        puuid = userData['puuid']
        return id, tag, puuid

    def toggelTrack(self, author_id: str, toggle: str, channel_id):
        data = {
            "trackmatch": toggle,
            "trackchannel": channel_id
        }
        self.db.update_one({'author_id': author_id}, {'$set': data}, upsert=True)
        if toggle == 'on':
            return True
        elif toggle == 'off':
            return False

    def createPuuidList(self):
        puuidList = []
        authorPuuidList = []
        for data in self.db.find():
            author_id: str = data['author_id']
            puuid: str = data['puuid']
            puuiddata = {
                "author_id": author_id,
                "puuid": puuid
            }
            puuidList.append(puuid)
            authorPuuidList.append(puuiddata.copy())
        return puuidList, authorPuuidList

    def updateUserData(self, updateList: list):
        for playerId in updateList:
            data = {
                "gameid": playerId['gameid'],
                "gametag": playerId['gametag']
            }
            self.db.update_one({'author_id': playerId['author_id']}, {'$set': data})

    def createInfoList(self):
        infoList = []
        for data in self.db.find():
            info = {
                "author_id": data["author_id"],
                "gameid": data["gameid"],
                "gametag": data["gametag"],
                "lastmatch": data["lastmatch"],
                "puuid": data["puuid"],
                "trackchannel": data["trackchannel"],
                "trackmatch": data["trackmatch"]
            }
            infoList.append(info.copy())
        return infoList
    
    def updateLastmatch(self, author_id: str, match_id: str):
        data = {
            "lastmatch": match_id
        }
        self.db.update_one({'author_id': author_id}, {'$set': data})