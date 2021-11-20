from logging import currentframe
import discord
from discord.ext import commands
from discord.ext.commands.cog import Cog
from pymongo.message import update
from Managers.QueueManager import queueManagers, VoteTypes, Vote, GAME_SIZE
from Managers.MatchManager import matchManager
from Managers.DatabaseManager import update_record, insert_record, find_record
from Managers.PlayerManager import Player
import math

class CommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def q(self, ctx: commands.Context):
        if ctx.channel.name[0:4] == "rank":
            rank = ctx.channel.name[-1].upper()
            for queueManager in queueManagers:
                if rank == queueManager.rank:
                    for player in queueManager.GetCurrentQueue().players:
                        if player.id == ctx.author.id:
                            return

                    newPlayer = Player(ctx.author.id, ctx.guild.id)

                    await queueManager.GetCurrentQueue().AddPlayer(newPlayer)

                    currentQueueSize = queueManager.GetCurrentQueue().GetQueueSize()

                    playersNeeded = GAME_SIZE - currentQueueSize

                    embed = discord.Embed(title=f"Player has joined the queue ({currentQueueSize}/{GAME_SIZE})", description=f"{ctx.author.mention} has joined the queue")
                    embed.set_footer(text=f"{playersNeeded} more players needed to pop!")

                    await ctx.reply("", embed=embed)

                    await queueManager.GetCurrentQueue().CheckQueueFull(ctx, rank)

    @commands.command()
    async def status(self, ctx):
        if ctx.channel.name[0:4] == "rank":
            rank = ctx.channel.name[-1].upper()
            for queueManager in queueManagers:
                if rank == queueManager.rank:
                    playersStr = ""
                    
                    if not queueManager.GetCurrentQueue().players:
                        playersStr = "Queue is empty"
                    else:
                        for player in queueManager.GetCurrentQueue().players:
                            playersStr += f"<@{player.id}>\n"
                    
                    playersNeeded = GAME_SIZE - queueManager.GetCurrentQueue().GetQueueSize()
                    
                    embed = discord.Embed(title="Current members in the queue", description=playersStr)
                    embed.set_footer(text=f"{playersNeeded} more players needed to pop!")
                    
                    await ctx.reply("", embed=embed)
    
    @commands.command()
    async def r(self, ctx: commands.Context):
        if ctx.channel.name[0:4] == "rank":
            rank = ctx.channel.name[-1].upper()
            for queueManager in queueManagers:
                if rank == queueManager.rank:
                    playerVoted = False
                    currentQueue = queueManager.GetCurrentQueue()
                    for player in currentQueue.players:
                        for vote in currentQueue.votes:
                            if vote.player == player:
                                playerVoted = True
                            else:
                                playerVoted = False
                        if player.id == ctx.author.id and currentQueue.inVote is True and playerVoted is False:
                            newVote = Vote(player, VoteTypes.RANDOM)
                            await ctx.message.add_reaction("✅")  
                            await currentQueue.AddVote(ctx, newVote, rank)  

    @commands.command()
    async def votes(self, ctx):
        if ctx.channel.name[0:4] == "rank":
            rank = ctx.channel.name[-1].upper()
            for queueManager in queueManagers:
                if rank == queueManager.rank:
                    votes = ""

                    voteCount = len(queueManager.GetCurrentQueue().votes)

                    for vote in queueManager.GetCurrentQueue().votes:
                        votes = votes + f"<@{vote.player.id}> voted for **`{vote.vote.name}`**\n"

                    embed = discord.Embed(title="Current votes", description=votes)
                    embed.set_footer(text=f"{voteCount}/{round(GAME_SIZE/2)} people have voted")
                    await ctx.send("", embed=embed)


    #!TODO Make this only work in score report
    @commands.command()
    async def report(self, ctx: commands.Context, matchNum, result):
        if ctx.channel.name == "score-report":
            result = result.lower()
            if matchNum.isnumeric() == False:
                await ctx.reply("Please enter the match number is digit form, eg. **`500`**")
                return
            if result != "w" and result != "l":
                await ctx.reply("Please report the result as either a W for a win, or L for a loss")
                return

            reported = matchManager.ReportMatch(ctx.guild.id, ctx.author.id, int(matchNum), result)
            
            if reported == True:
                await ctx.message.add_reaction("✅")     
            else:
                await ctx.message.add_reaction("❌")  
    
    @commands.command()
    async def leave(self, ctx):
        if ctx.channel.name[0:4] == "rank":
            rank = ctx.channel.name[-1].upper()
            for queueManager in queueManagers:
                if rank == queueManager.rank:
                    for player in queueManager.GetCurrentQueue().players:
                        if player.id == ctx.author.id and queueManager.GetCurrentQueue().inVote == False:
                            queueManager.GetCurrentQueue().players.remove(player)

                            currentQueueSize = queueManager.GetCurrentQueue().GetQueueSize()

                            playersNeeded = GAME_SIZE - currentQueueSize

                            embed = discord.Embed(title=f"Player has left the queue ({currentQueueSize}/{GAME_SIZE})", description=f"{ctx.author.mention} has left the queue")
                            embed.set_footer(text=f"{playersNeeded} more players needed to pop!")

                            await ctx.reply("", embed=embed)

    @commands.command()
    async def leaderboard(self, ctx):
        if ctx.channel.name[0:4] == "rank":
            rank = ctx.channel.name[-1].upper()
            server = find_record(ctx.guild.id)
            for dbRank in server["ranks"]:
                if rank == dbRank["name"]:
                    playersInRank = []
                    for player in server["players"]:
                        if player["rank"] == rank:
                            playersInRank.append(player)
                    playersInRank.sort(key=lambda x: x["mmr"], reverse=True) 
                    message = ""
                    pagesNeeded = math.ceil(len(playersInRank) / 20) 
                    currentPage = 1
                    i = 1
                    lastPage = False
                    for player in playersInRank:
                        message = message + f"{i}. <@{player['id']}> - {round(player['mmr'])}\n"
                        if i % 20 == 0:
                            embed = discord.Embed(title=f"Leaderboard for Rank {rank}", description=message)
                            embed.set_footer(text=f"Page ({currentPage}/{pagesNeeded})")
                            await ctx.send("", embed = embed)
                            currentPage = currentPage + 1
                            message = ""
                        else:
                            lastPage = True
                        i = i + 1
                    
                    if lastPage == True:
                        embed = discord.Embed(title=f"Leaderboard for Rank {rank}", description=message)
                        embed.set_footer(text=f"Page ({currentPage}/{pagesNeeded})")
                        await ctx.send("", embed = embed)
        

def setup(bot):
    bot.add_cog(CommandsCog(bot))