from Database import db, COLLECTIONS

if not db["backup"]:
    db["backup","configs"] = int(input("Please enter database backup time"))

if not db["DISCORD_BOT_TOKEN"]:
    db["DISCORD_BOT_TOKEN","configs"] = input("Please enter your bot token from Discord")

if not db["BOT_LOG_CHANNEL"]:
    db["BOT_LOG_CHANNEL","configs"] = int(input("Logging channel"))

if not db["MQTT_HOST"]:
    db["MQTT_HOST","configs"] = input("Please enter your MQTT broker's IP")

if not db["MQTT_PORT"]:
    db["MQTT_PORT","configs"] = int(input("Please enter your MQTT broker's open port"))

if not db["MQTT_USERNAME"]:
    db["MQTT_USERNAME","configs"] = input("Please enter your MQTT publisher username")

if not db["MQTT_PASSWORD"]:
    db["MQTT_PASSWORD","configs"] = input("Please enter your MQTT publisher password")

db.backup_data()

from imports import *
