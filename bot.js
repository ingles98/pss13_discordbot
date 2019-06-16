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

	createTable_queue() {
		const sql = `
		CREATE TABLE IF NOT EXISTS `+config.queueTable+` (
		msg TEXT)`
		return this.run(sql)
	}
	createTable_users() {
		const sql = `
		CREATE TABLE IF NOT EXISTS `+config.usersTable+` (
			userID STRING  PRIMARY KEY ON CONFLICT ROLLBACK
						   UNIQUE ON CONFLICT ROLLBACK
						   NOT NULL ON CONFLICT ROLLBACK,
			ckey   STRING  UNIQUE ON CONFLICT ROLLBACK
						   NOT NULL ON CONFLICT ROLLBACK,
			valid  BOOLEAN DEFAULT (false) 
		);		
		`
		return this.run(sql)
	}

	createTable() {
		this.createTable_queue();
		this.createTable_users();
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
		var sql = `SELECT * FROM `+config.queueTable
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
		var sql = `DELETE FROM `+config.queueTable+` WHERE msg =`+msg
		var params = []
		this.db.run(`DELETE FROM `+config.queueTable+` WHERE msg=?`, msg, function(err) {
			if (err) {
				return console.error(err.message);
			}
		})
	}

	message(target, msg) {
		//Handles all sorts of messaging
		this.clear_message_from_db(msg)
		var source = null
		var msg_array = msg.split("|")
		var cmd = msg_array[0]
		var parsed_msg = msg
		switch (cmd){
			case "MAIL":
				
				target = msg_array[1].split("\"").join("")
				source = msg_array[2]
				var target_character_name = msg_array[3]
				var message_title = msg_array[4]
				msg_array.splice(0,5)
				var message = msg_array.join(" ").split("[editorbr]").join("\n")
				if (! bot.servers[config.serverId]["members"].hasOwnProperty(target) ){
					console.log("WARNING - Attempted to MAIL non existing target user ID " + target)
					return false
				}
				parsed_msg = "You've got Mail!"+ "\n\nFrom: `"+ source +"`\nTo: \`"+target_character_name+"\`\nTitle: **\`"+message_title+"\`**\n\n```"+ message +"```"
				break;
			default:
				//
		}
		return bot.sendMessage({
			to: target,
			message: parsed_msg
		});
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
			case 'validatelink':
				var ckey = args[0]
				if (!ckey){
					bot.sendMessage({
						to: userID,
						message: 'You need to enter your BYOND username. Eg.: \"!validatelink stiigma\" - ' + ckey
					});
				} else {
					const err_usr_msg = `Sorry, but I couldn't process your Discord to Persistence link validation.
					\nHave you already linked your acount in-game? Or perhaps \`you're not typing your BYOND username (aka ckey) correctly!\`
					\nTo do so, simply join the server, press the \`"Special Verbs"\` tab and \`"Link Discord Account"\`.`+
					`\nYou'll just need to enter DEVELOPER MODE on discord to be able to grab your user ID. If it is enabled,`+
					`just right-click on your Username and pick "Copy ID" on the context menu, then paste it on the input window that`+
					`had popped in-game.
					\nAfterwards, you may validate your linkage here.`
					const sql = `SELECT * FROM `+config.usersTable+` WHERE userID = '`+'\"'+userID+'\"'+`' AND ckey = "`+ckey+`"`
					sqlmngr.db.get(sql, params=[], (err, result) => {
						if (err) {
							console.log('validatelink - Error running sql: ' + sql)
							console.log(err)
							bot.sendMessage({
								to: userID,
								message: err_usr_msg
							});
						} else {
							if (result){
								//console.log("USER ID EXISTS - "+userID+" rs: "+result)
								var status_msg = "Hooray! Your account has been linked!"
								if (result.valid == 0){
									const sql = `UPDATE `+config.usersTable+` SET valid = 1 WHERE userID = '`+'\"'+userID+'\"'+`'`
									sqlmngr.db.run(sql, params = [], function (err) {
										if (err) {
											console.log('Error running sql ' + sql)
											console.log(err)
											status_msg = "There was a problem processing your validation request. Please, contact a developer."
										} else {

										}
									})
								} else {
									status_msg = `My apologies, but this Discord account is already linked! You may unlink it using the following methods:
									\n\t - \`!devalidatelink\`
									\n\t - \`In-game > "Special Verbs" > "Devalidate Discord Link"\``
								}
								bot.sendMessage({
									to: userID,
									message: status_msg
								});
							} else {
								console.log('NO RESULT' + sql)
								bot.sendMessage({
									to: userID,
									message: err_usr_msg
								});
							}
						}
					})
				}
				break;
         }
     }
});

function Main (){
	if (generalChannel != null && bot != null && bot_ready){
		sqlmngr.get_messages(generalChannel.id)
	}
	setTimeout(() => {
		Main ()
	}, 3000);
}
Main()