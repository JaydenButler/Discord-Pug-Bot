import discord
from discord.ext import commands
from discord.ext.commands.cog import Cog
from cogs.queue import queueManager

from cogs.queue import Player

class CommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def q(self, ctx: commands.Context):
        newPlayer = Player(ctx.author.id)

        await queueManager.GetCurrentQueue().AddPlayer(ctx, newPlayer)

        currentQueueSize = queueManager.GetCurrentQueue().GetQueueSize()

        playersNeeded = 6 - currentQueueSize

        embed = discord.Embed(title=f"Someone has joined the queue ({currentQueueSize}/6)", description=f"{ctx.author.mention} has joined the queue")
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
        
        playersNeeded = 6 - queueManager.GetCurrentQueue().GetQueueSize()
        
        embed = discord.Embed(title="Current members in the queue", description=playersStr)
        embed.set_footer(text=f"{playersNeeded} more players needed to pop!")
        
        await ctx.reply("", embed=embed)

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
    
def setup(bot):
    bot.add_cog(CommandsCog(bot))