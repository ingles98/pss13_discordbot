var Discord = require('discord.io');
var logger = require('winston');
var config = require('./config.json');

const sqlite3 = require('sqlite3')  
const Promise = require('bluebird')

class AppDAO {

	constructor(dbFilePath) {
		this.db = new sqlite3.Database(dbFilePath, (err) => {
		if (err) {
			console.log('Could not connect to database', err, dbFilePath)
		} else {
			console.log('Connected to database')
		}
		})
	}

	run(sql, params = []) {
		return new Promise((resolve, reject) => {
		this.db.run(sql, params, function (err) {
			if (err) {
			console.log('Error running sql ' + sql)
			console.log(err)
			reject(err)
			} else {
			resolve({ id: this.lastID })
			}
		})
		})
	}

	createTable() {
		const sql = `
		CREATE TABLE IF NOT EXISTS discord_hook (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		msg TEXT)`
		return this.run(sql)
	}

	get(sql, params = []) {
		this.db.get(sql, params, (err, result) => {
		if (err) {
			console.log('Error running sql: ' + sql)
			console.log(err)
			reject(err)
		} else {
			//resolve(result)
			return result
		}
		})
	}

	get_messages(channel_id) {
		var sql = `SELECT * FROM discord_hook`
		var params = []
		
		this.db.all(sql, params, (err, rows) => {
			if (err) {
				console.log('Error running sql: ' + sql)
				console.log(err)
			} else {
				//resolve(rows)
				rows.forEach((row) => {
					console.log(row.msg);
					this.message(channel_id, row.msg)
				});
			}
		})
	}

	clear_message_from_db(msg) {
		var sql = `DELETE FROM discord_hook WHERE msg =`+msg
		var params = []
		this.db.run(`DELETE FROM discord_hook WHERE msg=?`, msg, function(err) {
			if (err) {
				return console.error(err.message);
			}
		})
	}

	message(target, msg) {
		//target = "178524531575619584"
		var source = null
		var msg_array = msg.split(" ")
		var cmd = msg_array[0]
		var parsed_msg = msg
		switch (cmd){
			case "MAIL":
				target = msg_array[1]
				source = msg_array[2]
				msg_array.splice(0,3)
				parsed_msg = "EMAIL RECEIVED - "+ "From "+ source +" - "+ msg_array.join(" ")
				break;
			default:
				//
		}
		bot.sendMessage({
			to: target,
			message: parsed_msg
		});
		this.clear_message_from_db(msg)
	}
}

pathToDb = config.db
var sqlmngr = new AppDAO (pathToDb)
sqlmngr.createTable()

// Configure logger settings
logger.remove(logger.transports.Console);
logger.add(new logger.transports.Console, {
    colorize: true
});
logger.level = 'debug';
// Initialize Discord Bot
var bot = new Discord.Client({
   token: config.token,
   autorun: true
});

var generalChannel = null//bot.channels.get( toString(config.generalChannelId) )
var bot_ready = false

bot.on('ready', function (evt) {
    logger.info('Connected');
    logger.info('Logged in as: ');
	logger.info(bot.username + ' - (' + bot.id + ')');
	//bot.setActivity("with PSS13 code!");
	var channels = bot.channels//.get( toString(config.generalChannelId) )
	for (i in channels) {
		//logger.info(i, channels[i]);
		if (channels[i].id == config.generalChannelId){
			generalChannel = channels[i];
			break;
		}
	}

	bot_ready = true
});
bot.on('message', function (user, userID, channelID, message, evt) {
    // Our bot needs to know if it will execute a command
    // It will listen for messages that will start with `!`
    if (message.substring(0, 1) == '!') {
        var args = message.substring(1).split(' ');
        var cmd = args[0];
       
        args = args.splice(1);
        switch(cmd) {
            // !ping
            case 'ping':
                bot.sendMessage({
                    to: channelID,
                    message: 'Pong!'
				});
			case 'hookdb':
				sqlmngr.get_messages(channelID)
            break;
            // Just add any case commands if you want to..
         }
     }
});

function Main (){
	if (generalChannel != null && bot != null && bot_ready){
		//generalChannel.send("Hello, world!")
		sqlmngr.get_messages(generalChannel.id)
	}
	setTimeout(() => {
		Main ()
	}, 3000);
}
Main()