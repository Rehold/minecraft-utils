# Imports
import discord
from discord.ext import commands
from discord import app_commands, Colour
import platform
import psutil
import json


# Cog subclass
class BotInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = (
            bot  # Allows us to use the bot outside of the __init__ function
        )
        self.bot.tree.add_command(
            botinfo
        )  # Register the slash command in our bot


configjson = open("config.json")
# config should be file name, () gotta be var above
config = json.load(configjson)
serverID = int(config['bot']["serverID"])
mainColor = config['brandingColors']["mainColor"]
errorColor = config['brandingColors']["errorColor"]
successColor = config['brandingColors']["successColor"]
configjson.close()


# note!! need to change to cmd groups
@app_commands.command(
    name="botinfo", description="Get infomation about the bot."
)
@app_commands.guilds(serverID)
async def botinfo(interaction: discord.Interaction):
    # code

    commands = [
        cmd.name
        for cmd in interaction.client.tree.walk_commands(
            guild=discord.Object(id=serverID)
        )
    ]
    embed = discord.Embed(
        title=f":tools: {interaction.client.user.name} bot details",
        colour=Colour.from_str(mainColor),
    )
    embed.add_field(
        name="• Bot details:",
        value=f"> Uptime: <t:{interaction.client.uptime.timestamp():.0f}:R>\n> Commands loaded: {len(commands)}\n> Cogs: {str(len(interaction.client.cogs))}",
    )
    embed.add_field(
        name="• Softwere details:",
        value=f"> Python version: {platform.python_version()}\n> Discord version: {discord.__version__}",
    )
    embed.add_field(
        name="• Server details:",
        value=f"> CPU: {psutil.cpu_percent()}%\n> RAM: {round(psutil.virtual_memory().available * 100 / psutil.virtual_memory().total)}%",
    )
    embed.add_field(
        name="• Developers:",
        value="> <@842859032628822057>",
    )
    await interaction.response.send_message(embed=embed)


# Sets up the cog
async def setup(bot):
    await bot.add_cog(BotInfo(bot))
