# Imports
import discord
from discord.ext import commands
from discord import app_commands, Colour
import json
import sys
import os


# Cog subclass
class RestartBot(commands.Cog):
    def __init__(self, bot):
        self.bot = (
            bot  # Allows us to use the bot outside of the __init__ function
        )
        self.bot.tree.add_command(
            restart
        )  # Register the slash command in our bot


configjson = open("config.json")
# config should be file name, () gotta be var above
config = json.load(configjson)
serverID = int(config['bot']["serverID"])
requiredRole = int(config['permissions']['admin']['restart'])
mainColor = config['brandingColors']["mainColor"]
errorColor = config['brandingColors']["errorColor"]
successColor = config['brandingColors']["successColor"]
configjson.close()


@app_commands.command(
    name="restart", description="ADMIN | Restart the bot."
)
@app_commands.checks.has_role(requiredRole)
@app_commands.guilds(serverID)
async def restart(interaction: discord.Interaction):
    def restart_bot():
        os.execv(sys.executable, ["python"] + sys.argv)

    await interaction.client.change_presence(
        status=discord.Status.idle, activity=discord.Game(name="Rebooting..")
    )  # Write the data to the db, making sure to set upsert to True incase the guild ID is not in the DB
    embed = discord.Embed(
        title="🔄 Bot rebooting",
        description=f"The bot is now rebooting.. Please wait",
        colour=Colour.from_str(mainColor),
    )
    await interaction.response.send_message(embed=embed)
    restart_bot()


@restart.error
async def ban_error(
    interaction: discord.Interaction, error: app_commands.AppCommandError
):
    if isinstance(error, app_commands.MissingRole):
        embed = discord.Embed(
            title="⛔ No permission",
            description="You do not have the required permission to run this command!",
            colour=Colour.from_str(errorColor)
        )
        embed.add_field(name="Role required:", value=f"<@&{requiredRole}>")
        await interaction.response.send_message(embed=embed)
        return
    raise error


# Sets up the cog
async def setup(bot):
    await bot.add_cog(RestartBot(bot))
