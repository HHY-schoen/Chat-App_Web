from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import time

HOST = 'localhost'  #監聽所有可用的網路介面
PORT = 5500
ADDR = (HOST, PORT)  #在 bind 操作中使用(主機,端口)
MAX_CONNETIONS = 10
BUFSIZ = 512


messages= []

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(ADDR)


def receive_messages():
        while True:
            try:
                msg = client_socket.recv(BUFSIZ).decode()
                messages.append(msg)
                print(msg)
            except Exception as e:
                print("[EXCEPTION]", e)
                break


def send_message(msg):
    client_socket.send(bytes(msg, 'utf8'))
    if msg == 'quit':
        client_socket.close()


receive_thread = Thread(target=receive_messages)
receive_thread.start()

send_message("Joe")
time.sleep(2)
send_message("Hello")
time.sleep(2)
send_message("{quit}")