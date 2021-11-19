import discord
from discord.ext import commands
from discord.ext.commands.cog import Cog
from pymongo.message import update
from Managers.QueueManager import queueManager, VoteTypes, Vote, GAME_SIZE
from Managers.MatchManager import matchManager
from Managers.DatabaseManager import update_record, insert_record, find_record
from Managers.PlayerManager import Player

class CommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #TODO: Set their mmr based on their rank
    @commands.command()
    async def q(self, ctx: commands.Context):
        for player in queueManager.GetCurrentQueue().players:
            if player.id == ctx.author.id:
                return

        newPlayer = Player(ctx.author.id, ctx.guild.id)

        await queueManager.GetCurrentQueue().AddPlayer(newPlayer)

        currentQueueSize = queueManager.GetCurrentQueue().GetQueueSize()

        playersNeeded = GAME_SIZE - currentQueueSize

        embed = discord.Embed(title=f"Someone has joined the queue ({currentQueueSize}/{GAME_SIZE})", description=f"{ctx.author.mention} has joined the queue")
        embed.set_footer(text=f"{playersNeeded} more players needed to pop!")

        await ctx.reply("", embed=embed)

        await queueManager.GetCurrentQueue().CheckQueueFull(ctx)

    @commands.command()
    async def status(self, ctx):
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
                await currentQueue.AddVote(ctx, newVote)  

    @commands.command()
    async def votes(self, ctx):
        votes = ""

        voteCount = len(queueManager.GetCurrentQueue().votes)

        for vote in queueManager.GetCurrentQueue().votes:
            votes = votes + f"<@{vote.player.id}> voted for **`{vote.vote.name}`**\n"

        embed = discord.Embed(title="Current votes", description=votes)
        embed.set_footer(text=f"{voteCount}/{queueManager.GetCurrentQueue().GetQueueSize()} people have voted")
        await ctx.send("", embed=embed)

    @commands.command()
    async def report(self, ctx: commands.Context, matchNum, result):
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
        for player in queueManager.GetCurrentQueue().players:
            if player.id == ctx.author.id and queueManager.GetCurrentQueue().inVote == False:
                queueManager.GetCurrentQueue().players.remove(player)

                currentQueueSize = queueManager.GetCurrentQueue().GetQueueSize()

                playersNeeded = GAME_SIZE - currentQueueSize

                embed = discord.Embed(title=f"Someone has left the queue ({currentQueueSize}/{GAME_SIZE})", description=f"{ctx.author.mention} has left the queue")
                embed.set_footer(text=f"{playersNeeded} more players needed to pop!")

                await ctx.reply("", embed=embed)

def setup(bot):
    bot.add_cog(CommandsCog(bot))