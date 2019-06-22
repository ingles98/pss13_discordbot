import BotSettings
import asyncio

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
        content = """You've got mail!\n\nFrom: `{}`\nTo: `{}`\nTitle: `{}`\n\n```{}```""".format( ic_sender, ic_receiver, message_title, formatted_message )
        await discord_user.send(content)

    async def send_broadcast(self, args:list, message_content:str):
        await BotSettings.bot_general_channel_ref.send(message_content)