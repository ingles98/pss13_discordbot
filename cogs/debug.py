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

    @commands.command()
    @commands.check(BotSettings.is_user_whitelisted)
    async def db_create_link(self, ctx, *args, member: discord.Member = None):
        """
        Manually creates a link between a discord account and a BYOND one.
        """
        valid = 0
        if len(args) == 2:
            userid, ckey = args
        elif len(args) == 3:
            userid, ckey, valid = args
            valid = 1 if valid else 0   # Making sure ppl dont fuck this one up
        else:
            return await ctx.author.send("Invalid usage. Needs at least two arguments. USER_ID CKEY [VALID? (0 or 1) ]")
        succ = BotSettings.DB.create_link(userid, ckey, valid)
        await ctx.author.send("Successfuly created link." if succ else "Something went wrong while creating the link. Check the bot's logs.")

    @commands.command()
    @commands.check(BotSettings.is_user_whitelisted)
    async def db_validate_link(self, ctx, *args, member: discord.Member = None):
        """
        Manually validates an existing link. Argument may be either a discord ID or a CKEY.
        """
        if not args or not len(args):
            return await ctx.author.send("Invalid usage. Needs at least one argument. (User ID or CKEY)")
        is_ckey = False
        user = args[0]
        try:
            int(user)
        except:
            is_ckey = True
        
        user_data = BotSettings.DB.get_user_data( user if not is_ckey else None, user if is_ckey else None)
        if not user_data:
            return await ctx.author.send("There is no entry with that user ID/CKEY.")
        if user_data["valid"]:
            return await ctx.author.send("This linkage is already validated.")
        succ = BotSettings.DB.validate_link(user_data["userID"])
        await ctx.author.send("Succesfully validated this user's link." if succ else "There was a problem validating this link. Check the bot's logs.")

    @commands.command()
    @commands.check(BotSettings.is_user_whitelisted)
    async def db_devalidate_link(self, ctx, *args, member: discord.Member = None):
        """
        Manually removes an existing link.
        """
        if not args or not len(args):
            return await ctx.author.send("Invalid usage. Needs at least one argument. (User ID or CKEY)")
        is_ckey = False
        user = args[0]
        try:
            int(user)
        except:
            is_ckey = True
        
        user_data = BotSettings.DB.get_user_data( user if not is_ckey else None, user if is_ckey else None)
        if not user_data:
            return await ctx.author.send("There is no entry with that user ID/CKEY.")
        succ = BotSettings.DB.devalidate_link(user_data["userID"])
        await ctx.author.send("Succesfully devalidated this user's link." if succ else "There was a problem devalidating this link. Check the bot's logs.")

    @commands.command()
    @commands.check(BotSettings.is_user_whitelisted)
    async def db_create_message(self, ctx, *args, member: discord.Member = None):
        """
        Manually creates and enqueues a message.
        First argument: command eg: MAIL or BROADCAST (Always on all caps.)
        Second argument: arguments (Have to be between quotes and seperated arguments using a special seperator set on the configs) eg: "firstarg[[sep]]secondarg[[sep]]you get it[[sep]]fuckthis"
        Third argument: message content
        (BROADCAST doesnt expect arguments at the moment. Send empty double quotes.)
        """
        if not args or len(args) != 3:
            return await ctx.author.send("Invalid number of arguments.")
        cmd, arguments, content = args
        succ = BotSettings.DB.create_message(cmd, arguments, content)
        await ctx.author.send("Successfully created and enqued a new message." if succ else "There was a problem creating and/or enqueing this message. Check the bot's logs.")


def setup(bot):
    bot.add_cog(DebugCommands(bot))
