import socket

# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
client_socket.connect(("localhost", 12345))

# Send data to the server
action = input("Enter your action: ")
client_socket.send(action.encode())

# Receive data from the server
data = client_socket.recv(1024)

# Print the received data
print("Received: ", data.decode())
client_socket.close()