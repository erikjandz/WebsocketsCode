import socket

# Some global variables
HEADER = 64
PORT = 5050
SERVER = "192.168.99.1"
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)
print("[CONNECTED] connected to server...")


# Update our file that got updated on the server
def writeFile(content):
    f = open("client.txt", "w")
    f.write(content)
    f.close()


# Main function to listen to the server and update our file
def handle_server():
    try:
        while True:
            message = client.recv(2048).decode(FORMAT)
            writeFile(message)
            print("[FILE UPDATED] client.txt got updated.")

    except Exception:
        print("[DISCONNECTED] we disconnected from the server.")


# Function to make sending data easier
def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    print("[MESSAGE SENT] message sent to server.")


send("Connected")
writeFile(client.recv(2048).decode(FORMAT))

handle_server()

# send(DISCONNECT_MESSAGE)
