import asyncio
import traceback
from discord.ext import commands
import BotSettings

bot = commands.Bot(command_prefix=BotSettings.command_prefix)

extensions = [
    'cogs.debug'
]

for extension in extensions:
    try:
        bot.load_extension(extension)

    except Exception as e:
        print(e)
        traceback.print_exc()


async def main_loop():
    while True:
        messages = BotSettings.DB.get_messages()
        await BotSettings.bot_actions.process_messages(messages)
        await asyncio.sleep(BotSettings.main_loop_timer)


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

    BotSettings.Setup(bot)
    bot.loop.create_task(main_loop())

bot.run(BotSettings.token, bot=True, reconnect=True)
