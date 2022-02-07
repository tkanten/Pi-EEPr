import os
import discord
from discord.ext import commands, tasks
import json
import datetime

from gpiozero import *
from time import sleep, time
import asyncio
import subprocess
from picamera import PiCamera
from dht11_library import DHT11

import glob

from client import MqttClient
from adxl345 import ADXL345

try:
    from signal import pause
except Exception as e:
    print("non POSIX OS detected")
    exit(-1)
