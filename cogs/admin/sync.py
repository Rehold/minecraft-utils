# Imports
import discord
from discord.ext import commands
from discord import app_commands, Colour
from typing import List
import json

# Cog subclass
class Sync(commands.Cog):
    def __init__(self, bot):
        self.bot = bot # Allows us to use the bot outside of the __init__ function
        self.bot.tree.add_command(sync) # Register the slash command in our bot


configjson = open("config.json")
# config should be file name, () gotta be var above
config = json.load(configjson)
serverID = int(config['bot']["serverID"])
requiredRole = int(config['permissions']['admin']['sync'])
mainColor = config['brandingColors']["mainColor"]
errorColor = config['brandingColors']["errorColor"]
successColor = config['brandingColors']["successColor"]
configjson.close()


@app_commands.command(name="sync", description="Sync slash commands.")
@app_commands.checks.has_role(requiredRole)
@app_commands.guilds(serverID)
async def sync(interaction: discord.Interaction):

    await interaction.client.tree.sync(guild=interaction.guild)
    embed=discord.Embed(title="🔄 Bot synced", description=f"Slash commands are now synced.", colour=0x00ff33)
    await interaction.response.send_message(embed=embed)

@sync.error
async def sync_error(
    interaction: discord.Interaction, error: app_commands.AppCommandError
):
    if isinstance(error, app_commands.MissingRole):
        embed = discord.Embed(
            title="⛔ No permission",
            description="You do not have the required permission to run this command!",
            colour=Colour.from_str(errorColor),
        )
        embed.add_field(name="Role required:", value=f"<@&{requiredRole}>")
        await interaction.response.send_message(embed=embed)
        return
    raise error

# Sets up the cog
async def setup(bot):
    await bot.add_cog(Sync(bot))