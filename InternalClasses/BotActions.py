import BotSettings
import asyncio
import discord

class BotActions:
    """
    This class controls bot actions like sending e-mail notifications and channel broadcasts.
    (To be used by the DatabaseDAO class)
    """

    COMMAND_MAIL = "MAIL"
    COMMAND_BROADCAST = "BROADCAST"

    async def process_messages(self, messages:list) -> None:
        """
        Processes the messages retrieved from the queue table on the database.

        Arguments:
            messages -> list of dictionaries
        
        Returns:
            None
        """
        if not messages:
            return
        for message in messages:
            print(" -- BotActions - Processing message: {}".format(dict(message)))
            cmd = message["command"]
            args = message["command_arguments"].split(BotSettings.config.queue_command_arguments_sep) if message["command_arguments"] else None
            message_content = message["msg"]
            print(cmd)
            if cmd == self.COMMAND_MAIL:
                await self.send_mail(args, message_content)
            elif cmd == self.COMMAND_BROADCAST:
                await self.send_broadcast(args, message_content)
            else:
                print("ERROR - Received a message with an unknown command !")
            print(" -- ")

    async def send_mail(self, args:list, message_content:str) -> None:
        if not args or not len(args):
            print("ERROR - BotActions.send_mail() need to receive a non-empty list 'args', got {}. This message will be ignored.".format(args))
            return
        discord_user_id, ic_sender, ic_receiver, message_title = args
        discord_user = BotSettings.bot_ref.get_user(int(discord_user_id))
        if not discord_user:
            print("ERROR - discord_user_id not found. Probably this user is not in contact with our bot. (On DMs and servers)")
            return

        formatted_message = message_content.replace("[editorbr]", "\n").replace("[br]", "\n")
        print( discord_user_id, ic_sender, ic_receiver, message_content)
        mail_embed = discord.Embed(
            title=u'\U0001f6f0 Incoming Transmission',
            description="You've got mail!",
            color=0xadd8e6)
        mail_embed.add_field(name="From:", value=ic_sender, inline=True)
        mail_embed.add_field(name="To:", value=ic_receiver, inline=True)
        mail_embed.add_field(name="Title:", value=message_title, inline=True)
        mail_embed.add_field(name="\u200b", value=formatted_message, inline=False)
        await discord_user.send(embed=mail_embed)

    async def send_broadcast(self, args:list, message_content:str):
        announce_embed = discord.Embed(
            title=u'\U0001f6f0 Incoming Transmission',
            color=0x000000)
        announce_embed.add_field(name="\u200b", value=message_content, inline=False)
        announce_embed.set_thumbnail(url=str(BotSettings.bot_ref.user.avatar_url))
        await BotSettings.bot_general_channel_ref.send(embed=announce_embed)