import socket

import inteltointernet as gateway


def intelServer(my_ip, my_port):

    intel_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    intel_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)         # reuse port if not free
    intel_server.bind((my_ip, my_port))
    intel_server.listen(5)

    print("Server Started at {}:{}".format(my_ip, my_port))

    while True:
        conn, addr = intel_server.accept()
        recvd_data = (conn.recv(1024)).decode()

    conn.close()
    intel_server.close()

    print("Server Closed at {}:{}".format(my_ip, my_port))
