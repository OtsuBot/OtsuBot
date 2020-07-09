from discord.ext import commands
import discord
import json

class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(brief = "kick [@member] [optional: reason] - kicks the member with the reason",
                      description = "Kicks the member and sets the audit log reason to the reason specified. Use `_setup` to create a custom kick message.")
    async def kick(self, ctx, member: discord.Member = None, *, reason = None):
        for x in [i for i in ctx.guild.text_channels if i.name == "otsu-preferences"]:
            message = (await x.history(limit = 1, oldest_first = True).flatten())[0]

            if message.content.startswith("{"):
                break

        try:
            preferences = json.loads(message.content)
            await member.send(preferences["kick dm"])

        except NameError:
            pass

        except json.decoder.JSONDecodeError:
            pass

        except KeyError:
            pass

        try:
            await member.kick(reason = reason)

        except discord.errors.Forbidden as e:
            if e.code == 50013:
                await ctx.send("I don't have permission to kick this member.")
            
            else:
                raise e

def setup(bot):
    bot.add_cog(Mod(bot))
