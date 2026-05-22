import discord
from discord.ext import commands
from database import Database
import random, asyncio

db = Database()

POKEMON_LIST = [
    {"name":"Pikachu","type":"Electric","hp":100,"atk":55,"def":40,"rarity":"Uncommon","emoji":"⚡"},
    {"name":"Charizard","type":"Fire/Flying","hp":150,"atk":84,"def":78,"rarity":"Rare","emoji":"🔥"},
    {"name":"Blastoise","type":"Water","hp":145,"atk":83,"def":100,"rarity":"Rare","emoji":"💧"},
    {"name":"Mewtwo","type":"Psychic","hp":212,"atk":110,"def":90,"rarity":"Legendary","emoji":"🔮"},
    {"name":"Eevee","type":"Normal","hp":95,"atk":45,"def":65,"rarity":"Common","emoji":"🦊"},
    {"name":"Gengar","type":"Ghost/Poison","hp":120,"atk":65,"def":60,"rarity":"Rare","emoji":"👻"},
    {"name":"Snorlax","type":"Normal","hp":320,"atk":110,"def":65,"rarity":"Epic","emoji":"😴"},
    {"name":"Lucario","type":"Fighting/Steel","hp":140,"atk":115,"def":70,"rarity":"Epic","emoji":"🥋"},
    {"name":"Rayquaza","type":"Dragon/Flying","hp":190,"atk":150,"def":90,"rarity":"Mythic","emoji":"🐉"},
    {"name":"Bulbasaur","type":"Grass/Poison","hp":110,"atk":49,"def":49,"rarity":"Common","emoji":"🌿"},
    {"name":"Squirtle","type":"Water","hp":108,"atk":48,"def":65,"rarity":"Common","emoji":"💦"},
    {"name":"Jigglypuff","type":"Normal/Fairy","hp":230,"atk":45,"def":20,"rarity":"Common","emoji":"🎵"},
]

MOVES = ["Tackle","Quick Attack","Thunderbolt","Flamethrower","Water Gun","Shadow Ball","Psychic","Earthquake","Ice Beam","Solar Beam"]
active_battles = {}

class Pokemon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="startjourney", aliases=["start-journey"])
    async def startjourney(self, ctx):
        if db.get_user_pokemon(ctx.author.id):
            await ctx.send("❌ You already started your journey!")
            return
        starters = [p for p in POKEMON_LIST if p['name'] in ["Pikachu","Bulbasaur","Squirtle","Charmander","Eevee"]]
        starter  = random.choice(starters)
        db.add_pokemon_to_user(ctx.author.id, starter['name'], starter)
        embed = discord.Embed(title="⚡ Journey Started!", description=f"You received **{starter['emoji']} {starter['name']}**!\nType: {starter['type']} | HP: {starter['hp']}", color=discord.Color.green())
        embed.set_footer(text="Use .catch to find wild Pokémon!")
        await ctx.send(embed=embed)

    @commands.command(name="catch")
    async def catch(self, ctx):
        poke = random.choice(POKEMON_LIST)
        rarity_weights = {"Common":50,"Uncommon":30,"Rare":15,"Epic":4,"Legendary":1,"Mythic":0.5}
        # Weighted random
        chances = {"Common":0.5,"Uncommon":0.4,"Rare":0.25,"Epic":0.15,"Legendary":0.05,"Mythic":0.02}
        catch_rate = chances.get(poke['rarity'], 0.3)
        caught = random.random() < catch_rate
        embed = discord.Embed(title=f"🌿 A wild {poke['name']} appeared!", description=f"{poke['emoji']} **{poke['name']}**\nType: {poke['type']} | Rarity: {poke['rarity']}", color=discord.Color.green())
        if caught:
            db.add_pokemon_to_user(ctx.author.id, poke['name'], poke)
            embed.add_field(name="Result", value="✅ Caught! Added to your PC!", inline=False)
        else:
            embed.add_field(name="Result", value="💨 It fled! Better luck next time!", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="pokemon")
    async def pokemon(self, ctx, user: discord.User = None):
        target  = user or ctx.author
        pokemons = db.get_user_pokemon(target.id)
        if not pokemons:
            await ctx.send(f"{'You have' if target == ctx.author else f'{target.display_name} has'} no Pokémon! Use `.startjourney` first!")
            return
        embed = discord.Embed(title=f"⚡ {target.display_name}'s Pokémon", description=f"Total: {len(pokemons)}", color=discord.Color.yellow())
        for p in pokemons[:9]:
            data = p.get('data',{})
            embed.add_field(name=f"{data.get('emoji','⚡')} {p['name']}", value=f"HP:{data.get('hp','?')} ATK:{data.get('atk','?')}", inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="pokedex")
    async def pokedex(self, ctx, *, name: str = None):
        if name:
            poke = next((p for p in POKEMON_LIST if p['name'].lower() == name.lower()), None)
            if not poke:
                await ctx.send(f"❌ Pokémon **{name}** not found!")
                return
            embed = discord.Embed(title=f"{poke['emoji']} {poke['name']}", color=discord.Color.yellow())
            embed.add_field(name="Type",   value=poke['type'],   inline=True)
            embed.add_field(name="HP",     value=poke['hp'],     inline=True)
            embed.add_field(name="ATK",    value=poke['atk'],    inline=True)
            embed.add_field(name="DEF",    value=poke['def'],    inline=True)
            embed.add_field(name="Rarity", value=poke['rarity'], inline=True)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="📖 Pokédex", color=discord.Color.yellow())
            for p in POKEMON_LIST:
                embed.add_field(name=f"{p['emoji']} {p['name']}", value=p['type'], inline=True)
            await ctx.send(embed=embed)

    @commands.command(name="findpoke")
    async def findpoke(self, ctx, *, name: str):
        results = [p for p in POKEMON_LIST if name.lower() in p['name'].lower()]
        if not results:
            await ctx.send(f"❌ No Pokémon found for **{name}**")
            return
        embed = discord.Embed(title=f"🔍 Results for '{name}'", color=discord.Color.yellow())
        for p in results:
            embed.add_field(name=f"{p['emoji']} {p['name']}", value=p['type'], inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="party")
    async def party(self, ctx):
        pokemons = db.get_user_pokemon(ctx.author.id)
        if not pokemons:
            await ctx.send("❌ No Pokémon! Use `.startjourney` first!")
            return
        embed = discord.Embed(title=f"⚔️ {ctx.author.display_name}'s Party", color=discord.Color.gold())
        for p in pokemons[:6]:
            data = p.get('data',{})
            embed.add_field(name=f"{data.get('emoji','⚡')} {p['name']}", value=f"HP: {data.get('hp','?')} | ATK: {data.get('atk','?')}", inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="pc")
    async def pc(self, ctx):
        pokemons = db.get_user_pokemon(ctx.author.id)
        embed    = discord.Embed(title=f"💻 {ctx.author.display_name}'s PC", description=f"{len(pokemons)} Pokémon stored", color=discord.Color.blue())
        for p in pokemons:
            data = p.get('data',{})
            embed.add_field(name=f"{data.get('emoji','⚡')} {p['name']}", value=data.get('type','?'), inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="battle")
    async def battle(self, ctx, user: discord.User):
        if user.id == ctx.author.id:
            await ctx.send("❌ Can't battle yourself!")
            return
        p1_pokemon = db.get_user_pokemon(ctx.author.id)
        p2_pokemon = db.get_user_pokemon(user.id)
        if not p1_pokemon:
            await ctx.send("❌ You have no Pokémon! Use `.startjourney`")
            return
        if not p2_pokemon:
            await ctx.send(f"❌ {user.display_name} has no Pokémon!")
            return
        p1 = p1_pokemon[0]; p2 = p2_pokemon[0]
        p1d = p1.get('data',{}); p2d = p2.get('data',{})
        p1_hp = p1d.get('hp',100); p2_hp = p2d.get('hp',100)
        rounds = []
        for _ in range(5):
            dmg1 = random.randint(10, p1d.get('atk',50))
            dmg2 = random.randint(10, p2d.get('atk',50))
            p2_hp -= dmg1; p1_hp -= dmg2
            rounds.append(f"⚔️ {p1['name']} hit {dmg1} | {p2['name']} hit {dmg2}")
            if p1_hp <= 0 or p2_hp <= 0:
                break
        winner = ctx.author if p2_hp <= 0 else user
        loser  = user if p2_hp <= 0 else ctx.author
        reward = 100
        db.add_stellas(winner.id, reward)
        embed = discord.Embed(title="⚡ Pokémon Battle!", description="\n".join(rounds[-3:]), color=discord.Color.yellow())
        embed.add_field(name="🏆 Winner", value=f"{winner.mention} +{reward} Stellas!", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="heal")
    async def heal(self, ctx):
        cost = 50
        if not db.remove_stellas(ctx.author.id, cost):
            await ctx.send(f"❌ Need **{cost}** Stellas to heal!")
            return
        await ctx.send(f"💊 All your Pokémon are healed! (-{cost} Stellas)")

    @commands.command(name="learn")
    async def learn(self, ctx, *, move: str = None):
        move = move or random.choice(MOVES)
        await ctx.send(f"✅ Your Pokémon learned **{move}**!")

    @commands.command(name="swap")
    async def swap(self, ctx, pos: int):
        await ctx.send(f"🔄 Swap feature coming soon~!")

async def setup(bot):
    await bot.add_cog(Pokemon(bot))
