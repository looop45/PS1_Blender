import socket
import threading
import pickle
import queue

class server_host():

    server_socket = None
    conn = None
    addr = None

    def __init__(self, host="127.0.0.1", port=6969):
        self.start_socket(host, port)

    def handle_client(self):
        try:
            while True:
                # Send example scene data
                scene_data = {"example_key": "example_value"}
                serialized_data = pickle.dumps(scene_data)
                self.conn.sendall(serialized_data)

                # Receive pixel data
                received_data = self.conn.recv(4096)
                if not received_data:  # Client disconnected
                    print("Client disconnected.")
                    break

                pixel_data = pickle.loads(received_data)
                print(f"Received pixel data: {pixel_data}")
        except Exception as e:
            print(f"Error with client: {e}")
        finally:
            self.conn.close()

    def start_socket(self, host="127.0.0.1", port=12345):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)
        print(f"Server listening on {host}:{port}")

    def connect(self):
        self.conn, self.addr = self.server_socket.accept()
        print(f"Connection established with {self.addr}")
            #self.handle_client(self.conn)

        return self.conn


if __name__ == "__main__":
    start_socket()