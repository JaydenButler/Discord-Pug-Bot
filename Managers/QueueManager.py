import random
import discord
from discord.ext import commands
from enum import Enum
from Managers.DatabaseManager import find_record
from Managers.MatchManager import Match
from Managers.EloManager import get_expected_score

global queueManager
GAME_SIZE = 2

class Player():
    def __init__(self, discordID, guildID):
        self.id = discordID
        self.mmr = 0,
        self.rank = None
        server = find_record(guildID)
        for player in server["players"]:
            if player["id"] == discordID:
                self.mmr = player["mmr"]
                self.rank = player["rank"]


    def dump(self):
        data = {
            "id": self.id,
            "mmr": self.mmr,
            "rank": self.rank
        }
        return data

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

        newMatch = newMatch.SaveMatch(ctx.guild.id)

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

        teamOneWinPercent = round(get_expected_score(match.teamOne, match.teamTwo) * 100)
        teamTwoWinPercent = round(100 - teamOneWinPercent)

        embed = discord.Embed(title=f"Match {match.matchNum} is ready!")
        embed.add_field(name=f"Team 1 - {teamOneWinPercent}%", value=teamOnePlayersStr, inline=True)
        embed.add_field(name=f"Team 2 - {teamTwoWinPercent}%", value=teamTwoPlayersStr, inline=True)

        await ctx.send("", embed=embed)

class QueueManager():
    def __init__(self):
        self.currentQueue = Queue()

    def GetCurrentQueue(self):
        return self.currentQueue

    def CreateNewQueue(self):
        self.currentQueue = Queue()

class Vote():
    def __init__(self, player, vote):
        self.player = player
        self.vote = vote

class VoteTypes(Enum):
    RANDOM = "r"
    BALANCED = "b"
    CAPTAINS = "c"

queueManager = QueueManager()