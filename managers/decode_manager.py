import subprocess
import threading
import datetime
import pause
import json
import time
from subprocess import Popen, PIPE

import utils
from managers import flyby_manager
import satellites
import globals


def decode(transmission_type, t_start, sat_name, name, freq, duration, temp, output, metadata, delete):
    dt = datetime.datetime.strptime(t_start, '%Y-%m-%d %H:%M:%S')
    pause.until(dt)
    globals.LOGGER.info("decoding image from satellite:\n"
                        f"* satellite name    : {sat_name}\n"
                        f"* transmission type : {transmission_type}\n"
                        f"* frequency         : {freq}\n"
                        f"* duration          : {duration}")
    globals.LAST_ACTION = f"{t_start} decoding {sat_name} {transmission_type} transmission on {freq}Mhz"
    t = 'error'
    if transmission_type == "APT":
        t = subprocess.Popen(
            ['gnome-terminal', '--', f'{globals.PATH}/decoders/apt_decode.sh', '-n', f'{name}', '-f', f'{freq}', '-t',
             f'{duration}', '-p', f'{temp}', '-o', f'{output}', '-m', metadata, '-d', str(delete)], stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
    elif transmission_type == "LRPT":
        t = subprocess.Popen(
            ['gnome-terminal', '--', f'{globals.PATH}/decoders/lrpt_decode.sh', '-n', f'{name}', '-f', f'{freq}', '-t',
             f'{duration}', '-p', f'{temp}', '-o', f'{output}', '-m', metadata, '-d', str(delete)], stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
    else:
        globals.LAST_ACTION = "cannot decode: unsupported decoding type"
    time.sleep(int(duration))
    stdout, stderr = t.communicate()
    globals.LOGGER.info("decoded image from satellite:\n"
                        f"{stdout, stderr}")

    globals.LAST_ACTION = f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} decoded {sat_name} {transmission_type} transmission on {freq}Mhz"


def decode_manager(sats: [satellites.satellite], t_in, t_out, angle, delete_temp: bool, temp: str, output: str):
    while True:
        delay = t_out.timestamp() - t_in.timestamp()
        flyby_list = flyby_manager.get_flyby_filtered_list(sats, t_in, t_out, angle)
        for key in flyby_list["events"]:
            duration = int(flyby_list["events"][key]["duration"])
            event_start = utils.utc_to_lc(str(flyby_list["events"][key]["rise"]["time"]))
            sat_name = str(flyby_list["events"][key]["name"])

            utc_epoch_rise = flyby_list["events"][key]["rise"]["epoch"]
            utc_epoch_culminate = flyby_list["events"][key]["culminate"]["epoch"]
            utc_epoch_set = flyby_list["events"][key]["set"]["epoch"]

            utc_time_rise = datetime.datetime.strptime(flyby_list["events"][key]["rise"]["time"], '%Y-%m-%d %H:%M:%S')
            utc_time_culminate = datetime.datetime.strptime(flyby_list["events"][key]["culminate"]["time"],
                                                            '%Y-%m-%d %H:%M:%S')
            utc_time_set = datetime.datetime.strptime(flyby_list["events"][key]["set"]["time"], '%Y-%m-%d %H:%M:%S')

            for sat in sats:
                if sat_name == sat.name:

                    time_rise = sat.datetime_to_utc(utc_time_rise)
                    time_culminate = sat.ts.utc(utc_time_culminate.year,
                                                utc_time_culminate.month,
                                                utc_time_culminate.day,
                                                utc_time_culminate.hour,
                                                utc_time_culminate.minute,
                                                utc_time_culminate.second)
                    time_set = sat.ts.utc(utc_time_set.year,
                                          utc_time_set.month,
                                          utc_time_set.day,
                                          utc_time_set.hour,
                                          utc_time_set.minute,
                                          utc_time_set.second)

                    if json.loads(utils.read_file('config/setup.json'))["decode_settings"]['write_metadata'] is True:
                        metadata = json.dumps({"status": "metadata_enabled",
                                               "satellite_name": sat_name,
                                               "transmission_type": sat.type,
                                               "frequency": sat.freq,
                                               "tle_line1": sat.line1,
                                               "tle_line2": sat.line2,
                                               "rise":
                                                   {
                                                       "epoch": utc_epoch_rise,
                                                       "time": str(utc_time_rise),
                                                       "pos": sat.get_position(time_rise),
                                                       "perspective": sat.get_perspective_info(time_rise)
                                                   },
                                               "culminate":
                                                   {
                                                       "epoch": utc_epoch_culminate,
                                                       "time": str(utc_time_culminate),
                                                       "pos": sat.get_position(time_culminate),
                                                       "perspective": sat.get_perspective_info(time_culminate)
                                                   },
                                               "set":
                                                   {
                                                       "epoch": utc_epoch_set,
                                                       "time": str(utc_time_set),
                                                       "pos": sat.get_position(time_set),
                                                       "perspective": sat.get_perspective_info(time_set)
                                                   },
                                               "flyby_duration": duration,
                                               "ground_station_lat": globals.POS["lat"],
                                               "ground_station_lon": globals.POS["lon"],
                                               "utc": utils.get_utc_offset()})
                    else:
                        metadata = json.dumps({"status": "metadata_disabled"})
                    decode_thread = threading.Thread(target=decode,
                                                     kwargs={
                                                         "transmission_type": sat.type,
                                                         "t_start": event_start,
                                                         "sat_name": sat.name,
                                                         "name": f"{event_start} {sat.name}",
                                                         "freq": sat.freq,
                                                         "duration": duration,
                                                         "temp": temp,
                                                         "output": output,
                                                         "metadata": metadata,
                                                         "delete": delete_temp})
                    decode_thread.start()
                    break

        # testing
        decode_thread = threading.Thread(target=decode,
                                         kwargs={"transmission_type": 'APT',
                                                 "t_start": '2022-02-28 14:20:00',
                                                 "sat_name": 'meteor',
                                                 "name": f"test",
                                                 "freq": '69',
                                                 "duration": '10',
                                                 "temp": 'temp',
                                                 "output": 'output',
                                                 "metadata": json.dumps({"status": "metadata_enabled"}),
                                                 "delete": delete_temp})
        decode_thread.start()

        globals.LAST_ACTION = f"scheduled flyby decode for {len(flyby_list['events'])} events"
        globals.LOGGER.info(f"scheduled flyby decode for {len(flyby_list['events'])} events")
        time.sleep(delay)
