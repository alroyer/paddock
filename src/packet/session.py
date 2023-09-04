from dataclasses import dataclass

from .header import PacketHeader


@dataclass
class MarshalZone:
    zone_start: float
    zone_flag: int


@dataclass
class WeatherForecastSample:
    session_type: int
    time_offset: int
    weather: int
    track_temperature: int
    track_temperature_change: int
    air_temperature: int
    air_temperature_change: int
    rain_percentage: int


@dataclass
class PacketSessionData:
    header: PacketHeader
    weather: int
    track_temperature: int
    air_temperature: int
    total_laps: int
    track_length: int
    session_type: int
    track_id: int
    formula: int
    # session_time_left: int
    # session_duration: int
    # pit_speed_limit: int
    # game_paused: int
    # is_spectating: int
    # spectator_car_index: int
    # sli_pro_native_support: int
    # num_marshall_zone: int
    # marshal_zones: list[MarshalZone]
    # safety_car_status: int
    # network_game: int
    # num_weather_forecast_samples: int
    # weather_forecast_samples: list[WeatherForecastSample]
    # forecast_accuracy: int
    # ai_difficulty: int
    # season_link_identifier: int
    # weekend_ling_identifier: int
    # session_link_identifier: int
    # pit_stop_window_ideal_lap: int
    # pit_stop_window_lastest_lap: int
    # pit_stop_rejoin_position: int
    # steering_assist: int
    # braking_assist: int
    # gearbox_assist: int
    # pit_assist: int
    # pit_release_assist: int
    # ers_assist: int
    # drs_assist: int
    # dynamic_racing_line: int
    # dybanic_racing_line_type: int
    # game_mode: int
    # rule_set: int
    # time_of_day: int
    # session_length: int
    # speed_units_lead_player: int
    # temperature_units_lead_player: int
    # speed_units_secondary_player: int
    # temperature_units_secondary_player: int
    # num_safety_car_periods: int
    # num_virtual_safety_car_periods: int
    # num_red_flag_periods: int

    @classmethod
    def bytes_count(cls) -> int:
        return 644 - PacketHeader.bytes_count()

    @classmethod
    def unpack_format(cls) -> str:
        return '<BbbBHBbB'

    def __str__(self) -> str:
        return f'''[PacketSessionData]
    {self.header}
    weather:           {_weather_to_str(self.weather)}
    track temperature: {self.track_temperature}°
    air temperature:   {self.air_temperature}°
    track length:      {self.track_length}m
    session type:      {_session_type_to_str(self.session_type)}
    track:             {_track_id_to_str(self.track_id)}
    formula:           {_formula_to_str(self.formula)}'''


WEATHER_DEFINITION = {
    0: 'Clear',
    1: 'Light cloud',
    2: 'Overcast',
    3: 'Light rain',
    4: 'Heavy rain',
    5: 'Storm',
}


def _weather_to_str(weather: int) -> str:
    return WEATHER_DEFINITION[weather]


SESSION_TYPE_DEFINITION = {
    0: 'unknown',
    1: 'P1',
    2: 'P2',
    3: 'P3',
    4: 'short',
    5: 'Q1',
    6: 'Q2',
    7: 'Q3',
    8: 'short q',
    9: 'OSQ',
    10: 'R',
    11: 'R2',
    12: 'R3',
    13: 'time trial',
}


def _session_type_to_str(session_type: int) -> str:
    return SESSION_TYPE_DEFINITION[session_type]


TRACK_ID_DEFINITION = {
    0: 'Melbourne',
    1: 'Paul Ricard',
    2: 'Shanghai',
    3: 'Sakhir (Bahrain)',
    4: 'Catalunya',
    5: 'Monaco',
    6: 'Montreal',
    7: 'Silverstone',
    8: 'Hockenheim',
    9: 'Hungaroring',
    10: 'Spa',
    11: 'Monza',
    12: 'Singapore',
    13: 'Suzuka',
    14: 'Abu Dhabi',
    15: 'Texas',
    16: 'Brazil',
    17: 'Austria',
    18: 'Sochi',
    19: 'Mexico',
    20: 'Baku (Azerbaijan)',
    21: 'Sakhir Short',
    22: 'Silverstone Short',
    23: 'Texas Short',
    24: 'Suzuka Short',
    25: 'Hanoi',
    26: 'Zandvoort',
    27: 'Imola',
    28: 'Portimão',
    29: 'Jeddah',
    30: 'Miami',
    31: 'Las Vegas',
    32: 'Losail',
}


def _track_id_to_str(track_id: int) -> str:
    return TRACK_ID_DEFINITION[track_id]


FORMULA_DEFINITION = {
    0: 'F1 modern',
    1: 'F1 classic',
    2: 'F2',
    3: 'F1 generic',
    4: 'beta',
    5: 'supercars',
    6: 'esports',
    7: 'F2 2021',
}


def _formula_to_str(formula: int) -> str:
    return FORMULA_DEFINITION[formula]
