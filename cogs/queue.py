import asyncio
import random
import discord
from discord.ext import commands

global queueManager
GAME_SIZE = 2

class Player():
    def __init__(self, discordID):
        self.id = discordID

class Queue():
    def __init__(self):
        self.players = []
    
    async def AddPlayer(self, ctx, player):
        self.players.append(player)
        if(self.GetQueueSize == GAME_SIZE):
            asyncio.sleep(1)
            await queueManager.GetCurrentQueue().DoQueuePop(ctx=ctx)

    def RemovePlayer(self, player):
        self.players.remove(player)  

    def GetQueueSize(self):
        if not self.players:
            return 0;
        else:
            return len(self.players)

    async def DoQueuePop(self, ctx: commands.Context):
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

        await ctx.reply("", embed=embed)

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

queueManager = QueueManager()