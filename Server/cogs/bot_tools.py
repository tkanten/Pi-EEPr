import asyncio
from settings import *


def setup(bot):
    bot.add_cog(BotTools(bot))


class BotTools(commands.Cog):
    """Control/debug tools for bot"""
    backup_freq = 5

    def __init__(self, bot):
        self.bot = bot

        self.BotLog = LogEmbeds(bot, db["BOT_LOG_CHANNEL"], discord.Colour.gold())

        if not self.backup_database.is_running():
            BotTools.backup_freq = db["backup"]
            self.backup_database.start()
            print(f"Backup task started - backing up every {BotTools.backup_freq} seconds")

    def cog_unload(self):
        if self.backup_database.is_running():
            self.backup_database.cancel()
        db.backup_data()

    #### BOT GROUP ####
    @commands.group()
    async def bot(self, ctx):
        """Base Bot Controller command"""
        await ctx.message.delete()

    @bot.command()
    async def shutdown(self, ctx):
        """Terminates the bot"""
        print(f"Shutdown command executed by {ctx.author.name}")
        db.backup_data()
        if self.backup_database.is_running():
            self.backup_database.stop()
        await self.bot.close()
        exit('-69')

    ### COG GROUP ###
    @commands.group()
    async def cog(self, ctx):
        """Base Cog Controller command"""
        ## push database just in case a forced shutdown must occur
        db.backup_data()
        # await ctx.send("Base cog command, check help cog", delete_after = 5)

    @cog.command()
    async def unload(self, ctx, cog: str):
        """Unload a cog file"""
        await ctx.message.delete()
        try:
            self.bot.unload_extension(f"cogs.{cog}")
        except Exception as e:
            await ctx.send(f"Cog '{cog}' failed to unload", delete_after=5)
            return

        await ctx.send(f"Cog '{cog}' unloaded", delete_after=5)

    @cog.command()
    async def load(self, ctx, cog: str):
        """Load a cog file"""
        await ctx.message.delete()
        try:
            self.bot.load_extension(f"cogs.{cog}")
        except Exception as e:
            await ctx.send(f"Cog '{cog}' failed to load", delete_after=5)
            return
        await ctx.send(f"Cog '{cog}' loaded", delete_after=5)

    @cog.command()
    async def reload(self, ctx, cog: str):
        """Reload a cog file, use * to wildcard and reload all"""
        await ctx.message.delete()
        if cog == "*":
            # create a message embed if wildcard reload

            embed = discord.Embed(colour=discord.Colour.gold(), title="Bot Cog Status")
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)

            for filename in os.listdir("./cogs"):
                if filename.endswith(".py") and filename != "__init__.py":
                    try:
                        self.bot.reload_extension(f"cogs.{filename[:-3]}")
                    except Exception as e:
                        embed.add_field(name=f"{filename[:-3]}", value="Not loaded", inline=True)
                        continue
                    embed.add_field(name=f"{filename[:-3]}", value="Loaded", inline=True)
            await ctx.send(embed=embed, delete_after=5)
        else:
            try:
                self.bot.reload_extension(f"cogs.{cog}")
            except Exception as e:
                await ctx.send(f"Failed to reload cog '{cog}'", delete_after=5)
                return
            await ctx.send(f"Cog '{cog}' reloaded", delete_after=3)

    #### DATABASE GROUP ####
    ## DATABASE COMMANDS ##
    @commands.group()
    async def database(self, ctx):
        """Base command for database management"""
        await ctx.message.delete()

    @database.command()
    async def backupfreq(self, ctx, seconds):
        """USAGE: backupfreq <minutes> - Adjust backup frequency"""
        if not seconds.isdigit():
            await ctx.send("Bad number input")
            return

        if db["backup"] != int(seconds):
            db["backup"] = int(seconds)
            BotTools.backup_freq = db["backup"]
            await ctx.send(f"Backup freqency changed to {seconds} seconds", delete_after=5)
            self.bot.reload_extension("cogs.bot_tools")
        else:
            await ctx.send(f"Backup already set at {BotTools.backup_freq} seconds", delete_after=5)

    @database.command()
    async def backup(self, ctx):
        """Force a database backup"""
        count = db.backup_data()
        await ctx.send(f"Database backed up, {count} document(s) updated.", delete_after=5)

    ## DATABASE TASKS ##
    @tasks.loop(seconds=backup_freq)
    async def backup_database(self):
        if not self.bot.is_ready():
            return
        db.backup_data()
