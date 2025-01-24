import socket
import sys
import json
import os
import struct
import time

SOCKET_PATH = '/tmp/ps1_render'

class ClientMessage:
    Start, \
    Stop, \
    Update, \
    Draw, \
    NumClientMessages = range(5)

class ServerMessage:
    Result, \
    NumServerMessages = range(2)


class client():

    client_sock = None

    def __init__(self):
        
        while True:
            try:
                self.client_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                self.client_sock.setblocking(True)
                self.client_sock.connect(SOCKET_PATH)
                print(f"Connected to server at {SOCKET_PATH}")
                break
            except socket.error as e:
                print(f"Connection failed: {e}. Retrying in 1 second...")
                time.sleep(1)

        self.stream = bytearray()
        self.headerStruct = struct.Struct( "=IB" )
        self.HEADER_SIZE = 5

    def disconnect(self):
        self.client_sock.close
        

    def send_data(self, messageType, data):
        assert( messageType < ClientMessage.NumClientMessages )

        if data == None:
            sizeBytes = 0
            data = bytes(0)
        else:
            sizeBytes = len(data)

        packet = self.headerStruct.pack( sizeBytes, messageType )

        self.client_sock.send( b''.join( (packet, data) ) )

    #Stolen from DERGO renderer
    def receive_data(self, callbackObj):

        chunk = self.client_sock.recv(4096*2)
        if not chunk:
            raise ConnectionError("Connection closed before the complete message was received.")
        
        self.stream.extend(chunk)

        remainingBytes = len(self.stream)
        while remainingBytes >= self.HEADER_SIZE:
            header = self.headerStruct.unpack_from( memoryview( self.stream ) )
            header_sizeBytes	= header[0]
            header_messageType	= header[1]
            #print(header_sizeBytes, header_messageType)
			
            if header_sizeBytes > remainingBytes - self.HEADER_SIZE:
                # Packet is incomplete. Process it the next time.
                break

            if header_messageType >= ServerMessage.NumServerMessages:
                raise RuntimeError( "Message type is higher than NumServerMessages. Message is corrupt!!!" )

            callbackObj.processMessage( header_sizeBytes, header_messageType,
                                        self.stream[self.HEADER_SIZE:(self.HEADER_SIZE + header_sizeBytes)] )

            remainingBytes -= self.HEADER_SIZE
            remainingBytes -= header_sizeBytes

            self.stream = self.stream[(self.HEADER_SIZE + header_sizeBytes):]
