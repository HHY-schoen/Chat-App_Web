from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread, Lock
import time


class Client:
    """
    for communication with server
    """
    HOST = "192.168.0.21"
    PORT = 5500
    ADDR = (HOST, PORT)
    BUFSIZ = 512

    def __init__(self, name):
        """
        Init object and send name to server
        :param name: str
        """
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.client_socket.connect(self.ADDR)
        self.messages = []
        receive_thread = Thread(target=self.receive_messages)
        receive_thread.start()
        self.send_message(name)
        self.lock = Lock()  #確保在多執行緒環境中，對共享資源的訪問是安全的

    def receive_messages(self):
        """
        receive messages from server
        :return: None
        """
        while True:
            try:
                msg = self.client_socket.recv(self.BUFSIZ).decode()  #recv:接收從伺服器發送來的消息

                # 防止多個執行緒同時修改 self.messages，確保一次只有一個執行緒能夠訪問
                self.lock.acquire()  
                self.messages.append(msg)
                self.lock.release()  #釋放鎖，允許其他執行緒訪問 self.messages
            except Exception as e:
                print("[EXCPETION]", e)
                break

    def send_message(self, msg):
        """
        send messages to server
        :param msg: str
        :return: None
        """
        try:
            self.client_socket.send(bytes(msg, "utf8"))
            if msg == "{quit}":
                self.client_socket.close()
        except Exception as e:
            self.client_socket = socket(AF_INET, SOCK_STREAM)  #重新創建 socket，重新連接伺服器
            self.client_socket.connect(self.ADDR)  #重新連接伺服器
            print(e)

    def get_messages(self):
        """
        :returns a list of str messages
        :return: list[str]
        """
        messages_copy = self.messages[:]

        # 確保對 self.messages 這個共享資源的訪問是線程安全的，使用鎖來防止多個執行緒同時修改 self.messages
        self.lock.acquire()
        self.messages = []  #清空 self.messages 列表，複本已保存在 messages_copy 中
        self.lock.release()

        return messages_copy
    
    def disconnect(self):
        self.send_message("{quit}")