import time
import asyncio
import discord
import traceback
from discord.ext import commands
import BotSettings
from threading import Thread

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

async def MainLoop():
	while True:
		messages = BotSettings.DB.get_messages()
		await BotSettings.bot_actions.process_messages(messages)
		await asyncio.sleep(BotSettngs.main_loop_timer)

@bot.event
async def on_ready():
	print('Logged in as')
	print(bot.user.name)
	print(bot.user.id)
	print('------')
	BotSettings.Setup(bot)
	bot.loop.create_task(MainLoop())

bot.run(BotSettings.token, bot=True, reconnect=True)