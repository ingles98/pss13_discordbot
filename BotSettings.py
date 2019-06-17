import json
import discord
from InternalClasses.DatabaseDAO import DatabaseDAO
from InternalClasses.BotActions import BotActions
from discord.ext.commands import Bot

"""
The seperator between arguments inside a string because spaces could be
insufficient. Use the same seperator as in the game's code:

(code/modules/discord_persistence/_hook.dm)
"""

queue_command_arguments_sep = "[[sep]]"
main_loop_timer = 2  # Seconds
command_prefix = "!"
token = 'NTg5ODM0NzkxNzU1NzEwNTA2.XQZe-A.h5JV5bB5UbqIxCSiwXeE0eX3uok'
db_path = ""
queueTable = ""
usersTable = ""
serverId = 0
generalChannelId = 0

DB: DatabaseDAO = None
bot_actions: BotActions = None
bot_ref: Bot = None
bot_general_channel_ref: discord.TextChannel = None


with open('config.json') as json_file:
    data = json.load(json_file)
    token = data["token"]
    db_path = data["db"]
    queueTable = data["queueTable"]
    usersTable = data["usersTable"]
    serverId = int(data["serverId"])
    generalChannelId = int(data["generalChannelId"])


def setup_bot(bot: Bot):
    # Save reference to the Bot
    global bot_ref
    bot_ref = bot

    # Setup database DAO
    global DB
    DB = DatabaseDAO(db_path, usersTable, queueTable)

    # Setup bot actions class
    global bot_actions
    bot_actions = BotActions()

    # Setup general channel discord object reference
    global bot_general_channel_ref
