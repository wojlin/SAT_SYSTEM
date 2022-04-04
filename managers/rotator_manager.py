from datetime import datetime
import time

from satellites import satellite
import globals


def manage_rotation(sat: satellite, duration):
    t_in_UTC = sat.datetime_to_utc(datetime.utcnow())
    left_duration = int(duration)
    while left_duration > 0:
        data = sat.get_perspective_info(t_in_UTC)
        globals.ROTATOR_ELEVATION = round(data["altitude"], 2)
        globals.ROTATOR_AZIMUTH = round(data["azimuth"], 2)
        time.sleep(1)
        left_duration -= 1

    globals.ROTATOR_AZIMUTH = 0.00
    globals.ROTATOR_ELEVATION = 0.00
