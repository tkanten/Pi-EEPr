from settings import *
from dht11_library import *

def setup(bot):
    bot.add_cog(TempHum(bot))

#gpio 18

class TempHum(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.sensor = DHT11(pin=18)

        self.module_name = __file__.split("/")[-1].split(".")[0]
        
        self._client = MqttClient("TempHum")
        self._client.add_subscription(f"Server/{self.module_name}")
        self._client.client.on_message = self.parse_message

    def parse_message(self, client, userdata, message):

        self.send_temp()
    
    def send_temp(self):
        temp = self.sensor.read()

        if (temp.temperature == 0 and temp.humidity == 0):
            self.send_temp()
        else:
            self._client.publish(f"RPi/{self.module_name}", f"The current temperature is {temp.temperature}, and the humidity is {temp.humidity}")

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.module_name} is On")