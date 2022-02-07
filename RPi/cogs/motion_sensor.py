from settings import *

def setup(bot):
    bot.add_cog(Motion_Sensor(bot))


class Motion_Sensor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sensor = MotionSensor(4, threshold=0.4)

        self.path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '', "mqtt_outgoing")
        self.module_name = __file__.split("/")[-1].split(".")[0]

        self.sensor.when_motion = self.motion_detected
        self.sensor.when_no_motion = self.motion_not_detected

        self._client = MqttClient("Motion Sensor")
        self._client.add_subscription(f'Server/{self.module_name}/status')

        self._client.client.on_message = self.parse_message

    def motion_detected(self):
        self._client.publish(f"RPi/{self.module_name}", 1)

    def motion_not_detected(self):
        self._client.publish(f"RPi/{self.module_name}", 0)

    def parse_message(self, client, userdata, message):
        if self.sensor.value:
            self._client.publish(f"RPi/{self.module_name}/status", "There is motion")
        else:
            self._client.publish(f"RPi/{self.module_name}/status", "There is no motion")

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.module_name} is On")