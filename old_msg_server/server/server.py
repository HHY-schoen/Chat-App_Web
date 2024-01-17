from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import time
from person import Person

# GLOBAL CONSTANTS
HOST = ''  #監聽所有可用的網路介面
PORT = 5500
ADDR = (HOST, PORT)  #在 bind 操作中使用(主機,端口)
MAX_CONNETIONS = 10
BUFSIZ = 512  #每次讀取的最大位元組數(緩衝區的大小)

# GLOBAL VARIABLES
persons = []
SERVER = socket(AF_INET, SOCK_STREAM)  #AF_INET:使用IPv4地址族、SOCK_STREAM:使用面向連接的TCP協議
SERVER.bind(ADDR)  # set up server


def broadcast(msg, name):
    """
    send new messages to all clients
    :param msg: bytes["utf8"]
    :param name: str
    :return:
    """
    for person in persons:
        client = person.client
        try:
            client.send(bytes(name, "utf8") + msg)  #將字串name轉換為UTF-8編碼的字節串，以確保可以正確傳輸
        except Exception as e:
            print("[EXCEPTION]", e)


def client_communication(person):
    """
    Thread to handle all messages from client
    :param person: Person
    :return: None
    """
    client = person.client

    # first message received is always the persons name
    name = client.recv(BUFSIZ).decode("utf8")  #接收用戶端消息
    person.set_name(name)

    msg = bytes(f"{name} has joined the chat!", "utf8")
    broadcast(msg, "")  # broadcast welcome message

    while True:  # wait for any messages from person
        msg = client.recv(BUFSIZ)  #接收用戶端消息

        if msg == bytes("{quit}", "utf8"):  # if message is quit disconnect client
            client.close()
            persons.remove(person)
            broadcast(bytes(f"{name} has left the chat...", "utf8"), "")
            print(f"[DISCONNECTED] {name} disconnected")
            break
        else:  # otherwise send message to all other clients
            broadcast(msg, name + ": ")
            print(f"{name}: ", msg.decode("utf8"))


def wait_for_connection():
    """
    Wait for connecton from new clients, start new thread once connected
    :return: None
    """
    while True:
        try:
            client, addr = SERVER.accept()  # wait for any new connections (socket method)
            person = Person(addr, client)  # create new person for connection
            persons.append(person)

            print(f"[CONNECTION] {addr} connected to the server at {time.time()}")
            Thread(target=client_communication, args=(person,)).start()  #創建一個新的執行緒，可同時處理多個客戶端連線
        except Exception as e:
            print("[EXCEPTION]", e)
            break

    print("SERVER CRASHED")


if __name__ == "__main__":  #程式碼僅在該檔案被直接執行時運行
    SERVER.listen(MAX_CONNETIONS)  #啟動伺服器，開始監聽來自客戶端的連線
    print("[STARTED] Waiting for connections...")
    ACCEPT_THREAD = Thread(target=wait_for_connection)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()  #等待被調用的執行緒(ACCEPT_THREAD)完成工作
    SERVER.close()