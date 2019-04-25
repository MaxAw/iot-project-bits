import socket
import threading
import time
import sys


# maintain a dictionary of host ID and IP address
host_dict = {}
time_info = '120%3'     # TODO : modify if no. of hosts unknown


def intelServer(my_ip, my_port, phase):
    global host_dict
    global time_info

    host_count = 0
    slot = 0

    intel_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    intel_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)         # reuse port if not free
    intel_server.bind((my_ip, my_port))
    intel_server.listen(5)

    print("Server Started at {}:{}".format(my_ip, my_port))

    while True:
        conn, addr = intel_server.accept()
        recvd_data = (conn.recv(1024)).decode()
        print("{} at {}".format(recvd_data, time.ctime()))

        if phase == 0:
            # data received as 'RP1%192.168.0.1%8000'

            host_id = (recvd_data.split('%'))[0]
            host_ip = (recvd_data.split('%'))[1]
            host_port = int((recvd_data.split('%'))[2])

            # add host information to host dictionary
            host_dict[host_count] = [host_id, (host_ip, host_port)]
            host_count = host_count + 1
            # reply time information
            conn.send(time_info.encode())

            # TODO : modify if no. of hosts unknown
            if host_count == 2:
                break
        else:
            host_id = host_dict[slot][0]
            # store recvd_data as file
            downloadFile(host_id, conn, recvd_data)
            slot = (slot + 1) % 2
            # reply time information
            conn.send(time_info.encode())

    conn.close()
    intel_server.close()

    print("Server Closed at {}:{}".format(my_ip, my_port))


def intelClient(server_ip, server_port, file_name):
    intel_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    intel_client.connect((server_ip, server_port))

    # send file to gateway
    uploadFile(intel_client, file_name)

    recvd_data = (intel_client.recv(1024)).decode()
    print(recvd_data)

    print("Closing connection")
    intel_client.close()


def uploadFile(intel_client, file_name):

    # open file to send data
    send_file = open(file_name, 'rb')
    message = send_file.read(1024)
    while message:
        print("Sending...       ")
        intel_client.send(message)
        message = send_file.read(1024)

    send_file.close()
    print("~~ Sent! ~~")


def downloadFile(host_id, conn, recvd_data):

    file_name = 'file' + host_id + '.txt'
    # open file to store received data (will overwrite old data)
    recv_file = open(file_name, 'wb')

    while recvd_data:
        print("Receiving...     ")

        # add timestamp to received data
        data_with_timestamp = "Data received at " + time.ctime() + " : " + recvd_data
        recv_file.write(data_with_timestamp)
        recvd_data = conn.recv(1024)
        # print("{} at {}".format(recvd_data, time.ctime()))

    # save file contents
    recv_file.close()

    print("~~ Received! ~~")


def generateTime(default):
    global host_dict

    default_time_period = 2 * 60
    num_of_hosts = len(host_dict) + 1       # add one for intel board time slot

    if default:
        time_info = str(default_time_period) + "%" + str(num_of_hosts)

    else:
        time_period = int(input("Enter time period: "))
        time_info = str(time_period) + "%" + str(num_of_hosts)

    return time_info


def setupIntelBoard():
    global host_dict
    global time_info

    my_ip = sys.argv[1]
    my_port = int(sys.argv[2])

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
