from Managers.DatabaseManager import update_record, find_record, report_existing_match
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
        matchSaved = True
        savedMatches = self.GetMatchInfo(guildId)
        
        for match in savedMatches:
            if match["matchNum"] == matchNum:
                if match["winner"] == 1:
                    match["winner"] = 2
                elif match["winner"] == 2:
                    match["winner"] = 1
                elif match["winner"] == None:
                    matchSaved = False
                self.SaveMatchInfo(guildId, match)

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