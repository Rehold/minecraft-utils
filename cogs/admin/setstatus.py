# Imports
import discord
from discord.ext import commands
from discord import app_commands, Colour
from typing import List
import json


# Cog subclass
class SetStatus(commands.Cog):
    def __init__(self, bot):
        self.bot = (
            bot  # Allows us to use the bot outside of the __init__ function
        )
        self.bot.tree.add_command(
            setstatus
        )  # Register the slash command in our bot




configjson = open("config.json")
# config should be file name, () gotta be var above
config = json.load(configjson)
serverID = int(config['bot']["serverID"])
requiredRole = int(config['permissions']['admin']['setstatus'])
mainColor = config['brandingColors']["mainColor"]
errorColor = config['brandingColors']["errorColor"]
successColor = config['brandingColors']["successColor"]
configjson.close()


@app_commands.command(
    name="setstatus", description="ADMIN | Edit the status of the bot."
)
@app_commands.checks.has_role(requiredRole)
@app_commands.describe(status="The status to change too.")
@app_commands.describe(type="The type of status to change too.")
@app_commands.guilds(serverID)
async def setstatus(interaction: discord.Interaction, type: str, status: str):
    statusdict = {"botstatus": {"status": status, "type": type}}
    await interaction.client.database.botinfo.update_one(
        {"_botid": interaction.client.user.id},
        {"$set": statusdict},
        upsert=True,
    )
    statusdb = await interaction.client.database.botinfo.find_one(
        {"_botid": interaction.client.user.id}
    )
    await interaction.client.change_presence(
        activity=discord.Activity(
            name=statusdb["botstatus"]["status"],
            type=discord.ActivityType.listening
            if statusdb["botstatus"]["type"] == "Listening"
            else (
                discord.ActivityType.watching
                if statusdb["botstatus"]["type"] == "Watching"
                else discord.ActivityType.playing
            ),
        )
    )  # Write the data to the db, making sure to set upsert to True incase the guild ID is not in the DB
    embed = discord.Embed(
        title=":white_check_mark: Bot status updated",
        description=f"The bot's status is now: **{type} {'to' if type == 'Listening' else ''}** {status}",
        colour=Colour.from_str(mainColor),
    )
    await interaction.response.send_message(embed=embed)


@setstatus.autocomplete("type")
async def status_autocomplete(
    interaction: discord.Interaction, current: str
) -> List[app_commands.Choice[str]]:
    options = ["Playing", "Listening", "Watching"]
    return [
        app_commands.Choice(name=option, value=option)
        for option in options
        if current.lower() in option.lower()
    ]


@setstatus.error
async def setstatus_error(
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
    await bot.add_cog(SetStatus(bot))
