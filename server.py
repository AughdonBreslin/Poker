import socket
from threading import Thread
from poker import play
from table import Board, Hand, Table
from collections import deque
import time

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to a specific address and port
server_socket.bind(("localhost", 12345))

# Listen for incoming connections
server_socket.listen(5)

# CAPITAL LETTERS IMPLY THAT THESE ARE CONSTANTS YOU CAN CHANGE :) 
# LIKE CONFIG SETTINGS
MINPLAYERS = 2 #minimum players needed by server to start a game

# List to store the clients
clients = []
roundnumber = 0
numPlayers = 0
currentActor = ""
started = False
table = Table()
table.actionQueue = type('stack', (list,), {'push':list.append})()
global command_received
command_received = False


def isActionOn(table, playerid):
        if table.actionQueue[0] == playerid:
            return True
        else:
            return False

def commenceRound(table, roundNumber):
        table.dealToHands()
        table.actionQueue = []
        table.inAction = []
        print(str(table.playerids))
        for i in range(0, table.numPlayers - 1):
            print("button: " + str(table.button))
            print("numplayers: " + str(table.numPlayers))
            print("i: " + str(i))
            table.actionQueue.append(table.playerids[table.button + i % table.numPlayers])

            table.inAction.append(table.playerids[table.button + i % table.numPlayers])
        global currentActor
        currentActor = table.actionQueue.pop()
        print("currentActor: " + str(currentActor))
    
        

        print("actionQueue: " + str(table.actionQueue))
        
        table.board.dealToBoard(3)
        # wait
        table.board.dealToBoard()
        # wait
        table.board.dealToBoard()
        # print(f"{Table.board}\n")
        # wait


def process(command):
    global command_received
    command_received = True  # Set the flag to indicate command received
    response = ""

    ### COMMAND: bet {VALUE}
    if command.startswith("bet"):
        value = command.split()[1]
        # Process the bet command with the provided value
        
        # the list mess below just reorganizes the action queue 
        table.actionQueue = table.inAction[table.inAction.index(currentActor) :] + table.inAction[: table.inAction.index(currentActor)] 
        table.actionQueue.remove(currentActor)

        response = f"You placed a bet of {value}" # sent to user

    ### COMMAND: fold
    elif command == "fold":
        # Process the fold command
        table.inAction.remove(currentActor)
        table.actionQueue.pop()
        response = "You folded"

    ### COMMAND: call  
    elif command == "call":
        table.actionQueue.pop()
        # Process the call command
        response = "You called"

    ### COMMAND: playersinhand   
    elif command == "playersinhand":
        response = "Players in hand: "
        responselist = table.inAction[table.inAction.index(currentActor) :] + table.inAction[: table.inAction.index(currentActor)] 
        for player in responselist:
            response += " " + str(player)
            
    elif command == "getboard":
        # Process the getBoard command
        response = "Board: ..."
    elif command == "getmycards":
        # Process the getMyCards command
        response = "Your cards: ..."
    elif command == "getmyhandranking":
        # Process the getMyHandRanking command
        response = "Your hand ranking: ..."
    elif command == "/help":
        response = "commands are: " + "fold, " + "call, " + "raise <value>, " + "playersinhand, " + "getboard, " + "getmycards, " + "getmyhandranking, " + "/help"
    else:
        response = "Invalid command. Use /help to see commands."
    return response


def handle_client(client):
    client_socket, addr = client
    table.addPlayer(client)
    table.playerids.append(client)
    print("numplayers = " + "table: " + str(table.numPlayers))
    buffer = ""  # Buffer to store received data
    while True:
        # Receive data from the client
        data = client_socket.recv(1024)
        if not data:
            clients.remove(client)
            table.removePlayer(client)
            client_socket.close()
            break
        # Process the data character by character
        for char in data.decode():
            if char == '\n' or char == '\r':
                if buffer:  # Process the command if the buffer is not empty
                    command = buffer.strip()
                    response = process(command)  # sends client input to process(), receives response string
                    client_socket.send(response.encode())  # sends a response to the client
                    buffer = ""  # Reset the buffer
            else:
                buffer += char  # Add the character to the buffer

        # Check if a complete command is received
        if '\n' in data.decode() or '\r' in data.decode():
            if buffer:  # Process the command if the buffer is not empty
                command = buffer.strip()
                response = process(command)  # sends client input to process(), receives response string
                client_socket.send(response.encode())  # sends a response to the client
                buffer = ""  # Reset the buffer

        if currentActor == client:
            response = "waiting for your action ..."  # Prompt for the current actor
            client_socket.send(response.encode())  # sends a response to the client
        else:
            response = "waiting for other player actions ..."
            client_socket.send(response.encode())  # sends a response to the client



while True:
    if table.numPlayers >= MINPLAYERS:
        print("player minimum reached")
        if not started:
            numPlayers = table.numPlayers
            table = Table(numPlayers)
            started = True
            commenceRound(table, 0)
            print("round commenced!")
        
    # Establish a connection with the client
    client = server_socket.accept()
    clients.append(client)
    # Create a new thread for each client
    Thread(target=handle_client, args=(client, )).start()
    

def main():
    run_server(table)
    
    

if __name__ == "__main__":
    main()