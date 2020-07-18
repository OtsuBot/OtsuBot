from discord.ext import commands
import discord
from Extensions import functions as functs

class Credits(commands.Cog):
    """💰|**to see credit moving comands**"""

    @commands.command(brief = "`daily` - collects a daily bonus",
                      description = "Awards 500 credits. This command has a 12 hour cooldown.")
    @commands.cooldown(1, 43200, commands.BucketType.user)
    async def daily(self, ctx):
        functs.update_balance(ctx.author.id, 500)

        await ctx.send("You have been awarded your daily **500** credits.")

    @daily.error
    async def daily_error(self, ctx, error):
        if type(error) == commands.CommandOnCooldown:
            msg = str(error)[34:-1]
            msg = round(float(msg))
            min, sec = divmod(msg, 60)
            hour, min = divmod(min, 60)

            if hour > 0:
                await ctx.send(f"You can't use this command for {hour} hours, {min} minutes, and {sec} seconds.")

            else:
                if min > 0:
                    await ctx.send(f"You can't use this command for {min} minutes and {sec} seconds.")

                else:
                    await ctx.send(f"You can't use this command for {sec} seconds.")

        else:
            raise error

    @commands.command(brief = "`balance [optional: member]` - returns your balance",
                      description = "Returns your hand balance, bank balance, and net worth. If given, returns that of the given member.",
                      aliases = ["bal"])
    async def balance(self, ctx, member: discord.Member = None):
        if member == None:
            member = ctx.author

        hand_bal = functs.get_balance(member.id)
        bank_bal = functs.get_bank_balance(member.id)

        embed = discord.Embed(title = f"{member.display_name}'s Balance", description = f'Net worth: {hand_bal + bank_bal}', color = 0x5b5f90)
        embed.add_field(name = "**Hand Balance**", value = str(hand_bal), inline = False)
        embed.add_field(name = "**Bank Balance**", value = str(bank_bal), inline = False)
        await ctx.send(embed = embed)

    @balance.error
    async def balance_error(self, ctx, error):
        if type(error) == commands.errors.BadArgument:
            await ctx.send("Make sure you @ a valid member.")

        else:
            raise error

    @commands.command(brief = "`deposit [amount]` - moves credits from the hand to the bank",
                      description = "Takes credits out of your hand and puts them in your bank account. Saying `_deposit all` will deposit all credits in hand.",
                      aliases = ["dep"])
    async def deposit(self, ctx, amount):
        if amount.lower() == "all":
            bal = functs.get_balance(ctx.author.id)

            if bal == 0:
                await ctx.send("You don't have any credits on hand.")
                return

            functs.update_balance(ctx.author.id, -bal)
            functs.update_bank_balance(ctx.author.id, bal)

            await ctx.send(f"Successfully deposited **{bal}** credits to the bank.")
            return

        messages = {"NotAFloat": "The amount you deposit must be a number.",
                    "MoreThanTwoDecimals": "You can only deposit credits up to the second decimal place.",
                    "LessThanOrEqualToZero": "You can only deposit an amount over 0.\nUse `_withdraw [amount]` to take credits from the bank."}
        if await functs.invalid_credit_amount(ctx, amount, messages):
            return

        bal = functs.get_balance(ctx.author.id)
        amount = float(amount)
        if amount > bal:
            await ctx.send(f"You don't have that many credits on hand. You only have {bal} credits.")
            return

        functs.update_balance(ctx.author.id, -amount)
        functs.update_bank_balance(ctx.author.id, amount)

        await ctx.send(f"Successfully deposited **{amount}** credits to the bank.")

    @deposit.error
    async def deposit_error(self, ctx, error):
        error_type = type(error)
        if error_type == commands.errors.MissingRequiredArgument:
            await ctx.send("You must specfy an amount to deposit to the bank, or to deposit everything on hand, say `_deposit all`.")

        else:
            raise error

    @commands.command(brief = "`withdraw [amount]` - moves credits from the bank to the hand",
                      description = "Takes credits out of your bank account and puts them in your hand. Saying `_withdraw all` will withdraw all credits from the bank.",
                      aliases = ["with"])
    async def withdraw(self, ctx, amount):
        if amount.lower() == "all":
            bal = functs.get_bank_balance(ctx.author.id)
            if bal == 0:
                await ctx.send("You don't have any credits in the bank.")
                return

            functs.update_bank_balance(ctx.author.id, -bal)
            functs.update_balance(ctx.author.id, bal)

            await ctx.send(f"Successfully withdrew **{bal}** credits from the bank.")
            return

        messages = {"NotAFloat": "The amount you withdraw must be a number.",
                    "MoreThanTwoDecimals": "The amount of credits you withdraw can only go up to the second decimal place.",
                    "LessThanOrEqualToZero": "You can only withdraw an amount over 0.\nUse `_deposit [amount]` to put your credits into the bank."}
        if await functs.invalid_credit_amount(ctx, amount, messages):
            return

        bal = functs.get_bank_balance(ctx.author.id)
        amount = float(amount)
        if amount > bal:
            await ctx.send(f"You don't have that many credits in the bank. You only have {bal} credits.")
            return

        functs.update_bank_balance(ctx.author.id, -amount)
        functs.update_balance(ctx.author.id, amount)

        await ctx.send(f"Successfully withdrew **{amount}** credits from the bank.")

    @withdraw.error
    async def withdraw_error(self, ctx, error):
        if type(error) == commands.errors.MissingRequiredArgument:
            await ctx.send("You must specfy an amount to withdraw from the bank, or to withdraw everything, say `_withdraw all`.")

        else:
            raise error

    @commands.command(brief = "`give [member] [amount]` - gives the member the amount of credits",
                      description = "Takes the amount of credits out of your hand and into the member's hand.")
    async def give(self, ctx, member: discord.Member, amount):
        messages = {"NotAFloat": "The amount you give must be a number.",
                    "MoreThanTwoDecimals": "The amount you give can only go up to the second decimal place.",
                    "LessThanOrEqualToZero": "You can only give an amount over 0."}
        if await functs.invalid_credit_amount(ctx, amount, messages):
            return

        bal = functs.get_balance(ctx.author.id)
        amount = float(amount)
        if amount > bal:
            await ctx.send(f"You don't have that many credits in your hand. You only have {bal} credits.")
            return
        
        functs.update_balance(ctx.author.id, -amount)
        functs.update_balance(member.id, amount)

        await ctx.send(f"{ctx.author.mention} gave {member.mention} **{amount}** credits!")

    @give.error
    async def give_error(self, ctx, error):
        error_type = type(error)

        if error_type == commands.errors.MissingRequiredArgument:
            if error.param.name == "member":
                await ctx.send("You have to specify a member to give the credits to.")

            elif error.param.name == "amount":
                await ctx.send("You have to specify a credit amount to give the member.")

        elif error_type == commands.errors.BadArgument:
            await ctx.send("Make sure you @ a valid member.")

        else:
            raise error

def setup(bot):
    global Bot
    Bot = bot
    bot.add_cog(Credits(bot))
