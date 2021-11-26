import random
import discord
from discord.ext import commands
from enum import Enum
from Managers.DatabaseManager import find_record
from Managers.MatchManager import Match
from Managers.EloManager import get_expected_score

global queueManager
GAME_SIZE = 6
GUILD_ID = 907069401507983380

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
        self.votesNeeded = GAME_SIZE / 2 #In the future change this to half the queue size
    
    async def AddVote(self, ctx, vote, rank):
        self.votes.append(vote)
        if len(self.votes) == self.votesNeeded:
            await self.DoRandomTeamSelection(ctx, rank)
    
    async def AddPlayer(self, player):
        self.players.append(player)

    def RemovePlayer(self, player):
        self.players.remove(player)  

    def GetQueueSize(self):
        if not self.players:
            return 0;
        else:
            return len(self.players)
    
    #Check if player is in another queue here
    async def CheckQueueFull(self, ctx, rank):
        if(self.GetQueueSize() == GAME_SIZE):
            for queueManager in queueManagers:
                if rank == queueManager.rank:
                    for player in queueManager.GetCurrentQueue().players:
                        for checkQueueManager in queueManagers:
                            if queueManager != checkQueueManager:
                                for checkPlayer in checkQueueManager.GetCurrentQueue().players:
                                    if player.id == checkPlayer.id:
                                        checkQueueManager.GetCurrentQueue().players.remove(checkPlayer)
                    await queueManager.GetCurrentQueue().PostQueueTypeVote(ctx)

    #Send this match info to the database
    async def DoRandomTeamSelection(self, ctx: commands.Context, rank):
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

        for queueManager in queueManagers:
            if rank == queueManager.rank:
                queueManager.CreateNewQueue()

        await self.PostQueue(ctx, newMatch)
        

    async def PostQueueTypeVote(self, ctx):
        self.inVote = True
        print("Posting the queue type vote")
        embed = discord.Embed(title="Please vote on the queue type below!", description="ONLY RANDOM TEAMS WORK AT THE MOMENT, PLEASE VOTE !r <3")
        embed.add_field(name="Balanced", value="```!b```", inline=True)
        embed.add_field(name="Captains", value="```!c```", inline=True)
        embed.add_field(name="Random", value="```!r```", inline=True)
        await ctx.send("", embed=embed)


    async def PostQueue(self, ctx: commands.Context, match):
        
        playersToPing = ""

        teamOnePlayersStr = ""
        for player in match.teamOne.GetPlayers():
            teamOnePlayersStr += f"<@{player.id}>\n"
            playersToPing += f"<@{player.id}> "

        teamTwoPlayersStr = ""
        for player in match.teamTwo.GetPlayers():
            teamTwoPlayersStr += f"<@{player.id}>\n"
            playersToPing += f"<@{player.id}> "

        teamOneWinPercent = round(get_expected_score(match.teamOne, match.teamTwo) * 100)
        teamTwoWinPercent = round(100 - teamOneWinPercent)

        embed = discord.Embed(title=f"Match {match.matchNum} is ready!")
        embed.add_field(name=f"Team 1 - {teamOneWinPercent}%", value=teamOnePlayersStr, inline=True)
        embed.add_field(name=f"Team 2 - {teamTwoWinPercent}%", value=teamTwoPlayersStr, inline=True)

        await ctx.send(playersToPing, embed=embed)

class QueueManager():
    def __init__(self, rank):
        self.currentQueue = Queue()
        self.rank = rank

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

queueManagers = []

def SetupQueueManagers():
    queueManagers.clear()

    server = find_record(GUILD_ID)

    for rank in server["ranks"]:
        newQueue = QueueManager(rank["name"])
        queueManagers.append(newQueue)

SetupQueueManagers()