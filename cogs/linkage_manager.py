import BotSettings
import discord
from discord.ext import commands

MESSAGE_LINK_NO_CKEY_PROVIDED = """
You need to enter your BYOND username. Eg.: "{}validatelink stiigma"
""".format(BotSettings.config.command_prefix)

MESSAGE_LINK_FAILED = """
Sorry, but I couldn't process your Discord to Persistence link validation.

Have you already linked your acount in-game? Or perhaps `you're not typing your BYOND username (aka ckey) correctly!`
To do so, simply join the server, press the `"Special Verbs"` tab and `"Link Discord Account"`

~~You'll just need to enter DEVELOPER MODE on discord to be able to grab your user ID. If it is enabled, 
just right-click on your Username and pick "Copy ID" on the context menu, then paste it on the input window that had popped in-game.~~
**Type in the command `"{}getid"` to retrieve your User ID.**

Afterwards, you may validate your linkage here.
""".format(BotSettings.config.command_prefix)

MESSAGE_LINK_ALREADY_EXISTS = """
My apologies, but this Discord account is already linked! You may unlink it using the following methods:
    - `{}devalidatelink`
    - `In-game > "Special Verbs" > "Devalidate Discord Link"`
""".format(BotSettings.config.command_prefix)

MESSAGE_LINK_ERROR = """
There was a problem processing your validation request. Please, contact a developer.
"""

MESSAGE_LINK_SUCCESS = """
Hooray! Your account has been linked!
"""

MESSAGE_UNLINK_LINK_DOESNT_EXIST = """
It seems like your discord account isn't linked to any BYOND account on Persistence.
"""

MESSAGE_UNLINK_ERROR = """
There was a problem processing your devalidation request. Please, contact a developer.
"""

MESSAGE_UNLINK_SUCCESS = """
Your account has been successfuly unlinked.
"""

MESSAGE_USER_ID = """
Here's your Discord User ID: {}
"""

class LinkageManager(commands.Cog, name="Link validation commands"):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    def __get_user_data(self, userid, ckey=None):
        return BotSettings.DB.get_user_data(userid, ckey)

    def __validate_link(self, userid):
        return BotSettings.DB.validate_link(userid)

    def __devalidate_link(self, userid):
        return BotSettings.DB.devalidate_link(userid)

    @commands.command()
    async def validatelink(self, ctx, *args):
        """
        Validate your discord-BYOND account link through this command.
        """
        userid = ctx.author.id
        ckey = " ".join(args)
        if not ckey:
            await ctx.author.send( MESSAGE_LINK_NO_CKEY_PROVIDED )
            return
        db_user_data = self.__get_user_data(userid, ckey)
        if not db_user_data:
            await ctx.author.send( MESSAGE_LINK_FAILED )
            return
        if db_user_data["valid"]:
            await ctx.author.send( MESSAGE_LINK_ALREADY_EXISTS )
            return
        if not self.__validate_link(userid):
            await ctx.author.send( MESSAGE_LINK_ERROR )
            return
        await ctx.author.send( MESSAGE_LINK_SUCCESS )

    @commands.command()
    async def devalidatelink(self, ctx, *args):
        """
        Devalidate your discord-BYOND linkage.
        """
        userid = ctx.author.id
        if not self.__get_user_data(userid):
            await ctx.author.send( MESSAGE_UNLINK_LINK_DOESNT_EXIST )
            return
        if not self.__devalidate_link(userid):
            await ctx.author.send( MESSAGE_UNLINK_ERROR )
            return
        await ctx.author.send( MESSAGE_UNLINK_SUCCESS )


    @commands.command()
    async def getid(self, ctx, *args):
        """Returns your Discord User ID."""
        await ctx.author.send( MESSAGE_USER_ID.format(ctx.author.id) )

def setup(bot):
    bot.add_cog(LinkageManager(bot))
