from Managers.DatabaseManager import find_record, update_record
from datetime import datetime, timedelta

def update_player_elo(guildID, playerID, amount):
    server = find_record(guildID)
    i = 0
    for player in server["players"]:
        if player["id"] == playerID:
            newElo = int(player["mmr"]) + amount
            update_record(guildID, "$set", f"players.{i}.mmr", newElo)
        i = i + 1

class Player():
    def __init__(self, discordID, guildID, queueLength):
        self.id = discordID
        self.mmr = 0,
        self.rank = None
        self.timeQueued = datetime.now()
        self.queueLengthTime = queueLength

        server = find_record(guildID)
        for player in server["players"]:
            if player["id"] == discordID:
                self.mmr = player["mmr"]
                self.rank = player["rank"]


    def dump(self):
        data = {
            "id": self.id,
            "mmr": self.mmr,
            "rank": self.rank,
        }
        return data
