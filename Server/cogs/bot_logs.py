from settings import *

def setup(bot):
    bot.add_cog(ErrorTracking(bot))


class ErrorTracking(commands.Cog):
    """Methods for error tracking/sending"""

    def __init__(self, bot):
        self.bot = bot
        self.BotLog = LogEmbeds(bot, db["BOT_LOG_CHANNEL"]["ID"], discord.Colour.blurple())

    @commands.Cog.listener()
    async def on_ready(self):
        print("Error Tracking Cog is Online")
        
    @commands.Cog.listener()
    async def on_command_error(self, ctx, exception):
        try:
            await ctx.message.delete()
        except Exception as e:
            print("couldn't delete",exception, '- likely a DM channel')
        await ctx.send(f"{exception}. Check help!",delete_after=5)
        await self.BotLog.log_event("Command Error Detected",f"{exception}",ctx.author)
    
    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):
        await self.BotLog.log_event("ERROR EVENT","ARGS/KWARGS REQUIRE PARSING. DM COMPUNCTION.")
        print("ERROR EVENT\nNEED TO INTEGRATE INTO A BOT LOG")
        print(event)
        print(args)
        print(kwargs)
        print("\n"*5)