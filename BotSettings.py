import json
import discord
from InternalClasses.DatabaseDAO import DatabaseDAO
from InternalClasses.BotActions import BotActions
from discord.ext.commands import Bot
from os import path

"""
The seperator between arguments inside a string because spaces could be
insufficient. Use the same seperator as in the game's code:

(code/modules/discord_persistence/_hook.dm)
"""
queue_command_arguments_sep = "[[sep]]"

main_loop_timer = 2  # Seconds
command_prefix = "!"
token = str()
db_path = str()
queueTable = str()
usersTable = str()
serverId = 0
generalChannelId = 0
COMMANDS_WHITELIST = list() # A whiteLIST for commands that require it. Currently only the debug Cog commands should require it.
                            # Can be user ID's (INT) or server roles (STR)

MESSAGE_CONFIG_NOT_FOUND = """
----------
CONFIG FILE 'config.json' NOT FOUND!
REMEMBER TO COPY OVER 'config.json.example' TO 'config.json'
EXITING!
----------
"""

DB: DatabaseDAO = None
bot_actions: BotActions = None
bot_ref: Bot = None
bot_general_channel_ref: discord.TextChannel = None


if path.exists('config.json'):
    with open('config.json') as json_file:
        data = json.load(json_file)
        token = data["token"]
        db_path = data["db"]
        queueTable = data["queueTable"]
        usersTable = data["usersTable"]
        serverId = int(data["serverId"])
        generalChannelId = int(data["generalChannelId"])
        if "whitelist" in data:
            COMMANDS_WHITELIST = data["whitelist"]
else:
    print(MESSAGE_CONFIG_NOT_FOUND)
    quit()

def is_user_whitelisted(ctx):
        # Check if the user ID is in the whitelist
        if ctx.author.id in COMMANDS_WHITELIST:
            return True
        # Check if the context is of a server(guild) and if so, check if the member has whitelisted roles.
        if ctx.guild:
            member = ctx.guild.get_member(ctx.author.id)
            for role in member.roles:
                if role.name in COMMANDS_WHITELIST:
                    return True
        return False

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
    bot_general_channel_ref = bot.get_channel(generalChannelId)