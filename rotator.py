import socket
import json

import utils

host = json.loads(utils.read_file('config/setup.json'))["decode_settings"]['rotator_host']
port = json.loads(utils.read_file('config/setup.json'))["decode_settings"]['rotator_port']

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

while True:
    msg_length = client.recv(64).decode('utf-8')
    if msg_length:
        msg_length = int(msg_length)
        msg = client.recv(msg_length).decode('utf-8')
        print(msg)