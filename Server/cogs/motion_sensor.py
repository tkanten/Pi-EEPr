from settings import *

def setup(bot):
    bot.add_cog(Motion_Sensor(bot))

class Motion_Sensor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        if (os.name == "posix"):
            self.module_name = __file__.split("/")[-1].split(".")[0]
        else:
            self.module_name = __file__.split("\\")[-1].split(".")[0]

        self.logging_channel = db["BOT_LOG_CHANNEL"]
        self.payload_detected = False
        self.status_ready = False
        self.status_message = ""

        self._client = MqttClient("Motion SensorS")
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
            self.status_ready = True
            self.status_message = message.payload.decode("UTF-8")
        elif b'1' in message.payload:
            self.payload_detected = True

    @commands.group()
    async def motion_sensor(self, ctx):
        """Base command for motion sensor functions"""
        pass

    @motion_sensor.command()
    async def status(self, ctx):
        """Get the current status of the motion sensor"""
        self._client.publish(f'Server/{self.module_name}/status', 1)

    @tasks.loop(seconds=1)
    async def send_alert(self):
        if not (self.payload_detected or self.status_ready):
            return
        if not self.bot.is_ready():
            return

        if isinstance(self.logging_channel, int):
            self.logging_channel = await self.bot.fetch_channel(self.logging_channel)

        if self.payload_detected:
            await self.logging_channel.send("Alert!!! The Pi-EEPr has seen movement!!!")
            self.payload_detected = False

        if self.status_ready:
            await self.logging_channel.send(self.status_message)
            self.status_ready = False

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.module_name} is On")