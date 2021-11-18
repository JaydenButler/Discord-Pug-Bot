from Managers.DatabaseManager import find_record, update_record

def update_player_elo(guildID, playerID, amount):
    server = find_record(guildID)
    i = 0
    for player in server["players"]:
        if player["id"] == playerID:
            newElo = int(player["mmr"]) + amount
            update_record(guildID, "$set", f"players.{i}.mmr", newElo)
        i = i + 1
