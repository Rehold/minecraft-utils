# Imports
import discord
import requests
from discord.ext import commands, tasks
from discord import app_commands, Colour
import json

configjson = open("config.json")
# config should be file name, () gotta be var above
config = json.load(configjson)
serverID = int(config['bot']["serverID"])
serverIP = config['main']["serverIP"]
logChannel = int(config['channels']['main']['mcJoinLog'])
mainColor = config['brandingColors']["mainColor"]
errorColor = config['brandingColors']["errorColor"]
successColor = config['brandingColors']["successColor"]
configjson.close()

dbjson = open("config.json")
db = json.load(configjson)
dbjson.close()


class UserLeaveMCServer(commands.Cog):
    def __init__(self, bot):
        self.bot = (
            bot  # Allows us to use the bot outside of the __init__ function
        )

    async def cog_load(self):
        self.minecraft_userleave.start()

    async def cog_unload(self):
        self.minecraft_userleave.cancel()

    @tasks.loop(minutes=3)
    async def minecraft_userleave(self):
        if logChannel == "":
            return
        server = requests.get(f"https://api.mcsrvstat.us/2/{serverIP}")
        server = server.json()

        channelVar = self.bot.get_channel(logChannel) or await self.bot.fetch_channel(logChannel)

        if server['online'] == False:
            return
        else:
            for player in db['main']['lastPlayerUpdate']:
                if player in server['players']['list']:
                    return
                else:
                    embed = discord.Embed(title="Player left", description=f"{player} left the server", color=Colour.from_str(mainColor))
                    await channelVar.send(embed=embed)
                    db['main']['lastPlayerUpdate'].remove(player)
                    dbjson = open("config.json", "w")
                    json.dump(db, dbjson)
                    dbjson.close()


# Sets up the cog
async def setup(bot):
    await bot.add_cog(UserLeaveMCServer(bot))