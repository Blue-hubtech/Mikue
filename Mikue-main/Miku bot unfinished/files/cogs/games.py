import discord
from discord.ext import commands
from database import Database
import random, asyncio

db = Database()

# ── Active game sessions ───────────────────────────────────────────────────────
active_quiz     = {}
active_hangman  = {}
active_chess    = {}

QUIZ_QUESTIONS = [
    {"q": "What is the Naruto's signature jutsu?", "a": "rasengan"},
    {"q": "Who is the captain of the Straw Hat Pirates?", "a": "luffy"},
    {"q": "What is Goku's home planet?", "a": "planet vegeta"},
    {"q": "Which anime features Titans eating humans?", "a": "attack on titan"},
    {"q": "What power does Satoru Gojo have?", "a": "infinity"},
    {"q": "What fruit did Luffy eat?", "a": "gum gum fruit"},
    {"q": "Who writes the Death Note?", "a": "light yagami"},
    {"q": "What is the name of Tanjiro's breathing style?", "a": "water breathing"},
    {"q": "Which city is Batman's home?", "a": "gotham"},
    {"q": "What is the first Pokémon in the Pokédex?", "a": "bulbasaur"},
]

HANGMAN_WORDS = ["PIKACHU","NARUTO","LUFFY","TANJIRO","GOKU","VEGETA","SASUKE","GOJO","ICHIGO","DEKU"]

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="quiz")
    async def quiz(self, ctx):
        if ctx.channel.id in active_quiz:
            await ctx.send("❌ A quiz is already running in this channel!")
            return
        q = random.choice(QUIZ_QUESTIONS)
        active_quiz[ctx.channel.id] = {"answer": q["a"], "author": ctx.author.id}
        embed = discord.Embed(title="🧠 Quiz Time!", description=q["q"], color=discord.Color.purple())
        embed.set_footer(text="Use .answer <your answer> to respond! (30 seconds)")
        await ctx.send(embed=embed)
        await asyncio.sleep(30)
        if ctx.channel.id in active_quiz:
            del active_quiz[ctx.channel.id]
            await ctx.send(f"⏰ Time's up! The answer was **{q['a'].title()}**!")

    @commands.command(name="answer")
    async def answer(self, ctx, *, ans: str):
        if ctx.channel.id not in active_quiz:
            await ctx.send("❌ No active quiz! Start one with `.quiz`")
            return
        correct = active_quiz[ctx.channel.id]["answer"]
        if ans.lower().strip() == correct.lower():
            del active_quiz[ctx.channel.id]
            reward = 50
            db.add_stellas(ctx.author.id, reward)
            embed = discord.Embed(title="✅ Correct!", description=f"{ctx.author.mention} got it! +**{reward}** Stellas 💫", color=discord.Color.green())
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"❌ Wrong! Keep trying~")

    @commands.command(name="hangman")
    async def hangman(self, ctx):
        if ctx.channel.id in active_hangman:
            await ctx.send("❌ Hangman already running here!")
            return
        word    = random.choice(HANGMAN_WORDS)
        display = ["_"] * len(word)
        active_hangman[ctx.channel.id] = {"word": word, "display": display, "guessed": [], "lives": 6}
        embed = discord.Embed(title="🎯 Hangman!", description=f"`{' '.join(display)}`\n\nLives: ❤️×6", color=discord.Color.orange())
        embed.set_footer(text="Type a letter to guess!")
        await ctx.send(embed=embed)

    @commands.command(name="guess")
    async def guess(self, ctx, letter: str):
        if ctx.channel.id not in active_hangman:
            await ctx.send("❌ No active hangman! Start with `.hangman`")
            return
        game   = active_hangman[ctx.channel.id]
        letter = letter.upper()[0]
        if letter in game["guessed"]:
            await ctx.send("Already guessed that letter!")
            return
        game["guessed"].append(letter)
        if letter in game["word"]:
            for i, l in enumerate(game["word"]):
                if l == letter:
                    game["display"][i] = letter
            if "_" not in game["display"]:
                del active_hangman[ctx.channel.id]
                reward = 75
                db.add_stellas(ctx.author.id, reward)
                await ctx.send(f"🎉 {ctx.author.mention} solved it! **{game['word']}** +{reward} Stellas!")
                return
        else:
            game["lives"] -= 1
            if game["lives"] == 0:
                del active_hangman[ctx.channel.id]
                await ctx.send(f"💀 Game over! Word was **{game['word']}**")
                return
        embed = discord.Embed(title="🎯 Hangman", description=f"`{' '.join(game['display'])}`\nLives: ❤️×{game['lives']}\nGuessed: {', '.join(game['guessed'])}", color=discord.Color.orange())
        await ctx.send(embed=embed)

    @commands.command(name="chess", aliases=["accept-ch"])
    async def chess(self, ctx, user: discord.User = None):
        await ctx.send("♟️ Chess system coming soon~! 🎤💚")

    @commands.command(name="accept")
    async def accept(self, ctx):
        await ctx.send("✅ Challenge accepted! Feature coming soon~")

    @commands.command(name="reject")
    async def reject(self, ctx):
        await ctx.send("❌ Challenge rejected!")

    @commands.command(name="forfeit")
    async def forfeit(self, ctx):
        await ctx.send("🏳️ You forfeited the game!")

async def setup(bot):
    await bot.add_cog(Games(bot))
