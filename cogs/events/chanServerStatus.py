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
updateChannel = int(config['channels']['main']['serverStatus'])
mainColor = config['brandingColors']["mainColor"]
errorColor = config['brandingColors']["errorColor"]
successColor = config['brandingColors']["successColor"]
configjson.close()

class ChannelMcStatus(commands.Cog):
    def __init__(self, bot):
        self.bot = (
            bot  # Allows us to use the bot outside of the __init__ function
        )

    async def cog_load(self):
        self.minecraft_count.start()

    async def cog_unload(self):
        self.minecraft_count.cancel()





    @tasks.loop(minutes=3)
    async def minecraft_count(self):
        if updateChannel == "":
            return
        server = requests.get(f"https://api.mcsrvstat.us/2/{serverIP}")
        server = server.json()

        channelVar = self.bot.get_channel(updateChannel) or await self.bot.fetch_channel(updateChannel)

        if server['online'] == False:
            await channelVar.edit(name=f"[🔴] Server offline")
        else:
            await channelVar.edit(name=f"[🟢] Players online: {str(server['players']['online'])}")


# Sets up the cog
async def setup(bot):
    await bot.add_cog(ChannelMcStatus(bot))