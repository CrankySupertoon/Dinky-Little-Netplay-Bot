import asyncio
import discord
import re

# response constants
ENTRY_EXIST                 = "The {ent} entry exists already!"
ENTRY_NOT_EXIST             = "The {ent} entry does not exist!"
ADD_SUCCES                  = "{ent} entry created successfully."
DELETE_SUCCESS              = "Deleted."
INVALID_ARG                 = "Invalid or missing argument(s) passed!  Use {pf}help for more info."

# regex constants for reading commands and other stuff
MULTI_ARG_RE = re.compile(r"""(\w+)\s*=\s*["'](.+?)["']""")

BUILTIN_FUNC_RE = re.compile(r"__[.+]__")

# function for sending responses to commands
async def rs(client, resp, channel, prefix = None, entry = None):
	str_formatted = resp.format(ent = entry, pf = prefix)

	await client.send_message(channel, str_formatted)
	return

# class for handling arguments made to the bot
# this is used primarily for organization, keeping
# certain groups of arguments organized
# Each instance also runs asynchronously
class ArgumentHandler(discord.Client):
	def __init__(self, prefix, guild):
		super(ArgumentHandler, self).__init__()

		self.pf    = prefix
		self.guild = guild

		self.cmd_dic = self.get_commands()

		print("{} handler set up".format(self.__class__.__name__))
		print(self.cmd_dic)

	# gets a list of functions exclusive to a class, then turns them into bot-usable commands
	def get_commands(self):
		ah_cmd_list = dir(self.__class__)
		dc_cmd_list = dir(discord.Client)
		sp_cmd_list = dir(super(self.__class__, self))

		cmd_dic = {}

		for cmd in ah_cmd_list:
			if   cmd in dc_cmd_list: 
				continue
			elif cmd in sp_cmd_list:
				continue
			else:
				cmd_name = cmd.replace("_", "-")
				cmd_dic[cmd_name] = getattr(self, cmd)

		return cmd_dic

	async def on_message(self, message):
		if message.author.id == self.user.id:
			return

		await self.send_message(message.channel, "You said: \"{}\"".format(message.content))

if __name__ == "__main__":
	test = ArgumentHandler("$", "insert guild id")

	test.run("testing token")
