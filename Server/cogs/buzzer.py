from settings import *

def setup(bot):
    bot.add_cog(DblBuzzer(bot))
    
class DblBuzzer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.status_message = ""
        self.send_status_b = False

        self.logging_channel = db["BOT_LOG_CHANNEL"]

        if (os.name == "posix"):
            self.module_name = __file__.split("/")[-1].split(".")[0]
        else:
            self.module_name = __file__.split("\\")[-1].split(".")[0]
        
        self._client = MqttClient("BuzzerS")
        self._client.add_subscription(f"RPi/{self.module_name}/status")

        self._client.client.on_message = self.parse_message

        if not self.send_status.is_running():
            self.send_status.start()

    @commands.group()
    async def buzzer(self, ctx):
        """Base command for buzzer functions"""
        pass

    @buzzer.command()
    async def nice(self, ctx, *duration):
        """Turn the nice buzzer on, OPTIONAL: duration (seconds)"""
        self._client.publish(f'Server/{self.module_name}/nice', 1)
        await ctx.send("Buzzer is playing nice")
        if len(duration):
            await asyncio.sleep(int(duration[0]))
            self._client.publish(f'Server/{self.module_name}/off', 0)
            await ctx.send("Buzzer is off")

    @buzzer.command()
    async def naughty(self, ctx, *duration):
        """Turn the naughty buzzer on, OPTIONAL: duration (seconds)"""
        self._client.publish(f'Server/{self.module_name}/naughty', 1)
        await ctx.send("Buzzer is playing naughty")
        if len(duration):
            await asyncio.sleep(int(duration[0]))
            self._client.publish(f'Server/{self.module_name}/off', 0)
            await ctx.send("Buzzer is off")

    @buzzer.command()
    async def off(self, ctx):
        """Turn the buzzer off"""
        self._client.publish(f'Server/{self.module_name}/off', 0)
        await ctx.send("Buzzer is off")

    @buzzer.command()
    async def status(self, ctx):
        """Get the current activity of the buzzer"""
        self._client.publish(f'Server/{self.module_name}/status', 1)

    def parse_message(self, client, userdata, message):
        self.status_message = message.payload.decode("UTF-8")
        self.send_status_b = True

    @tasks.loop(seconds=1)
    async def send_status(self):
        if not self.send_status_b:
            return
        if not self.bot.is_ready():
            return
        
        if isinstance(self.logging_channel, int):
            self.logging_channel = await self.bot.fetch_channel(self.logging_channel)
        
        await self.logging_channel.send(self.status_message)
        self.send_status_b = False

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.module_name} is On")