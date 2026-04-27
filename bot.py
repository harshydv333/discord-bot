import discord
from discord.ext import commands
import asyncio
import random
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

players = []
race_active = False

def generate_event():
    subjects = [
        "a hunter", "an eagle", "a hawk", "a cat", "a snake",
        "a storm", "strong wind", "a drone", "a net trap",
        "a falling branch", "thunder", "a predator bird",
        "a human", "a kid throwing stones", "a crow gang",
        "a dog", "a fisherman net", "a vehicle"
    ]

    actions = [
        "attacked", "chased", "almost caught", "hit",
        "injured", "scared", "ambushed", "disturbed",
        "blocked", "targeted", "pushed", "confused"
    ]

    situations = [
        "mid-air", "while flying", "near a tree",
        "close to the ground", "during landing",
        "in the sky", "during a turn",
        "while escaping", "near a building",
        "over water", "in a storm"
    ]

    results = [
        "but survived!",
        "and lost balance!",
        "and slowed down!",
        "but escaped quickly!",
        "and got injured!",
        "but gained speed!",
        "and froze for a moment!",
        "but recovered!",
        "and panicked!",
        "but fought back!",
        "and almost died!",
        "but made a comeback!"
    ]

    return f"{random.choice(actions)} by {random.choice(subjects)} {random.choice(situations)} {random.choice(results)}"


@bot.event
async def on_ready():
    print(f"Bot online: {bot.user}")


@bot.command()
async def start(ctx, time: int = 1):
    global players, race_active

    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Only admin can start!")
        return

    if race_active:
        await ctx.send("Race already running!")
        return

    if time not in [1, 3, 5]:
        await ctx.send("❌ Choose 1 / 3 / 5 min")
        return

    race_active = True
    players = [ctx.author]

    msg = await ctx.send(f"🏁 React 🦜 to join ({time} min)")
    await msg.add_reaction("🦜")

    await asyncio.sleep(time * 60)

    msg = await ctx.channel.fetch_message(msg.id)

    for reaction in msg.reactions:
        if str(reaction.emoji) == "🦜":
            async for user in reaction.users():
                if not user.bot and user not in players:
                    players.append(user)

    if len(players) < 2:
        await ctx.send("❌ Need at least 2 players!")
        race_active = False
        return

    await run_race(ctx)


async def run_race(ctx):
    global race_active

    random.shuffle(players)

    positions = {p: 0 for p in players}
    dead = {}

    finish = 30 + len(players) * 5

    race_msg = await ctx.send("🏁 Race starting...")

    while True:
        text = "🏁 **PARROT SURVIVAL RACE** 🦜🔥\n\n"

        for p in players:

            if p in dead:
                if random.random() < 0.25:
                    del dead[p]
                    text += f"✨ **{p.display_name} revived!**\n\n"
                else:
                    text += f"💀 **{p.display_name}**\n🪦 {dead[p]}\n\n"
                    continue

            event = generate_event()
            move = random.randint(1, 4)

            if "speed" in event or "recovered" in event:
                move += 2
            elif "injured" in event or "slowed" in event:
                move = max(1, move - 2)

            positions[p] += move

            track = "─" * positions[p] + "🦜"

            text += f"**{p.display_name}**\n{track}\n➡ {event}\n\n"

            if any(x in event for x in ["attacked", "hit", "ambushed", "almost died"]):
                if random.random() < 0.2:
                    dead[p] = event

            if positions[p] >= finish:
                await race_msg.edit(content=text)
                await ctx.send(f"🏆 **Winner: {p.display_name}** 🔥")
                race_active = False
                return

        await race_msg.edit(content=text)
        await asyncio.sleep(3)


# 🔐 TOKEN FROM ENV
bot.run(os.getenv("TOKEN"))
