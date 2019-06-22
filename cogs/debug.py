import BotSettings
import discord
from discord.ext import commands

class DebugCommands(commands.Cog, name="Debug Commands"):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    @commands.check(BotSettings.is_user_whitelisted)
    async def hello(self, ctx, *, member: discord.Member = None):
        """
        Says hello
        """
        member = member or ctx.author
        if self._last_member is None or self._last_member.id != member.id:
            await ctx.send('Hello {0.name}~'.format(member))
        else:
            await ctx.send(
                    'Hello {0.name}... This feels familiar.'.format(member)
            )
        self._last_member = member

    @commands.command()
    @commands.check(BotSettings.is_user_whitelisted)
    async def db_get_users(self, ctx, *, member: discord.Member = None):
        """
        Retrieves all entries in the Users table from the database and DMs it to you.
        """
        users = BotSettings.DB.get_all_users()
        users_parsed = str()
        for user in users:
            users_parsed += str(dict(user)) +"\n"
        await ctx.author.send("Users table: \n```{}```".format(users_parsed or "N/A") )

    @commands.command()
    @commands.check(BotSettings.is_user_whitelisted)
    async def db_get_queue(self, ctx, *, member: discord.Member = None):
        """
        Retrieves all entries in the Queue table from the database and DMs it to you.
        """
        queue = BotSettings.DB.get_queue()
        queue_parsed = str()
        for msg in queue:
            queue_parsed += str(dict(msg)) +"\n"
        await ctx.author.send("Queue table: \n```{}```".format(queue_parsed or "N/A") )

def setup(bot):
    bot.add_cog(DebugCommands(bot))
