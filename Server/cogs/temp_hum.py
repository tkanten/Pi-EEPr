from settings import *

def setup(bot):
    bot.add_cog(TempHum(bot))

class TempHum(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.status_message = ""
        self.send_status_b = False

        self.logging_channel = db["BOT_LOG_CHANNEL"]

        if (os.name == "posix"):
            self.module_name = __file__.split("/")[-1].split(".")[0]
        else:
            self.module_name = __file__.split("\\")[-1].split(".")[0]

        self._client = MqttClient("TempHumS")
        self._client.add_subscription(f"RPi/{self.module_name}")
        self._client.client.on_message = self.parse_message

        if not self.send_status.is_running():
            self.send_status.start()

    @commands.group()
    async def temp_hum(self, ctx):
        """Base class for Temp/Hum sensor"""
        pass

    @temp_hum.command()
    async def status(self, ctx):
        """Get the status of the Temp/Hum"""
        self._client.publish(f"Server/{self.module_name}", 1)

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