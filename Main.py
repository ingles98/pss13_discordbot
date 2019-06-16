import time
import discord
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

def MainLoop():
	while True:
		BotSettings.DB.get_messages()
		print("endtick")
		time.sleep(BotSettings.main_loop_timer)

@bot.event
async def on_ready():
	print('Logged in as')
	print(bot.user.name)
	print(bot.user.id)
	print('------')
	MainLoop()

bot.run(BotSettings.token, bot=True, reconnect=True)