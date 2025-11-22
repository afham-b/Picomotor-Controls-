import socket
import threading

def send_test_data():
    test_data = '1.0,1.0 Hello Port Open and Useable'  # Simulate some realistic test data
    pico_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('127.0.0.1', 1278)
    try:
        pico_sock.sendto(test_data.encode(), server_address)
        print("Test data sent:", test_data)
    finally:
        pico_sock.close()

def receive_test_data():
    pico_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    pico_sock.bind(('127.0.0.1', 1278))
    try:
        data, _ = pico_sock.recvfrom(4096)
        print("Test data received:", data.decode())
    finally:
        pico_sock.close()

def main():
    # Create a thread to receive data
    receiver_thread = threading.Thread(target=receive_test_data)
    receiver_thread.start()

    # Send test data
    send_test_data()

    # Wait for the receiver to finish
    receiver_thread.join()

if __name__ == '__main__':
    main()
