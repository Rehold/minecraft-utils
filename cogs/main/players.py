# Imports
import discord
import requests
from discord.ext import commands
from discord import app_commands, Colour
from typing import List
import json

# Cog subclass
class Players(commands.Cog):
    def __init__(self, bot):
        self.bot = bot # Allows us to use the bot outside of the __init__ function
        self.bot.tree.add_command(players) # Register the slash command in our bot


configjson = open("config.json")
# config should be file name, () gotta be var above
config = json.load(configjson)
serverID = int(config['bot']["serverID"])
serverIP = config['main']["serverIP"]
mainColor = config['brandingColors']["mainColor"]
errorColor = config['brandingColors']["errorColor"]
successColor = config['brandingColors']["successColor"]
configjson.close()


@app_commands.command(name="players", description="A list of players in the server.")
@app_commands.guilds(serverID)
async def players(interaction: discord.Interaction):

    server = requests.get(f"https://api.mcsrvstat.us/2/{serverIP}")
    server = server.json()

    if server['online'] == False:
        embed=discord.Embed(title="🔴 Server offline", description=f"The server is currently offline.", colour=Colour.from_str(errorColor))
        await interaction.response.send_message(embed=embed)
        return

    players = server['players']['list']
    players = ', '.join(players)
    if players == "":
        players = "No players online."
    if len(players) > 1024:
        players = "Too many players to display."

    embed=discord.Embed(title="👥 Players online", description=f"{players}", colour=Colour.from_str(mainColor))
    await interaction.response.send_message(embed=embed)


# Sets up the cog
async def setup(bot):
    await bot.add_cog(Players(bot))