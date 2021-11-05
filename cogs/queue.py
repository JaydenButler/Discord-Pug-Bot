import json
import random
import discord
from discord.ext import commands
from enum import Enum

global queueManager
global matchManager
GAME_SIZE = 2

class Player():
    def __init__(self, discordID):
        self.id = discordID

    def dump(self):
        data = {
            "id": self.id
        }
        return data

class Queue():
    def __init__(self):
        self.players = []
        self.inVote = False
        self.votes = []
        self.votesNeeded = GAME_SIZE #In the future change this to half the queue size
    
    async def AddVote(self, ctx, vote):
        self.votes.append(vote)
        if len(self.votes) == self.votesNeeded:
            await self.DoRandomTeamSelection(ctx)
    
    async def AddPlayer(self, player):
        self.players.append(player)

    def RemovePlayer(self, player):
        self.players.remove(player)  

    def GetQueueSize(self):
        if not self.players:
            return 0;
        else:
            return len(self.players)
    
    async def CheckQueueFull(self, ctx):
        if(self.GetQueueSize() == GAME_SIZE):
            await queueManager.GetCurrentQueue().PostQueueTypeVote(ctx)

    #Send this match info to the database
    async def DoRandomTeamSelection(self, ctx: commands.Context):
        print("A queue has popped!")

        playersToAdd = self.GetQueueSize() - 1

        teamOne = Team()
        teamTwo = Team()

        lastTeamAdded = 2;

        while playersToAdd >= 0:
            num = random.randint(0, playersToAdd)
            
            currentPlayer = self.players[num]
            
            if lastTeamAdded == 2:
                teamOne.AddPlayer(currentPlayer)
                self.RemovePlayer(currentPlayer)
                lastTeamAdded = 1
            elif lastTeamAdded == 1:
                teamTwo.AddPlayer(currentPlayer)
                self.RemovePlayer(currentPlayer)
                lastTeamAdded = 2

            playersToAdd -= 1

        newMatch = Match(teamOne, teamTwo)

        newMatch = newMatch.SaveMatch()

        queueManager.CreateNewQueue()

        await self.PostQueue(ctx, newMatch)
        

    async def PostQueueTypeVote(self, ctx):
        self.inVote = True
        print("Posting the queue type vote")
        embed = discord.Embed(title="Please vote on the queue type below!")
        embed.add_field(name="Balanced", value="```!b```", inline=True)
        embed.add_field(name="Captains", value="```!c```", inline=True)
        embed.add_field(name="Random", value="```!r```", inline=True)
        await ctx.send("", embed=embed)


    async def PostQueue(self, ctx: commands.Context, match):
        teamOnePlayersStr = ""
        for player in match.teamOne.GetPlayers():
            teamOnePlayersStr += f"<@{player.id}>\n"

        teamTwoPlayersStr = ""
        for player in match.teamTwo.GetPlayers():
            teamTwoPlayersStr += f"<@{player.id}>\n"

        embed = discord.Embed(title=f"Match {match.matchNum} is ready!")
        embed.add_field(name="Team 1", value=teamOnePlayersStr, inline=True)
        embed.add_field(name="Team 2", value=teamTwoPlayersStr, inline=True)

        await ctx.send("", embed=embed)

class QueueManager():
    def __init__(self):
        self.currentQueue = Queue()

    def GetCurrentQueue(self):
        return self.currentQueue

    def CreateNewQueue(self):
        self.currentQueue = Queue()

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
            matchManager.SaveMatchJson(savedMatches)
            return self

class Team():
    def __init__(self):
        self.players = []

    def AddPlayer(self, player):
        self.players.append(player)

    def GetPlayers(self):
        return self.players

    def dump(self):
        data = {
            "players": []
        }
        for player in self.GetPlayers():
            data["players"].append(player.dump())
        return data

class Vote():
    def __init__(self, player, vote):
        self.player = player
        self.vote = vote

class VoteTypes(Enum):
    RANDOM = "r"
    BALANCED = "b"
    CAPTAINS = "c"

queueManager = QueueManager()
matchManager = MatchManager()