# Imports
import discord
import requests
from discord.ext import commands
from discord import app_commands, Colour
from typing import List
import json


# Cog subclass
class ServerStatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  # Allows us to use the bot outside of the __init__ function
        self.bot.tree.add_command(serverstatus)  # Register the slash command in our bot


configjson = open("config.json")
# config should be file name, () gotta be var above
config = json.load(configjson)
serverID = int(config['bot']["serverID"])
serverIP = config['main']["minecraftIP"]
mainColor = config['brandingColors']["mainColor"]
errorColor = config['brandingColors']["errorColor"]
successColor = config['brandingColors']["successColor"]
configjson.close()


@app_commands.command(name="serverstatus", description="The status of the server.")
@app_commands.guilds(serverID)
async def serverstatus(interaction: discord.Interaction):

        server = requests.get(f"https://api.mcsrvstat.us/2/{serverIP}")
        server = server.json()
        if server['online'] == False:
            embed=discord.Embed(title="📊 Server status", description=f"The server is currently offline.", colour=Colour.from_str(errorColor))
            embed.add_field(name='• Players online', value=f"🔴 Server offline")
            embed.add_field(name='• Server IP', value=f"🔴 Server offline")
            embed.add_field(name='• Server version', value=f"🔴 Server offline")
            embed.add_field(name='• Server MOTD', value=f"🔴 Server offline")
            await interaction.response.send_message(embed=embed)
            return

        embed = discord.Embed(title="📊 Server status", colour=Colour.from_str(mainColor))
        embed.add_field(name='• Players online', value=f"{server['players']['online']}/{server['players']['max']}")
        embed.add_field(name='• Server IP', value=f"{serverIP}")
        embed.add_field(name='• Server version', value=f"{server['version']}")
        embed.add_field(name='• Server MOTD', value=f"{server['motd']['clean'][0]}")

        await interaction.response.send_message(embed=embed)


# Sets up the cog
async def setup(bot):
    await bot.add_cog(ServerStatus(bot))