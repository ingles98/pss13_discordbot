import json
import discord
from InternalClasses.DatabaseDAO import DatabaseDAO
from InternalClasses.BotActions import BotActions
from discord.ext.commands import Bot
from os import path


MESSAGE_CONFIG_NOT_FOUND = """
----------
CONFIG FILE 'config.json' NOT FOUND!
REMEMBER TO COPY OVER 'config.json.example' TO 'config.json'
EXITING!
----------
"""
MESSAGE_CONFIG_FORMAT_ERROR = """
----------
ERROR PARSING CONFIG FILE 'config.json'!
ERROR: {}
NO CONFIGURATIONS WERE LOADED
EXITING!
----------
"""


class BotConfigurations():
    """
    Handles the configurations.
    """
    """
    The separator between arguments inside a string because spaces could be
    insufficient. Use the same seperator as in the game's code:

    (code/modules/discord_persistence/_hook.dm)
    """
    queue_command_arguments_sep = "[[sep]]"

    main_loop_timer = 2  # Seconds
    command_prefix = "!"
    token = str()
    db_path = str()
    queue_table = str()
    users_table = str()
    server_id = 0   # Currently not used
    general_channel_id = 0

    """
    A whitelist for commands that require it. Currently onl the debug Cog
    commands should require it. Can be a user's ID (int) or server role (str).
    """
    whitelist_debug_commands = list()

    process_queue = True  # Used in the main loop to pause/resume bot queries.

    def __init__(self):
        if not self.load_config():
            quit()

    def load_config(self):
        if path.exists('config.json'):
            with open('config.json') as json_file:
                try:
                    data:dict = json.load(json_file)
                except Exception as err:
                    print(MESSAGE_CONFIG_FORMAT_ERROR.format(err))
                    return False
                self.token = data.pop("token", self.token)
                self.db_path = data.pop("db", self.db_path)
                self.queue_table = data.pop("queueTable", self.queue_table)
                self.users_table = data.pop("usersTable", self.users_table)
                self.server_id = int(data.pop("serverId", self.server_id))
                self.general_channel_id = int(
                    data.pop("generalChannelId", self.general_channel_id))
                self.whitelist_debug_commands = data.pop(
                    "whitelist", self.whitelist_debug_commands)
                return True
        else:
            print(MESSAGE_CONFIG_NOT_FOUND)
        return False

config: BotConfigurations = BotConfigurations()
DB: DatabaseDAO = None
bot_actions: BotActions = None
bot_ref: Bot = None
bot_general_channel_ref: discord.TextChannel = None


def is_user_whitelisted(ctx):
    """
    Simple whitelist check.
    Returns true if ctx.author or ctx.guild is found in whitelist.
    """

    if ctx.author.id in config.whitelist_debug_commands:
        return True
    if ctx.guild:
        member = ctx.guild.get_member(ctx.author.id)
        for role in member.roles:
            if role.name in config.whitelist_debug_commands:
                return True
    return False


def setup_bot(bot: Bot):
    # Save reference to the Bot
    global bot_ref
    bot_ref = bot

    # Setup database DAO
    global DB
    DB = DatabaseDAO(config.db_path, config.users_table, config.queue_table)

    # Setup bot actions class
    global bot_actions
    bot_actions = BotActions()

    # Setup general channel discord object reference
    global bot_general_channel_ref
    bot_general_channel_ref = bot.get_channel(config.general_channel_id)
