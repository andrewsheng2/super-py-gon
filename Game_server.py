# CITATION: Sockets starter code from Kyle
# https://kdchin.gitbooks.io/sockets-module-manual/

import socket
import threading
from queue import Queue

HOST = "127.0.0.1" # put host IP address here if playing online
PORT = 50005
BACKLOG = 2

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.bind((HOST,PORT))
server.listen(BACKLOG)
print("Looking for connections")

def handleClient(client, serverChannel, cID, clientele):
    client.setblocking(1)
    msg = ""
    while True:
        try:
            msg += client.recv(10).decode("UTF-8")
            command = msg.split("\n")
            while (len(command) > 1):
                readyMsg = command[0]
                msg = "\n".join(command[1:])
                serverChannel.put(str(cID) + " " + readyMsg)
                command = msg.split("\n")
        except:
            # we failed
            return

def serverThread(clientele, serverChannel):
    while True:
        msg = serverChannel.get(True, None)
        print("Recieved: ", msg)
        msgList = msg.split(" ")
        senderID = msgList[0]
        instruction = msgList[1]
        details = " ".join(msgList[2:])
        if (details != ""):
            for cID in clientele:
                if cID != senderID:
                    sendMsg = instruction + " " + senderID + " " + details + "\n"
                    clientele[cID].send(sendMsg.encode())
                    print("> Sent to player %s:" % cID, sendMsg[:-1])
        print()
        serverChannel.task_done()

clientele = dict()
playerNum = 0

serverChannel = Queue(100)
threading.Thread(target = serverThread, args = (clientele, serverChannel)).start()

names = [ "1", "2" ]

while True:
    client, address = server.accept()
    # myID is the key to the client in the clientele dictionary
    myID = names[playerNum]
    for cID in clientele:
        clientele[cID].send(("newPlayer %s\n" % myID).encode())
        client.send(("newPlayer %s\n" % cID).encode())
    clientele[myID] = client
    client.send(("myIDis %s \n" % myID).encode())
    print("Connection recieved from player %s" % myID)
    threading.Thread(target = handleClient, args = 
                    (client, serverChannel, myID, clientele)).start()
    playerNum += 1