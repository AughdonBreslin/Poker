import socket
from threading import Thread

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to a specific address and port
server_socket.bind(("localhost", 12345))

# Listen for incoming connections
server_socket.listen(5)

# List to store the clients
clients = []

# Function to handle a client's actions
def handle_client(client):
    client_socket, addr = client
    while True:
        # Receive data from the client
        data = client_socket.recv(1024)
        if not data:
            clients.remove(client)
            client_socket.close()
            break
        # Process the data
        print("Received: ", data.decode())
        # Send a response to the client
        client_socket.send(b"Action received.")

while True:
    # Establish a connection with the client
    client = server_socket.accept()
    clients.append(client)
    # Create a new thread for each client
    Thread(target=handle_client, args=(client,)).start()