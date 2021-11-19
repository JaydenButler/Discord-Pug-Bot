import discord
from discord.abc import GuildChannel
from discord.ext import commands
from Managers.MatchManager import matchManager
from Managers.DatabaseManager import find_record, insert_record, update_record, delete_record

MOD_ROLE = "mods"

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #region High only cmds
    #TODO: If already exists, delete and re create
    @commands.is_owner()
    @commands.command()
    async def setup(self, ctx: commands.Context):
        delete_record(ctx.guild.id)
        data = {
            "_id": ctx.guild.id,
            "players": [],
            "matches": [],
            "ranks": []
        }
        insert_record(data)
        await ctx.reply("Complete.")
    
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
    
    @commands.has_role(MOD_ROLE)
    @commands.command()
    async def lookup(self, ctx, user: discord.User):
        server = find_record(ctx.guild.id)
        userInfo = ""
        foundUser = False
        for player in server["players"]:
            if user.id == player["id"]:
                foundUser = True
                userInfo = f"**User ID**: {player['id']}\n**Rank**: {player['rank']}\n**Elo**: {player['mmr']}"
        if foundUser == True:
            embed = discord.Embed(title=f"Lookup results for {user.display_name}#{user.discriminator}", description=userInfo)
            await ctx.reply("", embed=embed)
        else:
            await ctx.message.add_reaction("❌")

    @commands.has_role(MOD_ROLE)
    @commands.command()
    async def addrank(self, ctx: commands.Context, rank: str, mmr: int):
        server = find_record(ctx.guild.id)
        rank = rank.upper()
        guild = ctx.guild

        role = None
        
        #check if role exists
        roleExists = False
        for guildRole in guild.roles:
            if f"Rank {rank}" == guildRole:
                roleExists = True

        if roleExists == False:
            role = await guild.create_role(name=f"Rank {rank}")

        #check if channel exists
        channelExists = False

        for guildChannel in guild.channels:
            if guildChannel.name == f"rank-{rank.lower()}":
                channelExists = True
        
        if channelExists == False:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True),
                role: discord.PermissionOverwrite(read_messages=True)
            }
            await guild.create_text_channel(f"rank-{rank.lower()}", overwrites=overwrites)
        
        #add to DB
        rankExists = False
        
        for dbRank in server["ranks"]:
            if rank == dbRank:
                rankExists = True
        
        if rankExists == False:
            newRank = {
                "name": rank,
                "mmr": mmr
            }
            update_record(ctx.guild.id, "$push", "ranks", newRank)
            

        await ctx.send("Complete.")
    
    @commands.has_role(MOD_ROLE)
    @commands.command()
    async def setrank(self, ctx, user: discord.User, rank: str):
        server = find_record(ctx.guild.id)
        rank = rank.upper()
        successful = False

        inDatabase = False
        for player in server["players"]:
            if player["id"] == user.id:  
                inDatabase = True
        
        if inDatabase == False:
            newPlayer = {
                "id": user.id,
                "rank": None,
                "mmr": 1500,
            }
            update_record(ctx.guild.id, "$push", "players", newPlayer)

        server = find_record(ctx.guild.id)

        i = 0
        for dbRank in server["ranks"]:
            if rank == dbRank["name"]:
                for player in server["players"]:
                    if user.id == player["id"]:
                        successful = True
                        update_record(ctx.guild.id, "$set", f"players.{i}.rank", rank)
                        update_record(ctx.guild.id, "$set", f"players.{i}.mmr", dbRank["mmr"])
                    i = i + 1

        if successful == True:
            await ctx.message.add_reaction("✅")     
        else:
            await ctx.message.add_reaction("❌") 

    @commands.command()
    async def ranks(self, ctx):
        server = find_record(ctx.guild.id)
        ranks = ""

        for rank in server["ranks"]:
            role = discord.utils.get(ctx.guild.roles, name=f"Rank {rank['name']}")
            channel = discord.utils.get(ctx.guild.channels, name=f"rank-{rank['name'].lower()}")
            ranks = ranks + f"Rank {rank['name']} ({rank['mmr']}) - {role.mention} - {channel.mention}\n"

        embed = discord.Embed(title="Current Ranks", description=ranks)

        await ctx.send("", embed=embed)

    #endregion
    
def setup(bot):
    bot.add_cog(AdminCommands(bot))
