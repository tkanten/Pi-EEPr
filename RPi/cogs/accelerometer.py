from settings import *

def setup(bot):
    bot.add_cog(Accelerometer(bot))

class Accelerometer(commands.Cog):
    motion = False
    directions = "xyz"

    iterations = 5
    delta = 5

    def __init__(self, bot):
        self.bot = bot
        # this sensor should be running 3.3v

        self.sensor = ADXL345()

        self.module_name = __file__.split("/")[-1].split(".")[0]

        self._client = MqttClient("Accelerometer")
        self._client.add_subscription(f"Server/{self.module_name}/status")

        self._client.client.on_message = self.parse_message

        self.driver()

        if not self.check_motion.is_running():
            self.check_motion.start()

    def driver(self):
        self.get_resting_average()
        # print(self.resting_values["max"]["x"])
        # print(self.resting_values["avg"]["x"])
        # print(self.resting_values["min"]["x"])

        self.find_delta()

        # print("delta:")
        # print(self.alert_values["low"]["x"])
        # print(self.alert_values["high"]["x"])

    def get_resting_average(self):
        """Find what resting values are"""
        current_value = []

        for i in range(self.iterations):

            current_read = self.sensor.getAxes()

            entry = [current_read["x"], current_read["y"], current_read["z"], ((current_read["x"] + current_read["y"] + current_read["z"]) / 3)]
            current_value.append(entry)
            sleep(1)

        max_vals = [current_value[0][0], current_value[1]
                    [0], current_value[2][0], current_value[3][0]]
        min_vals = [current_value[0][0], current_value[1]
                    [0], current_value[2][0], current_value[3][0]]
        avg_vals = [0, 0, 0, 0]

        for n in range(self.iterations):
            for i in range(4):
                if (current_value[n][i] > max_vals[i]):
                    max_vals[i] = current_value[n][i]
                elif (current_value[n][i] < min_vals[i]):
                    min_vals[i] = current_value[n][i]

                avg_vals[i] += current_value[n][i]

        for i in range(4):
            avg_vals[i] = avg_vals[i] / self.iterations

        average = {"x": avg_vals[0], "y": avg_vals[1],
                   "z": avg_vals[2], "avg": avg_vals[3]}
        min = {"x": min_vals[0], "y": min_vals[1],
               "z": min_vals[2], "avg": min_vals[3]}
        max = {"x": max_vals[0], "y": max_vals[1],
               "z": max_vals[2], "avg": max_vals[3]}

        self.resting_values = {"avg": average, "min": min, "max": max}

    def find_delta(self):
        """find the values that will set off the alarm"""

        low = {"x": 1, "y": 1, "z": 1}
        high = {"x": 1, "y": 1, "z": 1}

        for direction in "xyz":
            if (self.resting_values["min"][direction] > self.resting_values["avg"][direction] - self.delta):
                low[direction] = self.resting_values["avg"][direction] - self.delta
            else:
                low[direction] = self.resting_values["min"][direction] - self.delta

            if (self.resting_values["max"][direction] < self.resting_values["avg"][direction] + self.delta):
                high[direction] = self.resting_values["avg"][direction] + self.delta
            else:
                high[direction] = self.resting_values["max"][direction] + self.delta

        self.alert_values = {"low": low, "high": high}

    @tasks.loop(seconds=3)
    async def check_motion(self):
        # print("Check for motion")
        if not self.bot.is_ready():
            return
        current = self.sensor.getAxes()
        for i in range(3):
            if (current[self.directions[i]] < self.alert_values["low"][self.directions[i]]):
                self.motion = True
                await self.alert()
            elif (current[self.directions[i]] > self.alert_values["high"][self.directions[i]]):
                self.motion = True
                await self.alert()
            elif (self.motion == True):
                self.motion = False
                await self.no_alert()

    async def alert(self):
        """Alert the user that the device is undergoing acceleration"""

        self._client.publish(f"RPi/{self.module_name}", 1)

    async def no_alert(self):
        """alert saying that motion is over"""

        self._client.publish(f"RPi/{self.module_name}", 0)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.module_name} is On")
        
    def parse_message(self, client, userdata, message):
        print("Preparing status")

        current = self.sensor.getAxes()

        x_avg = self.resting_values["avg"]["x"]
        y_avg = self.resting_values["avg"]["y"]
        z_avg = self.resting_values["avg"]["z"]

        avg = self.resting_values["avg"]

        output = f"The accelerometer is currently undergoing {current}, where {avg} is normal"

        self._client.publish(f"RPi/{self.module_name}/status", output)
