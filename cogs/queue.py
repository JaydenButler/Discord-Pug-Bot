import asyncio
import random
import discord
from discord.ext import commands
from enum import Enum

global queueManager
GAME_SIZE = 2

class Player():
    def __init__(self, discordID):
        self.id = discordID

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

        await self.PostQueue(ctx, [teamOne, teamTwo])
        

    async def PostQueueTypeVote(self, ctx):
        self.inVote = True
        print("Posting the queue type vote")
        embed = discord.Embed(title="Please vote on the queue type below!")
        embed.add_field(name="Balanced", value="```!b```", inline=True)
        embed.add_field(name="Captains", value="```!c```", inline=True)
        embed.add_field(name="Random", value="```!r```", inline=True)
        await ctx.send("", embed=embed)


    async def PostQueue(self, ctx: commands.Context, teams):
        teamOnePlayersStr = ""
        for player in teams[0].GetPlayers():
            teamOnePlayersStr += f"<@{player.id}>\n"

        teamTwoPlayersStr = ""
        for player in teams[1].GetPlayers():
            teamTwoPlayersStr += f"<@{player.id}>\n"

        embed = discord.Embed(title="The queue has popped!")
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

    def DeleteQueue(self):
        self.currentQueue = Queue()

    def BackupQueue():
        raise NotImplementedError

class Match():
    def __init__(self, teamOne, teamTwo):
        self.teamOne = teamOne
        self.teamTwo = teamTwo
        self.MatchNum = 1
        self.reported = False
        self.winner = None

    def ReportWinner(self, winningTeam):
        self.reported = True
        self.winner = winningTeam

class Team():
    def __init__(self):
        self.players = []

    def AddPlayer(self, player):
        self.players.append(player)

    def GetPlayers(self):
        return self.players

class Vote():
    def __init__(self, player, vote):
        self.player = player
        self.vote = vote

class VoteTypes(Enum):
    RANDOM = "r"
    BALANCED = "b"
    CAPTAINS = "c"

queueManager = QueueManager()