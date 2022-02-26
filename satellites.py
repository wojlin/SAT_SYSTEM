from skyfield.api import load, wgs84, EarthSatellite
from datetime import datetime, timedelta

import globals


class satellite:
    def __init__(self, name, line1, line2, freq, type):
        self.name = name
        self.line1 = line1
        self.line2 = line2
        self.freq = freq
        self.type = type
        self.ts = load.timescale()
        self.sat = EarthSatellite(self.line1, self.line2, self.name, self.ts)

    @staticmethod
    def get_current_utc():
        return load.timescale().utc(datetime.utcnow().year,
                                    datetime.utcnow().month,
                                    datetime.utcnow().day,
                                    datetime.utcnow().hour,
                                    datetime.utcnow().minute,
                                    datetime.utcnow().second)

    def get_position(self, t_in_UTC):
        geocentric = self.sat.at(t_in_UTC)
        lat, lon = wgs84.latlon_of(geocentric)
        return {"lat": lat.degrees, "lon": lon.degrees}

    def get_direction(self):
        pos1 = self.get_position(self.get_current_utc())
        pos2 = self.get_position(self.get_current_utc() + timedelta(seconds=1))
        if pos1["lat"] > pos2["lat"]:
            direction = "down"
        else:
            direction = "up"
        return direction

    def get_perspective_info(self, t_in_UTC):
        bluffton = wgs84.latlon(globals.POS["lat"], globals.POS["lon"])
        difference = self.sat - bluffton
        topocentric = difference.at(t_in_UTC)
        alt, az, distance = topocentric.altaz()
        direction = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N'][int((int(az.degrees)*9)/360)]

        return {"altitude": alt.degrees, "azimuth": az.degrees, "direction": direction, "distance": distance.km}

    def get_passes(self, t_in_UTC, t_out_UTC, degree):
        bluffton = wgs84.latlon(globals.POS["lat"], globals.POS["lon"])
        t0 = self.ts.utc(t_in_UTC.year,
                         t_in_UTC.month,
                         t_in_UTC.day,
                         t_in_UTC.hour,
                         t_in_UTC.minute,
                         t_in_UTC.second)
        t1 = self.ts.utc(t_out_UTC.year,
                         t_out_UTC.month,
                         t_out_UTC.day,
                         t_out_UTC.hour,
                         t_out_UTC.minute,
                         t_out_UTC.second)
        t, events = self.sat.find_events(bluffton, t0, t1, altitude_degrees=0)

        list_events = {"settings": {
            "start_epoch": t_in_UTC.timestamp(),
            "end_epoch": t_out_UTC.timestamp(),
            "start_utc": t_in_UTC.strftime('%Y-%m-%d %H:%M:%S'),
            "end_utc": t_out_UTC.strftime('%Y-%m-%d %H:%M:%S'),
            "min_degree": degree},
            "events": {}}

        log = {}
        good = False
        event_dict_name = 'none'
        for ti, event in zip(t, events):
            name = ('rise', 'culminate', 'set')[event]
            info = self.get_perspective_info(ti)
            log[name] = {**{"time": ti.utc_strftime('%Y-%m-%d %H:%M:%S'), "epoch": ti.utc_datetime().timestamp()}, **info}
            if event == 1 and info["altitude"] > degree:
                good = True
                event_dict_name = ti.utc_datetime().timestamp()
            if event == 2 and good and "rise" in log:
                duration = float(log["set"]["epoch"]) - float(log["rise"]["epoch"])
                list_events["events"][event_dict_name] = {**{"name": self.name}, **{"duration": duration}, **log}
            if event == 2:
                log = {}
                good = False

        return list_events

    def get_perspective_path(self, t_in_UTC, t_out_UTC, resolution):
        path_json = {}
        delta_time = t_out_UTC - t_in_UTC
        time_segment = delta_time / resolution

        time_points = []
        for x in range(resolution):
            _standard_time = (t_in_UTC + (x * time_segment))
            _skyfield_time = self.ts.utc(_standard_time.year,
                                         _standard_time.month,
                                         _standard_time.day,
                                         _standard_time.hour,
                                         _standard_time.minute,
                                         _standard_time.second)
            time_points.append(_skyfield_time)

        x = 0
        for point in time_points:
            path_json[str(x)] = self.get_perspective_info(point)
            x += 1

        return path_json

    def get_position_path(self, t_in_UTC, t_out_UTC, resolution):
        path_json = {}
        delta_time = t_out_UTC - t_in_UTC
        time_segment = delta_time / resolution

        time_points = []
        for x in range(resolution):
            _standard_time = (t_in_UTC + (x * time_segment))
            _skyfield_time = self.ts.utc(_standard_time.year,
                                         _standard_time.month,
                                         _standard_time.day,
                                         _standard_time.hour,
                                         _standard_time.minute,
                                         _standard_time.second)
            time_points.append(_skyfield_time)

        x = 0
        for point in time_points:
            path_json[str(x)] = self.get_position(point)
            x += 1

        return path_json

    def get_epoch(self):
        days = self.get_current_utc() - self.sat.epoch
        return days

    def get_doppler(self):
        t = self.get_current_utc()
        bluffton = wgs84.latlon(globals.POS["lat"], globals.POS["lon"])
        pos = (self.sat - bluffton).at(t)
        _, _, the_range, _, _, range_rate = pos.frame_latlon_and_rates(bluffton)

        new_range = -range_rate.m_per_s
        freq_HZ = self.freq * 1000000
        shift = 299792458 / (299792458 + new_range) * freq_HZ
        doppler = freq_HZ - shift
        return doppler

    def get_json(self):
        out_json = {"name": self.name,
                    "freq": self.freq,
                    "type": self.type,
                    "epoch": self.get_epoch(),
                    "doppler": self.get_doppler(),
                    "direction": self.get_direction(),
                    "position": self.get_position(self.get_current_utc()),
                    "perspective": self.get_perspective_info(self.get_current_utc())}
        return out_json

    def __repr__(self):
        return self.name
