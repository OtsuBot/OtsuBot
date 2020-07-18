from discord.ext import commands
import discord
import json
from Extensions import functions as functs

class Mod(commands.Cog):
    """🛠️|**to see mod commands**"""

    @commands.group(brief = "`setup` - creates a channel that stores customizable preferences",
                    description = "Creates a preferences channel to edit server-custom messages when certain commands are used.")
    async def setup(self, ctx):
        if ctx.invoked_subcommand == None:
            await ctx.send("Say `_setup` new to create a new preferences channel.\nTo edit the server's preferences:\n    `_setup new` - creates the channel that holds the preferences (this will only be visible to members with the highest role)\n\n    `_setup kick_dm [dm message]` - the dm sent to the member when they are kicked\n    `_setup ban_dm [dm message]` - the dm sent to the member when they are banned\n    `_setup member_join_message [message]` - the message sent to a channel when a member joins\n    `_setup member_join_message_channel [channel]` - the channel the join message is sent to (the message will not be sent without this)")

    @setup.command()
    @commands.bot_has_permissions(manage_channels = True)
    async def new(self, ctx):
        await ctx.send("This command will make a new text channel. Do you want to proceed?\nSay `yes` to confirm or `no` to cancel.")

        def check(message):
            return message.author == ctx.author and message.content.lower().strip() in ["yes", "no"]

        answer = None
        try:
            answer = await Bot.wait_for("message", timeout = 300, check = check)

        except:
            return

        if answer.content.lower().strip() == "no":
            return

        overwrites = {ctx.guild.default_role: discord.PermissionOverwrite(read_messages = False),
                      ctx.guild.me: discord.PermissionOverwrite(read_messages = True),
                      ctx.guild.roles[-1]: discord.PermissionOverwrite(read_messages = True)}
        channel = await ctx.guild.create_text_channel("otsu-preferences", overwrites = overwrites)

        await channel.send('{\n    "kick_dm": "",\n    "ban_dm": "",\n    "member_join_message": "",\n    "member_join_message_channel": 0\n}')

    @new.error
    async def new_error(self, ctx, error):
        if type(error) == commands.MissingPermissions:
            await ctx.send("I need the manage channels permission to do this.")
        
        else:
            raise error

    @setup.command()
    async def kick_dm(self, ctx, *, dm_message):
        preferences, message = await functs.get_preferences_json(ctx.guild)
        if preferences == None:
            return

        try:
            preferences["kick_dm"] = await functs.json_filter(dm_message)
            await message.edit(content = json.dumps(preferences, indent = 4))

        except KeyError:
            await ctx.send("Make sure you have a preferences channel set up using the command `_setup new`.\nNote: the channel must be named 'otsu-preferences' to function.")

        else:
            await ctx.message.add_reaction("✅")

    @kick_dm.error
    async def kick_dm_error(self, ctx, error):
        if type(error) == commands.errors.MissingRequiredArgument:
            await ctx.send("You need to specify a message to dm.")
        
        else:
            raise error

    @commands.command(brief = "`kick [@member] [optional: reason]` - kicks the member with the reason",
                      description = "Kicks the member and sets the audit log reason to the reason specified. Use `_setup` to create a custom kick message.")
    @commands.bot_has_permissions(kick_members = True)
    async def kick(self, ctx, member: discord.Member, *, reason = None):
        preferences, message = await functs.get_preferences_json(ctx.guild)
        if preferences == None:
            return

        try:
            preferences = json.loads(message.content)
            await member.send(await functs.escape_character_replace(preferences["kick_dm"]))

        except KeyError:
            pass

        try:
            await member.kick(reason = reason)

        except discord.errors.Forbidden as e:
            if e.code == 50013:
                await ctx.send("I don't have permission to kick this member.")

            else:
                raise e

    @kick.error
    async def kick_error(self, ctx, error):
        error_type = type(error)

        if error_type == commands.MissingPermissions:
            await ctx.send("I need the `kick members` permission to do this.")

        elif error_type == commands.errors.MissingRequiredArgument:
            await ctx.send("You have to specify a member to kick.")

        elif error_type == commands.errors.BadArgument:
            await ctx.send("Make sure you @ a valid member.")

        else:
            raise error

    @setup.command()
    async def ban_dm(self, ctx, *, dm_message):
        preferences, message = await functs.get_preferences_json(ctx.guild)
        if preferences == None:
            return

        try:
            preferences["ban_dm"] = await functs.json_filter(dm_message)
            await message.edit(content = json.dumps(preferences, indent = 4))

        except KeyError:
            await ctx.send("Make sure you have a preferences channel set up using the command `_setup new`.\nNote: the channel must be named 'otsu-preferences' to function.")
        
        else:
            await ctx.message.add_reaction("✅")
    
    @ban_dm.error
    async def ban_dm_error(self, ctx, error):
        if type(error) == commands.errors.MissingRequiredArgument:
            await ctx.send("You need to specify a message to dm.")
        
        else:
            raise error

    @commands.command(brief = "`ban [@member] [optional: reason]` - bans the member with the reason",
                      description = "Bans the member and sets the audit log reason to the reason specified. Use `_setup` to create a custom ban message.")
    @commands.bot_has_permissions(ban_members = True)
    async def ban(self, ctx, member: discord.Member, *, reason = None):
        preferences, message = await functs.get_preferences_json(ctx.guild)
        if preferences == None:
            return

        try:
            preferences = json.loads(message.content)
            await member.send(await functs.escape_character_replace(preferences["ban_dm"]))

        except discord.errors.HTTPException as e:
            if e.code != 50006:
                raise e

        except KeyError:
            pass

        try:
            await member.ban(reason = reason)

        except discord.errors.Forbidden as e:
            if e.code == 50013:
                await ctx.send("I don't have permission to ban this member.")

            else:
                raise e

    @ban.error
    async def ban_error(self, ctx, error):
        error_type = type(error)

        if error_type == commands.MissingPermissions:
            await ctx.send("I need the `ban members` permission to do this.")

        elif error_type == commands.errors.MissingRequiredArgument:
            await ctx.send("You have to specify a member to ban.")

        elif error_type == commands.errors.BadArgument:
            await ctx.send("Make sure you @ a valid member.")

        else:
            raise error

    @setup.command()
    async def member_join_message(self, ctx, *, c_message):
        preferences, message = await functs.get_preferences_json(ctx.guild)
        if preferences == None:
            return

        try:
            preferences["member_join_message"] = await functs.json_filter(c_message)
            await message.edit(content = json.dumps(preferences, indent = 4))

        except KeyError:
            await ctx.send("Make sure you have a preferences channel set up using the command `_setup new`.\nNote: the channel must be named 'otsu-preferences' to function.")
        
        else:
            await ctx.message.add_reaction("✅")
    
    @member_join_message.error
    async def member_join_message_error(self, ctx, error):
        if type(error) == commands.errors.MissingRequiredArgument:
            await ctx.send("You need to specify a message to send.")
        
        else:
            raise error

    @setup.command()
    async def member_join_message_channel(self, ctx, *, channel: discord.TextChannel):
        preferences, message = await functs.get_preferences_json(ctx.guild)
        if preferences == None:
            return

        try:
            preferences["member_join_message_channel"] = channel.id
            await message.edit(content = json.dumps(preferences, indent = 4))

        except KeyError:
            await ctx.send("Make sure you have a preferences channel set up using the command `_setup new`.\nNote: the channel must be named 'otsu-preferences' to function.")
        
        else:
            await ctx.message.add_reaction("✅")
    
    @member_join_message_channel.error
    async def member_join_message_channel_error(self, ctx, error):
        error_type = type(error)

        if error_type == commands.errors.MissingRequiredArgument:
            await ctx.send("You need to specify a channel to send the message to.")

        elif error_type == commands.errors.BadArgument:
            await ctx.send("Make sure you #ed a channel in this server.")

        else:
            raise error

    @commands.Cog.listener()
    async def on_member_join(self, member):
        preferences, message = await functs.get_preferences_json(member.guild)
        if preferences == None:
            return

        try:
            preferences = json.loads(message.content)
            await member.guild.get_channel(preferences["member_join_message_channel"]).send(await functs.escape_character_replace(preferences["member_join_message"]))

        except AttributeError:
            pass

        except discord.errors.HTTPException as e:
            if e.code != 50006:
                raise e

        except KeyError:
            pass

def setup(bot):
    global Bot
    Bot = bot
    bot.add_cog(Mod())
