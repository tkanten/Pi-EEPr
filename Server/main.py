from settings import *

bot = commands.Bot(command_prefix=".", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print("Bot is initalizing")

for filename in os.listdir("./cogs"):
    if filename.endswith(".py") and filename != "__init__.py":
        try:
            bot.load_extension(f"cogs.{filename[:-3]}")
        except Exception as e:
            print(f"[ERROR LOADING {filename.upper()}]")
            print("ERR\n\n\n", e)

bot.run(DISCORD_BOT_TOKEN)
