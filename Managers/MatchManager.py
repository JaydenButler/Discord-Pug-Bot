import json
global matchManager

class MatchManager():
    def ReportMatch(self, id, matchNum, result):
        matchSaved = False
        savedMatches = self.GetMatchJson()
        
        for match in savedMatches["matches"]:
            if match["matchNum"] == matchNum:
                if match["reported"] is False:
                    for team in match["teams"]:
                        for player in team["playerData"]["players"]:
                            if player["id"] == id:
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
                                match["reportedBy"] = id
                                self.SaveMatchJson(savedMatches)
                                matchSaved = True
        
        return matchSaved
                                    
    def GetMatch(self, matchNum):
        savedMatches = self.GetMatchJson()
        for match in savedMatches["matches"]:
            if match["matchNum"] == matchNum:
                return match

    def SwapResult(self, matchNum):
        matchSaved = False
        savedMatches = self.GetMatchJson()
        
        for match in savedMatches["matches"]:
            if match["matchNum"] == matchNum:
                if match["winner"] == 1:
                    match["winner"] = 2
                elif match["winner"] == 2:
                    match["winner"] = 1
                elif match["winner"] == None:
                    matchSaved = False
                self.SaveMatchJson(savedMatches)
                matchSaved = True
        
        return matchSaved
        
    def GetMatchJson(self):
         with open("matches.json") as f:
            return json.load(f)

    def SaveMatchJson(self, data):
        with open('matches.json', 'w') as f:
            json.dump(data, f)

class Match():
    def __init__(self, teamOne, teamTwo):
        self.teamOne = teamOne
        self.teamTwo = teamTwo
        self.matchNum = 69420
        self.reported = False
        self.winner = None
        self.reportedBy = None

    def ReportWinner(self, winningTeam):
        self.reported = True
        self.winner = winningTeam

    def SaveMatch(self):
        with open("matches.json") as f:
            savedMatches = json.load(f)
            self.matchNum = len(savedMatches["matches"]) + 1
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
            savedMatches["matches"].append(newMatchJSON)
            self.matchManager.SaveMatchJson(savedMatches)
            return self

matchManager = MatchManager()