"""A run loop for agent/environment interaction."""

from pycmo.lib.protocol import Client, Server
import threading
import time
import json

f = open("C:\\Users\\AFSOC A8XW ORSA\\Documents\\Python Proj\\AI\\pycmo\\pycmo\\configs\\config.json")
config = json.load(f)

server = Server("C:\\Program Files (x86)\\Command Professional Edition\\Scenarios\\Standalone Scenarios\\Battle of Chumonchin Chan, 1950.scen")
x = threading.Thread(target=server.start_game)
x.start()

time.sleep(15)

client = Client()
client.connect()
for i in range(5):
    client.get_raw_data(config["observation_path"] + str(i) + ".xml")
    client.step("01", "00", "00")