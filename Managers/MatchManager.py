from Managers.DatabaseManager import update_record, find_record, report_existing_match
from Managers.EloManager import get_expected_score, get_expected_score_per_player, get_loss_elo_change, get_win_elo_change
from Managers.PlayerManager import update_player_elo
global matchManager

class MatchManager():
    def ReportMatch(self, guildId, playerId, matchNum, result):
        matchSaved = False
        savedMatches = self.GetMatchInfo(guildId)
        
        for match in savedMatches:
            if match["matchNum"] == matchNum:
                if match["reported"] is False:
                    for team in match["teams"]:
                        for player in team["playerData"]["players"]:
                            if player["id"] == playerId:
                                if result == "w":
                                    match["winner"] = team["teamNum"]
                                    match["reported"] = True
                                if result == "l":
                                    if team["teamNum"] == 1:
                                        match["winner"] = 2
                                        match["reported"] = True
                                    elif team["teamNum"] == 2:
                                        match["winner"] = 1
                                        match["reported"] = True
                                match["reportedBy"] = playerId

                                #!MAKE THIS AVG
                                teamOneMMR = 0
                                for player in match["teams"][0]["playerData"]["players"]:
                                    teamOneMMR = teamOneMMR + int(player["mmr"])
                                teamOneMMR = teamOneMMR / 3

                                #!MAKE THIS AVG
                                teamTwoMMR = 0
                                for player in match["teams"][1]["playerData"]["players"]:
                                    teamTwoMMR = teamTwoMMR + int(player["mmr"])
                                teamTwoMMR = teamTwoMMR / 3
                                
                                if match["winner"] == 1:
                                    #For the winning team
                                    for player in match["teams"][0]["playerData"]["players"]:
                                        playerWinChance = get_expected_score_per_player(player["mmr"], teamTwoMMR)
                                        amount = get_win_elo_change(playerWinChance)
                                        update_player_elo(guildId, player["id"], amount)
                                    
                                    #For the losing team
                                    for player in match["teams"][1]["playerData"]["players"]:
                                        playerWinChance = get_expected_score_per_player(player["mmr"], teamOneMMR)
                                        amount = get_loss_elo_change(playerWinChance)
                                        update_player_elo(guildId, player["id"], amount)

                                elif match["winner"] == 2:
                                    #For the winning team
                                    for player in match["teams"][0]["playerData"]["players"]:
                                        playerWinChance = get_expected_score_per_player(player["mmr"], teamOneMMR)
                                        amount = get_loss_elo_change(playerWinChance)
                                        update_player_elo(guildId, player["id"], amount)
                                    
                                    #For the losing team
                                    for player in match["teams"][1]["playerData"]["players"]:
                                        playerWinChance = get_expected_score_per_player(player["mmr"], teamTwoMMR)
                                        amount = get_win_elo_change(playerWinChance)
                                        update_player_elo(guildId, player["id"], amount)


                                report_existing_match(guildId, match)
                                matchSaved = True
        
        return matchSaved
                                    
    # def GetMatch(self, matchNum):
    #     savedMatches = self.GetMatchJson()
    #     for match in savedMatches["matches"]:
    #         if match["matchNum"] == matchNum:
    #             return match

    #TODO: Update to work with database
    def SwapResult(self, guildId, matchNum):
        matchSaved = False
        savedMatches = self.GetMatchInfo(guildId)
        i = 0
        for match in savedMatches:
            if match["matchNum"] == matchNum:
                winner = None
                if match["winner"] == 1:
                    winner = 2
                    matchSaved = True
                elif match["winner"] == 2:
                    winner = 1
                    matchSaved = True

                if matchSaved == True:
                    #!MAKE THIS AVG
                    teamOneMMR = 0
                    for player in match["teams"][0]["playerData"]["players"]:
                        teamOneMMR = teamOneMMR + int(player["mmr"])

                    #!MAKE THIS AVG
                    teamTwoMMR = 0
                    for player in match["teams"][1]["playerData"]["players"]:
                        teamTwoMMR = teamTwoMMR + int(player["mmr"])
                    
                    if winner == 1:
                        #For the winning team
                        for player in match["teams"][0]["playerData"]["players"]:
                            playerWinChance = get_expected_score_per_player(player["mmr"], teamTwoMMR)
                            amount = get_win_elo_change(playerWinChance) * 2
                            update_player_elo(guildId, player["id"], amount)
                        
                        #For the losing team
                        for player in match["teams"][1]["playerData"]["players"]:
                            playerWinChance = get_expected_score_per_player(player["mmr"], teamOneMMR)
                            amount = get_loss_elo_change(playerWinChance) * 2
                            update_player_elo(guildId, player["id"], amount)

                    elif winner == 2:
                        #For the winning team
                        for player in match["teams"][0]["playerData"]["players"]:
                            playerWinChance = get_expected_score_per_player(player["mmr"], teamOneMMR)
                            amount = get_loss_elo_change(playerWinChance) * 2
                            update_player_elo(guildId, player["id"], amount)
                        
                        #For the losing team
                        for player in match["teams"][1]["playerData"]["players"]:
                            playerWinChance = get_expected_score_per_player(player["mmr"], teamTwoMMR)
                            amount = get_win_elo_change(playerWinChance) * 2
                            update_player_elo(guildId, player["id"], amount)
                    
                update_record(guildId, "$set", f"matches.{i}.winner", winner)
            i = i + 1

        return matchSaved
        
    #TODO: Change GetMatchInfo to GetMatchesInfo and create a GetMatchInfo method that does what is says
    def GetMatchInfo(self, guildId):
        serverInfo = find_record(guildId)
        return serverInfo["matches"]

    def SaveMatchInfo(self, guildId, data):
        update_record(guildId, "$push", "matches", data)

class Match():
    def __init__(self, teamOne, teamTwo):
        self.teamOne = teamOne
        self.teamTwo = teamTwo
        self.matchNum = 69420
        self.reported = False
        self.winner = None
        self.reportedBy = None

    def SaveMatch(self, guildId):
        savedMatches = matchManager.GetMatchInfo(guildId)
        self.matchNum = len(savedMatches) + 1
        newMatchJSON = {
            "teams": [
                {
                    "teamNum": 1, 
                    "playerData": self.teamOne.dump()
                },
                {
                    "teamNum": 2,
                        "playerData": self.teamTwo.dump()
                }
            ],
            "matchNum": self.matchNum,
            "reported": False,
            "winner": None,
            "reportedBy": self.reportedBy
        }
        matchManager.SaveMatchInfo(guildId, newMatchJSON)
        return self

matchManager = MatchManager()