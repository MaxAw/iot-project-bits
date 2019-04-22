import socket
import threading
import time
import sys

my_time_slot = 0


# def raspiServer(my_ip, my_port):
#     global my_time_slot

#     raspi_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     raspi_server.bind((my_ip, my_port))
#     raspi_server.listen(5)

#     print("Server Started at {}:{}".format(my_ip, my_port))

#     conn, addr = raspi_server.accept()
#     # receive time slot
#     my_time_slot = (conn.recv(1024)).decode()

#     # reply acknowledgement
#     conn.send(b'ACK')
#     conn.close()
#     raspi_server.close()


def raspiClient(server_ip, server_port, message):
    raspi_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    raspi_client.connect((server_ip, server_port))

    print("Connecting...")

    raspi_client.send(message.encode())
    recvd_data = (raspi_client.recv(1024)).decode()

    print("Recvd data : {}".format(recvd_data))

    print("Closing connection")
    raspi_client.close()

    return recvd_data


def timeScheduler(my_id, server_ip, server_port, filename, time_info):
    global my_time_slot

    wait_counter = 0

    while True:

        current_time_info = time_info

        time_period = int((time_info.split("%"))[0])         # total time period
        num_of_hosts = int((time_info.split("%"))[1])        # number of PIs connected to Intel Board

        time_slots = time_period / num_of_hosts         # time slot for each PI
        # print("TIMESLOT : {}".format(time_slots))
        wait_time = (int(my_id) - 1) * time_slots       # total time to wait for before sending data

        if not wait_counter:
            print("Waiting for my slot... {}".format(wait_time))
            time.sleep(wait_time)
            wait_counter = 1

        print("Sending...")
        time_info = raspiClient(server_ip, server_port)

        if time_info != current_time_info:
            reset_time = time_period - wait_time        # wait for reset_time before updating to new schedule
            time.sleep(reset_time)
            wait_counter = 0
            continue

        print("Waiting for next slot...")
        time.sleep(time_period)


def setupRaspi(my_id, my_ip, my_port, server_ip, server_port, filename):
    # global my_time_slot

    # my_id = sys.argv[1]
    # my_ip = '127.0.0.1'
    # my_port = int(sys.argv[2])

    # server_ip = '127.0.0.1'
    # server_port = int(sys.argv[3])

    # begin server thread
    # raspi_server = threading.Thread(target=raspiServer, args=(my_ip, my_port, ))
    # raspi_server.start()

    # connect to Intel server
    # send data in the format - 'RP1%192.168.0.1%8000'

    my_data = my_id + '%' + my_ip + '%' + str(my_port)

    time_info = raspiClient(server_ip, server_port, my_data)

    # wait for intel server to set up
    time.sleep(5)

    timeScheduler(my_id, )
    data_to_send = 'This is RP {}'.format(my_id)


if __name__ == '__main__':
    setupRaspi()
