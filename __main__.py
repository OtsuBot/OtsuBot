from discord.ext import commands
import discord
import manifest
import ctypes

ctypes.windll.kernel32.SetConsoleTitleW(manifest["terminal name"])

bot = commands.Bot(command_prefix = manifest.prefix])

bot.remove_command("help")
[bot.load_extension("Extensions." + extension) for extension in ["info", "credits", "gaming"]]

@bot.event
async def on_ready():
    await bot.change_presence(status = discord.Status.online, activity = discord.Activity(type = discord.ActivityType.listening, name = "$info"))
    print(manifest.ready_message])

bot.run(manifest.token])
