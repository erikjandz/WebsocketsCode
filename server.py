import socket
import threading
import time

# Some global variables
HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)


# Simple function to read from the server.txt file
# and return the content as a string
def readFile() -> str:
    f = open("server.txt", "r")
    text = f.read()
    f.close()
    return text


# Send the file updated somewhere else to all the clients
def send_file_to_clients(registered_connections: list, new_file: str) -> None:
    for conn in registered_connections:
        conn.send(new_file.encode(FORMAT))
    print("[UPDATE ALL CLIENTS FILES] the files from the clients are updated")


# If the server.txt changes,
# this thread will send the changed file to the clients
def handle_file_changes(registered_connections: list, dummy_item: str) -> None:
    last_file_content = readFile()
    while True:
        new_file_content = readFile()
        if last_file_content != new_file_content:
            last_file_content = new_file_content
            print("[FILE CHANGED] the server.txt file changed content")
            send_file_to_clients(registered_connections, last_file_content)
        time.sleep(1)


# simple function to receive a message from a client
def recv(conn):
    msg_length = conn.recv(HEADER).decode(FORMAT)
    if msg_length:
        msg_length = int(msg_length)
        return conn.recv(msg_length).decode(FORMAT)
    return False


# Thread for every client so the server can listen to all of them
# if they want to disconnect
def handle_client(registered_connections: list, conn, addr: str) -> None:
    print(f"[NEW CONNECTION] {addr} connected.")
    connected = True
    try:
        # get the first message from the client
        msg = recv(conn)
        if msg:
            print(f"[{addr}] {msg}")

        # then send the current content of the server.txt file
        conn.send(readFile().encode(FORMAT))

        # then keep listening to the client
        # until they disconnect or send a message
        while connected:
            msg = recv(conn)
            if msg:
                if msg == DISCONNECT_MESSAGE:
                    print(f"[DISCONNECTED] {addr} disconnected.")
                    connected = False
                    registered_connections.remove(conn)
                    conn.close()

                print(f"[{addr}] {msg}")

    # When an error occurred
    # it's most likely because the client disconnected so we remove him
    # and end the thread by leaving the function
    except Exception:
        print(f"[DISCONNECTED] {addr} disconnected.")
        registered_connections.remove(conn)
        conn.close()


# Loop to register new clients
def start() -> None:
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")

    registered_connections = list()

    # start a thread that checks the server.txt file for updates
    file_handle_thread = threading.Thread(target=handle_file_changes,
                                          args=(registered_connections,
                                                "dummy_item"))
    file_handle_thread.start()

    # infinite loop to look for new clients to accept
    # and start a thread for every new client that listens to it
    while True:
        conn, addr = server.accept()
        registered_connections.append(conn)

        # start a thread for the specific client to listen to him for updates
        client_handle_thread = threading.Thread(target=handle_client,
                                                args=(registered_connections,
                                                      conn, addr))
        client_handle_thread.start()
        print(f"[ACTIVE CONNECTIONS] {len(registered_connections)}")


print("[STARTING] server is starting...")
start()
