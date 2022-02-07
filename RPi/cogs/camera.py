from settings import *

def setup(bot):
    bot.add_cog(PiCam(bot))

class PiCam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logging_channel = db["BOT_LOG_CHANNEL"]
        self.rotation = 180

        self.auto_upload = True

        self.path = os.path.join(os.path.dirname(
            os.path.dirname(__file__)), '', "camera_storage")

        self.module_name = __file__.split("/")[-1].split(".")[0]

        self._client = MqttClient("Camera")
        self._client.add_subscription("RPi/motion_sensor")
        self._client.add_subscription(f"Server/{self.module_name}/rotate")
        self._client.add_subscription(f"Server/{self.module_name}/snap")
        self._client.client.on_message = self.parse_message

        if not self.push_picture.is_running():
            self.push_picture.start()

    # @commands.command()
    # async def snap(self, ctx):
    #     await ctx.message.delete()
    #     await ctx.send("brb snappin a quick pic")

    #     await self.capture_picture()

    @tasks.loop(seconds=5)
    async def push_picture(self):
        if not self.auto_upload:
            return
        if not self.bot.is_ready():
            return
        if isinstance(self.logging_channel, int):
            self.logging_channel = await self.bot.fetch_channel(self.logging_channel)

        if not os.listdir(self.path):
            return
        for image in glob.glob(os.path.join(self.path, "", "*.jpeg")):
            print("Sending photo")
            if self.bot.is_ws_ratelimited():
                print("CAMERA UPLOAD THROTTLED, WAITING")
                return
            abs_path = os.path.join(self.path, '', image)
            await self.logging_channel.send(file=discord.File(abs_path))
            os.remove(abs_path)

    async def capture_picture(self):
        filename = f"{str(int(time()))}.jpeg"

        with PiCamera() as camera:
            camera.rotation = self.rotation
            
            camera.start_preview()
            await asyncio.sleep(1)
            camera.capture(os.path.join(self.path, "", filename))
            camera.stop_preview()
       
    def parse_message(self, client, userdata, message):

        if message.topic == f"Server/{self.module_name}/rotate":
            degrees = int(message.payload.decode("UTF-8"))
            self.rotate(degrees)
        elif message.topic == f"Server/{self.module_name}/snap":
            asyncio.run(self.capture_picture())
        elif (message.payload == b'1'):
            asyncio.run(self.capture_picture())

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.module_name} is On")

    def rotate(self, degrees):
        if degrees == 0 or degrees == 90 or degrees == 180 or degrees == 270:
            self.rotation = degrees