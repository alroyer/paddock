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
    # track_length: int
    # session_type: int
    # track_id: int
    # formula: int
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
        return '<BbbB'

    def __str__(self) -> str:
        return f'''[PacketSessionData]
    {self.header}
    weather:           {_weather_to_str(self.weather)}
    track temperature: {self.track_temperature}°
    air temperature:   {self.air_temperature}°'''


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
