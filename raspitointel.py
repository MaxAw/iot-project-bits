import socket
# import threading
import time
# import sys
import os           # run python program as root to use this

my_time_slot = 0


def raspiClient(server_ip, server_port, message):
    raspi_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    raspi_client.connect((server_ip, server_port))

    print("Connecting...")

    if message.split('.')[1] is 'txt':
        uploadFile(raspi_client, message)

    else:
        raspi_client.send(message.encode())

    recvd_data = (raspi_client.recv(1024)).decode()

    print("Recvd data : {}".format(recvd_data))

    print("Closing connection")
    raspi_client.close()

    return recvd_data


def uploadFile(raspi_client, file_name):

    # open file to send data
    send_file = open(file_name, 'rb')
    message = send_file.read(1024)
    while message:
        print("Sending...       ")
        raspi_client.send(message)
        message = send_file.read(1024)

    send_file.close()
    print("~~ Sent! ~~")

    # delete file to make space for new data
    os.remove(file_name)


def wifiSleepWake(status):

    if status:
        # switch on Wi-Fi
        wifi_cmd = "ifconfig wlan0 up"
        os.system(wifi_cmd)

    else:
        # switch off Wi-Fi
        wifi_cmd = "ifconfig wlan0 down"
        os.system(wifi_cmd)


def timeScheduler(my_id, server_ip, server_port, filename, time_info):

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
            if not wait_time:
                wait_counter = 1
            else:
                wifiSleepWake(0)
                time.sleep(wait_time)
                wait_counter = 1

        if not wait_time:
            pass
        else:
            wifiSleepWake(1)

        print("Sending...")
        time_info = raspiClient(server_ip, server_port, filename)

        if time_info != current_time_info:
            reset_time = time_period - wait_time        # wait for reset_time before updating to new schedule
            wifiSleepWake(0)
            time.sleep(reset_time)
            wait_counter = 0
            continue

        print("Waiting for next slot...")
        wifiSleepWake(0)
        time.sleep(time_period)


def setupRaspi(my_id, my_ip, my_port, server_ip, server_port, filename):

    my_data = my_id + '%' + my_ip + '%' + str(my_port)

    time_info = raspiClient(server_ip, server_port, my_data)

    # wait for intel server to set up
    time.sleep(5)

    timeScheduler(my_id, server_ip, server_port, filename, time_info)
