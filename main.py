#!/usr/bin/python3.5

import asyncio
import discord

import re
import json
import config

# regex for the add-game and add-user commands
EQUAL_REGEX = re.compile(r"""(\w+)\s*=\s*["'](.+?)["']""")

botToken, channels, users, roles, pf = config.load_config()
master                                   = config.load_json()

consoles = master["consoles"]
users    = master["users"]

client = discord.Client()

async def get_spaces(msgc, command):
	command_length = len(command) - 1
	i = 1

	while (i < len(msgc) - command_length):
		if msgc[i + command_length] != " ":
			return i
		else:
			i += 1

	return None

# returns a dictionary containing keys for various variables
async def return_variables(msgc):
	match_list = EQUAL_REGEX.findall(msgc)
	variable_list = ["name", "console", "link", "ip"]

	variables = {}

	for match in match_list:
		variables[match[0]] = match[1]

	return variables	

async def add_console(message, command):
	msg = message.content
	spaces = await get_spaces(msg, command)

	if spaces == None:
		await client.send_message(message.channel, "Your argument(s) are invalid!  Use **{}help**".format(pf))
		return

	console_name = msg[len(command) - 1 + spaces : ]

	if console_name in consoles:
		await client.send_message(message.channel, "The **{}** section exists already!".format(console_name))
		return

	consoles[console_name] = {}

	await client.send_message(message.channel, "The **{}** section was created successfully.".format(console_name))
	print(consoles)

	return 

async def remove_console(message, command):
	msg = message.content
	spaces = await get_spaces(msg, command)

	if spaces == None:
		await client.send_message(message.channel, "Your argument(s) are invalid!  Use **{}help**".format(pf))
		return
	
	console_name = msg[len(command) - 1 + spaces : ]

	if console_name not in consoles:
		await client.send_message(message.channel, "That console doesn't exist!")	
		return

	consoles.pop(console_name, None)
	
	await client.send_message(message.channel, "Deleted.")
	print(consoles)

	return

async def add_game(message, command):
	msg = message.content
	variables = await return_variables(msg)

	# TODO: this is kinda messy.  Refactor if possible.
	try:
		if variables["console"] not in consoles:
			await client.send_message(message.channel, "Please enter a valid console section.")
			return

		if ("name" not in variables) or ("link" not in variables):
			await client.send_message(message.channel, "Some parameters were not filled!  Use **{}help**".format(pf))
			return

		if variables["name"] in consoles[variables["console"]]:
			await client.send_message(message.channel, "That game already exists for that console!")
			return

		consoles[variables["console"]][variables["name"]] = variables["link"]

		await client.send_message(message.channel, "Added **{name}** to the **{console}** section.".format(name = variables["name"], console = variables["console"]))
		print(consoles)
	except KeyError:
		await client.send_message(message.channel, "Some parameters were not filled!  Use **{}help**".format(pf))
	return

async def remove_game(message, command):
	msg = message.content
	spaces = await get_spaces(msg, command)

	game_exist = False

	if spaces == None:
		await client.send_message(message.channel, "Your argument(s) are invalid!  Use **{}help**".format(pf))
		return

	name = msg[len(command) - 1 + spaces : ]

	for console in consoles:
		if name not in consoles:
			continue

		game_exist = True
		consoles[console].pop(name, None)

	if game_exist:
		await client.send_message(message.channel, "Deleted.")
	else:
		await client.send_message(message.channel, "That game doesn't exist!")

	print(consoles)
	
	return

async def list_games(message, command):
	master_list = "**List of All Games By Console:\n**"

	for console, games in consoles.items():
		master_list += "  {}:\n".format(console)

		for name, link in games.items():
			master_list += "    {name} : {link}\n".format(name = name, link = link)

		master_list += "\n"

	await client.send_message(message.channel, master_list)
	return

async def add_user(message, command):
	msg = message.content
	variables = await return_variables(msg)

	if ("name" not in variables) or ("ip" not in variables):
		await client.send_message(message.channel, "Some parameters were not filled!  Use **{}help**".format(pf))
		return

	if variables["name"] in users:
		await client.send_message(message.channel, "That user already exists!")
		return

	users[variables["name"]] = variables["ip"]

	await client.send_message(message.channel, "User added successfully.")
	print(users)

	return

async def remove_user(message, command):
	msg = message.content
	spaces = await get_spaces(msg, command)

	if spaces == None:
		await client.send_message(message.channel, "Your argument(s) are invalid!  Use **{}help**".format(pf))
		return

	name = msg[len(command) - 1 + spaces : ]

	if name not in users:
		await client.send_message(message.channel, "That user doesn't exist!")
		return

	users.pop(name, None)

	await client.send_message(message.channel, "Deleted.")
	print(users)

	return

async def list_users(message, command):
	user_list = "**List of Users and their IP Addresses:**\n"

	for name, ip in users.items():
		user_list += "  {name} : {ip}\n".format(name = name, ip = ip)

	await client.send_message(message.channel, user_list)
	return

async def info(message, command):
	msg = message.content
	spaces = await get_spaces(msg, command)

	is_game    = False
	is_user    = False
	is_console = False

	console = ""

	if spaces == None:
		await client.send_message(message.command, "Your argument(s) are invalid!  Use **{}help**".format(pf))
		return

	name = msg[len(command) - 1 + spaces : ]

	for key, c_game_list in consoles.items():
		if name == key:
			console = key
			is_console = True
			break

		if name not in c_game_list:
			continue

		console = key
		is_game = True

	if name in users:
		is_user = True

	if is_game:
		await client.send_message(message.channel, "**Game:         ** {name}\n**Download Link:** {link}".format(name = name, link = consoles[console][name]))
	elif is_user:
		await client.send_message(message.channel, "**Name:      ** {name}\n**IP Address:** {ip}".format(name = name, ip = users[name]))
	elif is_console:
		c_list = "**List of {console} Games:**\n".format(console = name)

		for game, link in consoles[name].items():
			c_list += "  {name} : {link}\n".format(name = game, link = link)

		await client.send_message(message.channel, c_list)
	else:
		await client.send_message(message.channel, "That entry does not exist.")

	return

async def help(message, command):
	h = ("add-console [console name]\n"
	    "    Adds a console section to the list.\n"
	    "remove-console [console name]\n"
	    "    Removes a console section from the list.\n"
	    """add-game name="[game name]" console="[console name]" link="[download link]"\n"""
	    "    Adds a game to a console.  **DON'T FORGET THE QUOTATION MARKS FOR THIS COMMAND!**\n"
	    "remove-game [game name]\n"
	    "    Removes a game.  No need to specify the console section; the bot does it automatically.\n"
	    "list-games\n"
	    "    Lists all games, from all console sections.\n"
	    """add-user name="[name]" ip="[IP Address]"\n"""
	    "    Adds a user to the list.  Like with add-game, **DON'T FORGET THE QUOTATION MARKS!**\n"
	    "remove-user [name]\n"
	    "    Removes a user from the list.\n"
	    "list-users\n"
	    "    Lists all users with an IP Address.\n"
	    "info\n"
	    "    Get information on a console, game, or user.")

	await client.send_message(message.channel, h)
	return
	

command_list = {pf + "add-console"    : add_console,
		pf + "remove-console" : remove_console,
		pf + "add-game"       : add_game,
		pf + "remove-game"    : remove_game,
		pf + "list-games"     : list_games,
		pf + "add-user"       : add_user,
		pf + "remove-user"    : remove_user,
		pf + "list-users"     : list_users,
		pf + "info"           : info,
		pf + "help"           : help}

@client.event
async def on_ready():
	print("Login successful.")
	print("Username: " + client.user.name)
	print("ID:       " + client.user.id)

@client.event
async def on_message(message):
	print("{user}: {msg}".format(user = message.author.name, msg = message.content))

	for key, function in command_list.items():
		if key in message.content:
			await function(message, key)

client.run(botToken)
