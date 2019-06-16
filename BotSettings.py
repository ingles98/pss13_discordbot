import json
from BotInternalClasses import DatabaseDAO


main_loop_timer = 5 # Seconds
command_prefix = "!"
token = 'NTg5ODM0NzkxNzU1NzEwNTA2.XQZe-A.h5JV5bB5UbqIxCSiwXeE0eX3uok'
db_path = ""
queueTable = ""
usersTable = ""
serverId = 0
generalChannelId = 0


with open('config.json') as json_file:
	data = json.load(json_file)
	token = data["token"]
	db_path = data["db"]
	queueTable = data["queueTable"]
	usersTable = data["usersTable"]
	serverId = int(data["serverId"])
	generalChannelId = int(data["generalChannelId"])

DB = DatabaseDAO(db_path, usersTable, queueTable)
