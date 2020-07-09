from discord.ext import commands
import discord
import Extensions.functions as functs
import requests
import random

class Gaming(commands.Cog):
    def __init__(self, bot, words):
        self.bot = bot
        self.words = words

    @commands.command(brief = "`hangman [optional: bet]` - starts a game of hangman",
                      description = "Starts a game of hangman. The goal of the game is to guess letters until you know the word, then to either guess the word or finish guessing the letters. To play, type +c to guess the letter c and +cat to guess the word cat. If a bet is provided (a number), you will be rewarded that many credits if you guess the entire word. Otherwise, you lose that many credits. Saying 'open' after _hangman [bet] makes the game public, and anyone can guess using -c and -cat instead of +c and +cat.",
                      aliases = ["hm"])
    async def hangman(self, ctx, bet = None):
        if bet != None:
            messages = {"NotAFloat": "Your bet must be a number.",
                        "MoreThanTwoDecimals": "Your bet cannot go past 2 decimal places.",
                        "LessThanOrEqualToZero": "Your bet must be over 0 credits."}
            if await functs.invalid_credit_amount(ctx, bet, messages):
                return

            bal = functs.get_balance(ctx.author.id)
            bet = float(bet)
            if bet > bal:
                await ctx.send(f"You don't have that many credits! You have {bal} credits on hand.")
                return

        if f"hm_{ctx.author.id}" in globals():
            await ctx.send("You're already playing hangman! Finish the game or wait 5 minutes for that game to automatically end.")
            return

        exec(f"global hm_{ctx.author.id}; hm_{ctx.author.id} = None")

        if bet != None:
            functs.update_balance(ctx.author.id, -bet)

        definition = None
        while definition in [None, "ang="]:
            rand_num = random.randint(0, 209785)
            word = self.words[rand_num:rand_num + 60]
            word = word[word.find("\n") + 1:]
            word = word[:word.find("\n")]

            data = requests.get(f"https://www.merriam-webster.com/dictionary/{word}").text

            definition = data[data.find("\"description\" content=\"") + 23:]
            definition = definition[:definition.find("\"")]

        word = word.lower()

        word_message = ["#" if i.isalpha() else i for i in word]
        title = f"Hangman | {ctx.author.display_name}"
        footer = "Say +c to guess the letter c.\nSay +cat to guess the word cat."
        lives_message = ["❤"] * 10
        letters_guessed = []
        won_game_msg = f"You won {bet} credits!" if bet != None else "You won!"
        lost_game_msg = f"You lost {bet} credits." if bet != None else "You lost."

        embed = discord.Embed(title = title, description = "Let's play hangman! Here's your word.", color = 0x23272a)
        embed.add_field(name = "**Word**", value = " ".join(word_message), inline = False)
        embed.add_field(name = "**Lives**", value = " ".join(lives_message), inline = False)
        embed.set_footer(text = footer, icon_url = 'https://cdn2.iconfinder.com/data/icons/app-types-in-grey/512/info_512pxGREY.png')
        await ctx.send(embed = embed)

        def check(message):
            return message.content.startswith("+") and message.author == ctx.author and len(message.content.strip()) > 1
        
        while True:
            try:
                guess = await self.bot.wait_for("message", timeout = 300, check = check)

            except:
                exec(f"del hm_{ctx.author.id}", globals())

                await ctx.send(f"5 minute timer: {ctx.author.mention}'s game has ended.")
                return
            
            content = guess.content[1:].strip().lower()

            if len(content) == 1:
                if content in letters_guessed:
                    embed = discord.Embed(title = title, description = "You already guessed that!", color = 0x23272a)
                    embed.add_field(name = "**Word**", value = " ".join(word_message), inline = False)
                    embed.add_field(name = "**Lives**", value = " ".join(lives_message), inline = False)
                    embed.add_field(name = "**Letters Guessed**", value = ", ".join(letters_guessed), inline = False)
                    embed.set_footer(text = footer, icon_url = 'https://cdn2.iconfinder.com/data/icons/app-types-in-grey/512/info_512pxGREY.png')
                    await ctx.send(embed = embed)

                elif content in word:
                    letters_guessed.append(content)

                    for x in [i for i, letter in enumerate(word) if letter == content]:
                        word_message[x] = content

                    if "".join(word_message) == word:
                        embed = discord.Embed(title = title, description = won_game_msg, color = 0x00ff00)
                        embed.add_field(name = "**Word**", value = " ".join(word), inline = False)
                        embed.add_field(name = "**Definition**", value = definition, inline = False)
                        embed.add_field(name = "**Lives**", value = " ".join(lives_message), inline = False)
                        await ctx.send(embed = embed)

                        if bet != None:
                            await functs.update_balance(ctx.author.id, bet * 2)

                        exec(f"del hm_{ctx.author.id}", globals())
                        return

                    embed = discord.Embed(title = title, description = f"Nice guess! Letter `{content}` is in the word.", color = 0x00ff00)
                    embed.add_field(name = "**Word**", value = " ".join(word_message), inline = False)
                    embed.add_field(name = "**Lives**", value = " ".join(lives_message), inline = False)
                    embed.add_field(name = "**Letters Guessed**", value = ", ".join(letters_guessed), inline = False)
                    embed.set_footer(text = footer, icon_url = 'https://cdn2.iconfinder.com/data/icons/app-types-in-grey/512/info_512pxGREY.png')
                    await ctx.send(embed = embed)

                else:
                    letters_guessed.append(content)

                    lives_message[-lives_message.count('❌') - 1] = '❌'

                    if lives_message.count('❤') == 0:
                        embed = discord.Embed(title = title, description = lost_game_msg, color = 0xff0000)
                        embed.add_field(name = "**Word**", value = " ".join(word), inline = False)
                        embed.add_field(name = "**Definition**", value = definition, inline = False)
                        embed.add_field(name = "**Lives**", value = " ".join(lives_message), inline = False)
                        await ctx.send(embed = embed)

                        exec(f"del hm_{ctx.author.id}", globals())
                        return

                    embed = discord.Embed(title = title, description = f"Oops! Letter `{content}` is not in the word.", color = 0xff0000)
                    embed.add_field(name = "**Word**", value = " ".join(word_message), inline = False)
                    embed.add_field(name = "**Lives**", value = " ".join(lives_message), inline = False)
                    embed.add_field(name = "**Letters Guessed**", value = ", ".join(letters_guessed), inline = False)
                    embed.set_footer(text = footer, icon_url = 'https://cdn2.iconfinder.com/data/icons/app-types-in-grey/512/info_512pxGREY.png')
                    await ctx.send(embed = embed)

            else:
                if word == content:
                    embed = discord.Embed(title = title, description = won_game_msg, color = 0x00ff00)
                    embed.add_field(name = "**Word**", value = " ".join(word), inline = False)
                    embed.add_field(name = "**Definition**", value = definition, inline = False)
                    embed.add_field(name = "**Lives**", value = " ".join(lives_message), inline = False)
                    await ctx.send(embed = embed)

                    if bet != None:
                        await functs.update_balance(ctx.author.id, bet * 2)

                    exec(f"del hm_{ctx.author.id}", globals())
                    return

                lives_message[-lives_message.count('❌') - 1] = '❌'

                if lives_message.count('❤') == 0:
                    embed = discord.Embed(title = title, description = lost_game_msg, color = 0xff0000)
                    embed.add_field(name = "**Word**", value = " ".join(word), inline = False)
                    embed.add_field(name = "**Definition**", value = definition, inline = False)
                    embed.add_field(name = "**Lives**", value = " ".join(lives_message), inline = False)
                    await ctx.send(embed = embed)

                    exec(f"del hm_{ctx.author.id}", globals())
                    return

                embed = discord.Embed(title = title, description = "Oops! That's not the word!", color = 0xff0000)
                embed.add_field(name = "**Word**", value = " ".join(word_message), inline = False)
                embed.add_field(name = "**Lives**", value = " ".join(lives_message), inline = False)
                if letters_guessed != []:
                    embed.add_field(name = "**Letters Guessed**", value = ", ".join(letters_guessed), inline = False)
                embed.set_footer(text = footer, icon_url = 'https://cdn2.iconfinder.com/data/icons/app-types-in-grey/512/info_512pxGREY.png')
                await ctx.send(embed = embed)

    @commands.command(brief = "`anagram [optional: bet]` - starts a game of anagram",
                      description = "Starts a game of anagram. The goal of the game is to guess a randomly scrambled word. To play, type +cat to guess the word cat. If a bet is provided (a number), you will be rewarded that many credits if you guess the word. Otherwise, you lose that many credits.",
                      aliases = ["ag"])
    async def anagram(self, ctx, bet = None):
        if bet != None:
            messages = {"NotAFloat": "Your bet must be a number.",
                        "MoreThanTwoDecimals": "Your bet cannot go past 2 decimal places.",
                        "LessThanOrEqualToZero": "Your bet must be over 0 credits."}
            if await functs.invalid_credit_amount(ctx, bet, messages):
                return

            bal = functs.get_balance(ctx.author.id)
            bet = float(bet)
            if bet > bal:
                await ctx.send(f"You don't have that many credits! You have {bal} credits on hand.")
                return

        if f"hm_{ctx.author.id}" in globals():
            await ctx.send("You're already playing hangman! Finish the game or wait 5 minutes for that game to automatically end.")
            return

        exec(f"global hm_{ctx.author.id}; hm_{ctx.author.id} = None")

        if bet != None:
            functs.update_balance(ctx.author.id, -bet)

        definition = None
        while definition in [None, "ang="]:
            rand_num = random.randint(0, 209785)
            word = self.words[rand_num:rand_num + 60]
            word = word[word.find("\n") + 1:]
            word = word[:word.find("\n")]

            data = requests.get(f"https://www.merriam-webster.com/dictionary/{word}").text

            definition = data[data.find("\"description\" content=\"") + 23:]
            definition = definition[:definition.find("\"")]

        word = word.lower()

        scrambled = list(word)
        random.shuffle(scrambled)
        title = f"Anagram | {ctx.author.display_name}"
        footer = "Say +cat to guess the word cat."
        lives_message = ["❤"] * 3
        won_game_msg = f"You won {bet} credits!" if bet != None else "You won!"
        lost_game_msg = f"You lost {bet} credits." if bet != None else "You lost."

        embed = discord.Embed(title = title, description = "Let's play anagram! Try to unscramble this word.", color = 0x23272a)
        embed.add_field(name = "**Anagram**", value = "".join(scrambled), inline = False)
        embed.add_field(name = "**Lives**", value = " ".join(lives_message), inline = False)
        embed.set_footer(text = footer, icon_url = 'https://cdn2.iconfinder.com/data/icons/app-types-in-grey/512/info_512pxGREY.png')
        await ctx.send(embed = embed)

        def check(message):
            return message.content.startswith("+") and message.author == ctx.author and len(message.content.strip()) > 1

        while True:
            try:
                guess = await self.bot.wait_for("message", timeout = 300, check = check)

            except:
                exec(f"del hm_{ctx.author.id}", globals())

                await ctx.send(f"5 minute timer: {ctx.author.mention}'s game has ended.")
                return

            content = guess.content[1:].strip().lower()

            if content == word:
                embed = discord.Embed(title = title, description = won_game_msg, color = 0x00ff00)
                embed.add_field(name = "**Word**", value = word, inline = False)
                embed.add_field(name = "**Definition**", value = definition, inline = False)
                embed.add_field(name = "**Lives**", value = " ".join(lives_message), inline = False)
                await ctx.send(embed = embed)

                if bet != None:
                    await functs.update_balance(ctx.author.id, bet * 2)

                exec(f"del hm_{ctx.author.id}", globals())
                return
            
            else:
                lives_message[-lives_message.count('❌') - 1] = '❌'

                if lives_message.count('❤') == 0:
                    embed = discord.Embed(title = title, description = lost_game_msg, color = 0xff0000)
                    embed.add_field(name = "**Word**", value = word, inline = False)
                    embed.add_field(name = "**Definition**", value = definition, inline = False)
                    embed.add_field(name = "**Lives**", value = " ".join(lives_message), inline = False)
                    await ctx.send(embed = embed)

                    exec(f"del hm_{ctx.author.id}", globals())
                    return

                embed = discord.Embed(title = title, description = f"Oops! Letter `{content}` is not in the word.", color = 0xff0000)
                embed.add_field(name = "**Word**", value = word, inline = False)
                embed.add_field(name = "**Lives**", value = " ".join(lives_message), inline = False)
                embed.set_footer(text = footer, icon_url = 'https://cdn2.iconfinder.com/data/icons/app-types-in-grey/512/info_512pxGREY.png')
                await ctx.send(embed = embed)

def setup(bot):
    bot.add_cog(Gaming(bot, requests.get("https://svnweb.freebsd.org/csrg/share/dict/words?view=co&content-type=text/plain").text))
