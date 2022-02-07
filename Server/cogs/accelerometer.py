from settings import *

def setup(bot):
    bot.add_cog(Accelerometer(bot))

class Accelerometer(commands.Cog):
    movement_detected = False
    def __init__(self, bot):
        self.bot = bot

        if (os.name == "posix"):
            self.module_name = __file__.split("/")[-1].split(".")[0]
        else:
            self.module_name = __file__.split("\\")[-1].split(".")[0]

        self.logging_channel = db["BOT_LOG_CHANNEL"]
        self.movement_detected = False
        self.status_detected = False
        self.status_message = ""
        self._client = MqttClient("AccelerometerS")
        self._client.add_subscription(f"RPi/{self.module_name}")
        self._client.add_subscription(f"RPi/{self.module_name}/status")
        self._client.client.on_message = self.parse_message

        if not self.send_alert.is_running():
            self.send_alert.start()

    def cog_unload(self):
        if self.send_alert.is_running():
            self.send_alert.cancel()

    def parse_message(self, client, userdata, message):
        if message.topic == f"RPi/{self.module_name}/status":
            self.status_detected = True
            self.status_message = message.payload.decode('UTF-8')
        elif b'1' in message.payload:
            self.movement_detected = True

    @commands.group()
    async def accelerometer(self, ctx):
        """Base command for accelerometer functions"""
        pass

    @accelerometer.command()
    async def status(self, ctx):
        """Get the current status, as well as normal, of the accelerometer"""
        self._client.publish(f"Server/{self.module_name}/status", 1)

    @tasks.loop(seconds=1)
    async def send_alert(self):
        if not (self.movement_detected or self.status_detected):
            return
        if not self.bot.is_ready():
            return

        if isinstance(self.logging_channel, int):
            self.logging_channel = await self.bot.fetch_channel(self.logging_channel)

        if self.movement_detected:
            await self.logging_channel.send("Alert!!! The Pi-EEPr has been moved!!!")
            self.movement_detected = False

        if self.status_detected:
            await self.logging_channel.send(self.status_message)
            self.status_detected = False
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.module_name} is On") 