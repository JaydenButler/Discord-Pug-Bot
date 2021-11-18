import discord
from discord.ext import commands
from Managers.MatchManager import matchManager
from Managers.QueueManager import queueManager
from Managers.DatabaseManager import insert_record

MOD_ROLE = "mods"

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #region High only cmds
    #TODO: If already exists, delete and re create
    @commands.is_owner()
    @commands.command()
    async def setup(self, ctx: commands.Context):
        data = {
            "_id": ctx.guild.id,
            "players": [],
            "matches": []
        }
        insert_record(data)
        await ctx.reply("Complete.")

    @commands.is_owner()
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
    
    @commands.is_owner()
    @commands.command()
    async def reload(self, ctx: commands.Context, *, cog: str):
        try:
            self.bot.unload_extension("cogs." + cog)
            self.bot.load_extension("cogs." + cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')
    #endregion

    #region Mod cmds
    @commands.has_role(MOD_ROLE)
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
    
    @commands.has_role(MOD_ROLE)
    @commands.command()
    async def swap(self, ctx, matchNum):
        if matchNum.isnumeric() == False:
            await ctx.reply("Please enter the match number is digit form, eg. **`500`**")
            return
        
        successful = matchManager.SwapResult(ctx.guild.id, int(matchNum))

        if successful == True:
            await ctx.message.add_reaction("✅")     
        else:
            await ctx.message.add_reaction("❌")  
    #endregion
    
def setup(bot):
    bot.add_cog(AdminCommands(bot))
