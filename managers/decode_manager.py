import subprocess
import threading
import datetime
import pause
import time

import utils
from managers import flyby_manager
import satellites
import globals


def decode(transmission_type, t_start, sat_name, name, freq, duration, temp, output):
    dt = datetime.datetime.strptime(t_start, '%Y-%m-%d %H:%M:%S')
    pause.until(dt)
    globals.LAST_ACTION = f"{t_start} decoding {sat_name} {transmission_type} transmission on {freq}Mhz"
    if transmission_type == "APT":
        subprocess.call(['gnome-terminal', '--', f'{globals.PATH}/decoders/apt_decode.sh', '-n', f'{name}', '-f', f'{freq}', '-t', f'{duration}', '-p', f'{temp}', '-o', f'{output}'])
    elif transmission_type == "LRPT":
        subprocess.call(['gnome-terminal', '--', f'{globals.PATH}/decoders/lrpt_decode.sh', '-n', f'{name}', '-f', f'{freq}', '-t', f'{duration}', '-p', f'{temp}', '-o', f'{output}'])
    else:
        globals.LAST_ACTION = "cannot decode: unsupported decoding type"
    time.sleep(int(duration))
    globals.LAST_ACTION = f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} decoded {sat_name} {transmission_type} transmission on {freq}Mhz"


def decode_manager(sats: [satellites.satellite], t_in, t_out, angle, delete_temp: bool, temp: str, output: str):
    while True:
        delay = t_out.timestamp() - t_in.timestamp()
        flyby_list = flyby_manager.get_flyby_filtered_list(sats, t_in, t_out, angle)
        for key in flyby_list["events"]:
            duration = int(flyby_list["events"][key]["duration"])
            event_start = utils.utc_to_lc(str(flyby_list["events"][key]["rise"]["time"]))
            sat_name = str(flyby_list["events"][key]["name"])
            for sat in sats:
                if sat_name == sat.name:
                    decode_thread = threading.Thread(target=decode,
                                                     kwargs={"transmission_type": sat.type,
                                                             "t_start": event_start,
                                                             "sat_name": sat.name,
                                                             "name": f"{event_start} {sat.name}",
                                                             "freq": sat.freq,
                                                             "duration": duration,
                                                             "temp": temp,
                                                             "output": output})
                    decode_thread.start()

        # testing
        '''decode_thread = threading.Thread(target=decode,
                                         kwargs={"transmission_type": 'LRPT',
                                                 "t_start": '2022-02-28 14:20:00',
                                                 "sat_name": 'meteor',
                                                 "name": f"test",
                                                 "freq": '69',
                                                 "duration": '10',
                                                 "temp": 'temp',
                                                 "output": 'output'})
        decode_thread.start()'''

        globals.LAST_ACTION = f"scheduled flyby decode for {len(flyby_list['events'])} events"
        time.sleep(delay)
