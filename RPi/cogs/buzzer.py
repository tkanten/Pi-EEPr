from settings import *

def setup(bot):
    bot.add_cog(DblBuzzer(bot))
    
class DblBuzzer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.buzzer1 = Buzzer(23)
        self.buzzer2 = Buzzer(24)

        self.module_name = __file__.split("/")[-1].split(".")[0]

        self._client = MqttClient("Buzzer")
        self._client.add_subscription("#")
        self._client.client.on_message = self.parse_message

    def buzzer_on(self, both=False):
        if both:
            self.buzzer1.on()
        self.buzzer2.on()

    def buzzer_off(self, both=True):
        self.buzzer1.off()
        self.buzzer2.off()

    def parse_message(self, client, userdata, message):

        if message.topic == 'RPi/accelerometer':
            if message.payload == b'1':
                self.buzzer_on(True)
            else:
                self.buzzer_off()
        # elif message.topic == 'RPi/motion_sensor':
        #     if message.payload == b'1':
        #         self.buzzer_on()
        #     else:
        #         self.buzzer_off()
        elif f'Server/{self.module_name}' in message.topic:
            if (message.topic == f'Server/{self.module_name}/nice'):
                self.buzzer_on()
            elif (message.topic == f'Server/{self.module_name}/naughty'):
                self.buzzer_on(True)
            elif (message.topic == f'Server/{self.module_name}/status'):
                buz1 = "off"
                buz2 = "off"
                if self.buzzer1.value:
                    buz1 = "on"
                if self.buzzer2.value:
                    buz2 = "on"
                
                self._client.publish(f"RPi/{self.module_name}/status", f"The buzzer 1 is {buz1}, and the buzzer 2 is {buz2}")
            else:
                self.buzzer_off()
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.module_name} is On")