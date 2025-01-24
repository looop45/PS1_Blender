import bpy
from .client import *
import struct

class Engine:
    connected = False

    def __init__(self):
        try:
            self.client = client()
            self.connected = True
        except ConnectionError as e:
            print( e )
            pass

    def start(self):
        type = ClientMessage.Start
        data = None

        self.client.send_data(type, data)

    def stop(self):
        self.client.disconnect()

    def update(self):
        type = ClientMessage.Update
        data = None #TODO: pack scene data

        self.client.send_data(type, data)

    def draw_request(self, camera, width, height):
        #construct data in correct order for the request
        type = ClientMessage.Draw

        dataStruct = struct.Struct("=HH") #TODO: Add camera data

        data = dataStruct.pack(width, height)

        #use client to create message and send
        self.client.send_data(type, data)

