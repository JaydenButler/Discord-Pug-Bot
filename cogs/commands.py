import discord
from discord.ext import commands
from discord.ext.commands.cog import Cog
from pymongo.message import update
from Managers.QueueManager import queueManager, VoteTypes, Player, Vote, GAME_SIZE
from Managers.MatchManager import matchManager
from Managers.DatabaseManager import update_record, insert_record, find_record

class CommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #TODO: If already exists, delete and re create
    @commands.command()
    async def setup(self, ctx: commands.Context):
        data = {
            "_id": ctx.guild.id,
            "players": [],
            "matches": []
        }
        insert_record(data)
        await ctx.reply("Complete.")

    #TODO: Set their mmr based on their rank
    @commands.command()
    async def q(self, ctx: commands.Context):
        for player in queueManager.GetCurrentQueue().players:
            if player.id == ctx.author.id:
                return

        server = find_record(ctx.guild.id)

        inDatabase = False
        for player in server["players"]:
            if player["id"] == ctx.author.id:  
                inDatabase = True
        
        if inDatabase == False:
            newPlayer = {
                "id": ctx.author.id,
                "rank": None,
                "mmr": 1500,
            }
            update_record(ctx.guild.id, "$push", "players", newPlayer)
                

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

    #!Delete
    @commands.command()
    async def force_pop(self, ctx):
        if queueManager.GetCurrentQueue().GetQueueSize() > 1:

            teams = queueManager.GetCurrentQueue().DoQueuePop()
            
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
        else:
            await ctx.reply("Queue is too small to pop... Get some friends to play with!")

    @commands.command()
    async def reload(self, ctx: commands.Context, *, cog: str):
        try:
            self.bot.unload_extension("cogs." + cog)
            self.bot.load_extension("cogs." + cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')
    
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
    async def lookup(self, ctx: commands.Context, matchNum):
        if matchNum.isnumeric() == False:
            await ctx.reply("Please enter the match number is digit form, eg. **`500`**")
            return

        matches = matchManager.GetMatchInfo(ctx.guild.id)

        currentMatch = None

        for match in matches:
            if match["matchNum"] == int(matchNum):
                currentMatch = match
        
        if currentMatch != None:
            reported = currentMatch["reported"]
            winner = currentMatch["winner"]
            reportedBy = currentMatch["reportedBy"]
            
            description = f"Reported: {reported}\nWinning team: {winner}\nReported by: <@{reportedBy}>"
            
            if currentMatch["reportedBy"] == None:
                description = f"Reported: {reported}\nWinning team: {winner}\nReported by: {reportedBy}"

            embed = discord.Embed(title=f"Found the following for __Match {matchNum}__", description=description)

            teamOnePlayers = ""
            for player in currentMatch["teams"][0]["playerData"]["players"]:
                id = player["id"]
                teamOnePlayers = teamOnePlayers + f"<@{id}>\n"

            teamTwoPlayers = ""
            for player in currentMatch["teams"][1]["playerData"]["players"]:
                id = player["id"]
                teamTwoPlayers = teamTwoPlayers + f"<@{id}>\n"

            embed.add_field(name="Team 1", value=teamOnePlayers, inline=True)
            embed.add_field(name="Team 2", value=teamTwoPlayers, inline=True)

            await ctx.send("", embed=embed)
        else:
            await ctx.reply(f"Could not find match **`{matchNum}`**")
    
    @commands.command()
    async def swap(self, ctx, matchNum):
        if matchNum.isnumeric() == False:
            await ctx.reply("Please enter the match number is digit form, eg. **`500`**")
            return
        
        successful = matchManager.SwapResult(ctx.guild.id, int(matchNum))

        if successful == True:
            await ctx.reply(f"Scores for match **`{matchNum}`** swapped successfully")
        else:
            await ctx.reply("There was an error swaping the matches. Please make sure the match exists and has been reported before trying to swap.")
    
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