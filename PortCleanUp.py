import socket

class SocketCleaner:
    def __init__(self, address=('127.0.0.1', 5001)):
        self.server_address = address

    def cleanup(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        port_number = self.server_address[1]
        print(f"Closing socket bound to port {port_number}")
        try:
            sock.bind(self.server_address)
            print(f"    Socket closed")
        except OSError as e:
            print(f"    Socket bind failed: {e}")
        finally:
            sock.close()


if __name__ == "__main__":
    cleaner = SocketCleaner()
    cleaner.cleanup()
