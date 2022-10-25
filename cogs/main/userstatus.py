# Imports
import discord
import requests
from discord.ext import commands
from discord import app_commands, Colour
from typing import List
import json

# Cog subclass
class UserStatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot # Allows us to use the bot outside of the __init__ function
        self.bot.tree.add_command(userstatus) # Register the slash command in our bot


configjson = open("config.json")
# config should be file name, () gotta be var above
config = json.load(configjson)
serverID = int(config['bot']["serverID"])
serverIP = config['main']["minecraftIP"]
mainColor = config['brandingColors']["mainColor"]
errorColor = config['brandingColors']["errorColor"]
successColor = config['brandingColors']["successColor"]
configjson.close()


@app_commands.command(name="userstatus", description="Info about a user in the server.")
@app_commands.guilds(serverID)
async def userstatus(interaction: discord.Interaction, ign: str):

    server = requests.get(f"https://api.mcsrvstat.us/2/{serverIP}")
    server = server.json()

    if server['online'] == False:
        embed=discord.Embed(title="🔴 Server offline", description=f"The server is currently offline.", colour=Colour.from_str(errorColor))
        await interaction.response.send_message(embed=embed)
        return

    if 'list' not in server['players']:
        embed=discord.Embed(title="🔴 Server offline", description=f"The server is currently offline.", colour=Colour.from_str(errorColor))
        await interaction.response.send_message(embed=embed)
        return
    if ign not in server['players']['list']:
        embed=discord.Embed(title="🔴 User not found", description=f"The user {ign} was not found in the server.", colour=Colour.from_str(errorColor))
        await interaction.response.send_message(embed=embed)
        return

    embed = discord.Embed(title="👥 User status", description=f"User {ign} was found in the server.", colour=Colour.from_str(mainColor))



# Sets up the cog
async def setup(bot):
    await bot.add_cog(UserStatus(bot))