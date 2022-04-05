from datetime import datetime
import threading
import socket
import time

from satellites import satellite
import globals


class tcp_manager:
    def __init__(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind((globals.ROTATOR_HOST, globals.ROTATOR_PORT))
            s.listen()
            while True:
                conn, addr = s.accept()
                thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                thread.start()
        except Exception as e:
            globals.LOGGER.error(f"cannot create rotator tcp socket:\n {e}")
            globals.LAST_ACTION = f"cannot create rotator tcp socket"

    @staticmethod
    def handle_client(conn, addr):
        globals.LOGGER.error(f"connected with rotator on address: {addr}")
        globals.LAST_ACTION = f"connected with rotator on address: {addr}"
        while True:
            packet = f"{globals.ROTATOR_AZIMUTH},{globals.ROTATOR_ELEVATION}".encode('utf-8')
            packet_length = len(packet)
            send_length = str(packet_length).encode('utf-8')
            send_length += b' ' * (64 - len(send_length))
            conn.send(send_length)
            conn.send(packet)
            time.sleep(1)


def manage_rotation(sat: satellite, duration):
    left_duration = int(duration)
    while left_duration > 0:
        t_in_UTC = sat.datetime_to_utc(datetime.utcnow())
        data = sat.get_perspective_info(t_in_UTC)
        globals.ROTATOR_ELEVATION = round(data["altitude"], 2)
        globals.ROTATOR_AZIMUTH = round(data["azimuth"], 2)
        time.sleep(1)
        left_duration -= 1

    globals.ROTATOR_AZIMUTH = 0.00
    globals.ROTATOR_ELEVATION = 0.00
