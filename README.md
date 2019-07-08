## Persistent SS13 Discord Bot

A Discord bot written in Python. It handles communications between Discord and the SS13 server.

### Installation
```
git clone https://github.com/ingles98/pss13_discordbot    # clone the repo.
cd pss13_discordbot                                       # cd into the repo.
python3 -m venv venv                                      # (optional) make a virtual environment.
pip install -r requirements.txt                           # install requirements.
```

### Usage
```
cp config.json.example config.json                        # copy example config over.
python3 Main.py                                           # run the bot.
```

### Configuration
All configuration is handled through config.json. This file is required to run the bot.
```
{
    "token":                                              # your bot token.
    "db":                                                 # the absolute or relative path to the sqlite db.
    "queueTable":                                         # name of the queue table.
    "usersTable":                                         # name of the users table.
    "serverId":                                           # discord server ID.
    "generalChannelId":                                   # ID of the channel where the bot sends it's announcements.
    "ahelpChannelId":                                     # Same as above, but for in-game tickets for the admins.
    "whitelist":                                          # List of server roles or user IDs that may use the debug commands (eg: " "whitelist" : [752381239521385291357, "Admins", "Fake Role"] ")
}
```
