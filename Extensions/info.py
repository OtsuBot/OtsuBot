from discord.ext import commands
import discord

class Info(commands.Cog):
    """ℹ|**to get back here**"""

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        welcome = "WELCOME TO GUILD MESSAGE"
        await guild.system_channel.send(welcome)
    
    @commands.command(brief = "`info [optional: command]` - gives brief descrition about all the commands",
                      description = "Gives a brief description about all the commands a user can access and basic information about the bot.",
                      aliases = ["help", "commands", "information"])
    async def info(self, ctx, command):
        try:
            command_obj = [i for i in Bot.commands if i.name == command.lower()][0]
        except KeyError:
            await ctx.send(f"The command {command.lower()} was not found.")
            return

        embed = discord.Embed(title = command_obj.name, color = 0x5b5f90)
        embed.add_field(name = "**Description**", value = command_obj.description)
        if len(command_obj.aliases) > 0:
            embed.add_field(name = "**Aliases**", value = ", ".join(command_obj.aliases), inline = False)
        await ctx.send(embed = embed)

    @info.error
    async def info_error(self, ctx, error):
        if type(error) == commands.errors.MissingRequiredArgument:
            emoji_to_cog = {cog.__doc__[0]: cog for cog in Bot.cogs.values()}
            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in emoji_to_cog
            emoji = "ℹ"
            message = None
            while True:
                embed = discord.Embed(title = "Information", description = "[Invite me to your server!](https://cutt.ly/otsu)\n<@713446074744045589> created by Elan\n[Join the official Otsu discord server!](https://cutt.ly/otsu_server)", color = 0x5b5f90)
                embed.set_author(name = 'Otsu', icon_url = "https://cdn.discordapp.com/attachments/713434731999658034/713454423615209502/pixelskull.png")
                if emoji == "ℹ":
                    embed.add_field(name = "**How To Use**", value = f"React with:\n{chr(10).join([cog.__doc__.replace('|', ' - ') for cog in emoji_to_cog.values()])}\n\u200b", inline = False)
                emoji_cog = emoji_to_cog[emoji]
                embed.add_field(name = f"{emoji} {emoji_cog.__cog_name__}", value = "\n".join([i.brief for i in emoji_cog.get_commands()]), inline = False)
                embed.set_footer(text = "Say _info [command name] to learn more about a command.", icon_url = "https://cdn2.iconfinder.com/data/icons/app-types-in-grey/512/info_512pxGREY.png")
                if message == None:
                    message = await ctx.send(embed = embed)
                else:
                    await message.edit(embed = embed)
                
                for emoji in emoji_to_cog:
                    await message.add_reaction(emoji)
                
                try:
                    reaction, user = await Bot.wait_for("reaction_add", timeout = 300.0, check = check)

                except:
                    return

                await reaction.remove(user)

                emoji = reaction.emoji

        else:
            raise error

    @commands.command(brief = "`invite` - gives a link to invite Otsu to a server",
                      description = "Gives a link to invite Otsu to a discord server with administrator permissions.")
    async def invite(self, ctx):
        await ctx.send("Use this link to invite me to your server!\n<https://cutt.ly/otsu>")
    
    @commands.command(brief = "`suggest [suggestion]` -  suggest a new feature/bug/change",
                      description = "Sends a message to a channel in the official Otsu discord server with the suggestion.")
    async def suggest(self, ctx, *, suggestion):
        await Bot.get_channel(729099966169088031).send(f"{ctx.author.name}#{ctx.author.discriminator}\n{suggestion}")

    @suggest.error
    async def suggest_error(self, ctx, error):
        if type(error) == commands.errors.MissingRequiredArgument:
            await ctx.send("You need to put a suggestion to suggest!")
        else:
            raise error

def setup(bot):
    global Bot
    Bot = bot
    bot.add_cog(Info(bot))
