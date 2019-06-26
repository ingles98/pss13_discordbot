import asyncio
import traceback
from discord.ext import commands
import BotSettings

bot = commands.Bot(command_prefix=BotSettings.config.command_prefix)

extensions = [
    'cogs.linkage_manager'
]

for extension in extensions:
    try:
        bot.load_extension(extension)
    except Exception as e:
        print(e)
        traceback.print_exc()


async def main_loop():
    while True:
        if BotSettings.config.process_queue:
            messages = BotSettings.DB.get_messages()
            await BotSettings.bot_actions.process_messages(messages)
        await asyncio.sleep(BotSettings.config.main_loop_timer)


@bot.command()
@commands.check(BotSettings.is_user_whitelisted)
async def load(ctx, extension: str):
    """
    Loads an extension

    Example: !load cogs.debug
    """

    try:
        bot.load_extension(extension)

    except (AttributeError, ImportError) as e:
        await ctx.send("```py\n{}: {}\n```".format(type(e).__name__, str(e)))

    await ctx.send("{} loaded".format(extension))


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure ):
        print("WARNING --- User {} is attempting to execute the " +
              "command '{}' but failed the whitelist/permissions " +
              "checks.".format(
                  {"name": ctx.author.name, "id": ctx.author.id},
                  ctx.command.name))
    else:
        print(error)


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

    BotSettings.setup_bot(bot)
    bot.loop.create_task(main_loop())

bot.run(BotSettings.config.token, bot=True, reconnect=True)
