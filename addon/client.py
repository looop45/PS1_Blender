import socket
import sys
import json
import os

SOCKET_PATH = '/tmp/ps1_render'

class server_client():

    client_sock = None

    def __init__(self):
        
        try:
            self.client_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.client_sock.settimeout(5)
            self.client_sock.connect(SOCKET_PATH)
            print(f"Connected to server at {SOCKET_PATH}")
        except Exception as e:
            print(f"Error: {e}")

    def start_scene(self, scene_data):
        message = construct_message("START", scene_data)
        try:
            self.client_sock.sendall(message.encode('utf-8'))
        except Exception as e:
            print(f"Error: {e}")

    def end_scene(self):
        pass

    def update_scene(self, update_data):
        pass

    def draw_scene(self, camera, dimensions):
        pass
     

API_ENUM = [
            "UPDATE",
            "DRAW",
            "START",
            "STOP"
]

def construct_message(cmd:str="", data=""):
    if cmd not in API_ENUM:
        raise Exception("cmd not found!")
        return
    
    message = {"cmd":cmd, "data":data}
    return json.dumps(message)