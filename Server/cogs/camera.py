from settings import *

def setup(bot):
    bot.add_cog(PiCam(bot))

class PiCam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.logging_channel = db["BOT_LOG_CHANNEL"]
        
        if (os.name == "posix"):
            self.module_name = __file__.split("/")[-1].split(".")[0]
        else:
            self.module_name = __file__.split("\\")[-1].split(".")[0]

        self._client = MqttClient("CameraS")

    @commands.group()
    async def camera(self, ctx):
        """Base command for camera functions"""
        pass

    @camera.command()
    async def rotate(self, ctx, *degrees):
        """Rotate the camera to the angle specified"""
        degrees = degrees[0]
        self._client.publish(f"Server/{self.module_name}/rotate", degrees)

    @camera.command()
    async def snap(self, ctx):
        """Snap a photo using the camera"""
        self._client.publish(f"Server/{self.module_name}/snap", 1)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.module_name} is On")