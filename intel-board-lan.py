import socket
import threading
import time
import sys


# maintain a dictionary of host ID and IP address
host_dict = {}
time_info = '120%2'


def intelServer(my_ip, my_port, phase):
    global host_dict
    global time_info

    intel_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    intel_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)         # reuse port if not free
    intel_server.bind((my_ip, my_port))
    intel_server.listen(5)

    print("Server Started at {}:{}".format(my_ip, my_port))

    while True:
        conn, addr = intel_server.accept()
        recvd_data = (conn.recv(1024)).decode()
        print("{} at {}".format(recvd_data, time.ctime()))

        # reply time information
        conn.send(time_info.encode())

        if phase == 0:
            # data received as 'RP1%192.168.0.1%8000'
            host_id = (recvd_data.split('%'))[0]
            host_ip = (recvd_data.split('%'))[1]
            host_port = int((recvd_data.split('%'))[2])

            # add host information to host dictionary
            host_dict[host_id] = ((host_ip, host_port))

            # TODO : modify if no. of hosts unknown
            if len(host_dict) == 2:
                break

    conn.close()
    intel_server.close()

    print("Server Closed at {}:{}".format(my_ip, my_port))


def intelClient(server_ip, server_port, message):
    intel_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    intel_client.connect((server_ip, server_port))
    intel_client.send(message.encode())
    recvd_data = (intel_client.recv(1024)).decode()
    print(recvd_data)

    print("Closing connection")
    intel_client.close()


def generateTime(default):
    global host_dict

    default_time_slot = 1 * 60
    default_time_period = 2 * 60
    num_of_hosts = len(host_dict)

    if default:
        time_info = str(default_time_period) + "%" + str(num_of_hosts)

    else:
        time_period = int(input("Enter time period: "))
        time_info = str(time_period) + "%" + str(num_of_hosts)

    return time_info


def setupIntelBoard():
    global host_dict
    global time_info

    my_ip = '127.0.0.1'
    my_port = int(sys.argv[1])

    # start server and accept raspi connections
    intelServer(my_ip, my_port, 0)

    time.sleep(1)

    # use default time information
    time_info = generateTime(True)

    server_thread = threading.Thread(target=intelServer, args=(my_ip, my_port, 1, ))
    server_thread.start()

    # if time information is to be changed
    time_info = generateTime(False)
    # intelServer(my_ip, my_port, 1, time_info)


if __name__ == '__main__':
    setupIntelBoard()
