from dataclasses import dataclass

from .constants import (
    FORMULA_DEFINITION,
    SESSION_TYPE_DEFINITION,
    TRACK_ID_DEFINITION,
    WEATHER_DEFINITION,
    ZONE_FLAG_DEFINITION,
)
from .header import PacketHeader


@dataclass
class MarshalZone:
    zone_start: float
    zone_flag: int

    @classmethod
    def unpack_format(cls) -> str:
        return '<fb'

    @classmethod
    def bytes_count(cls) -> int:
        return 5

    def __str__(self) -> str:
        return f'''[MarshalZone]
    zone start:             {self.zone_start}
    zone flag:              {ZONE_FLAG_DEFINITION[self.zone_flag]}'''


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

    @classmethod
    def unpack_format(cls) -> str:
        return '<BBBbbbbB'

    @classmethod
    def bytes_count(cls) -> int:
        return 8


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
    session_time_left: int
    session_duration: int
    pit_speed_limit: int
    game_paused: int
    is_spectating: int
    spectator_car_index: int
    sli_pro_native_support: int
    num_marshall_zones: int
    # safety_car_status: int
    # network_game: int
    # num_weather_forecast_samples: int
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
    marshal_zones: list[MarshalZone]
    weather_forecast_samples: list[WeatherForecastSample]

    @classmethod
    def bytes_count(cls) -> int:
        return 644 - PacketHeader.bytes_count()

    @classmethod
    def marshal_zone_bytes_offset(cls) -> int:
        return 19

    @classmethod
    def weather_forecast_samples_bytes_offset(cls) -> int:
        # TODO
        pass

    @classmethod
    def unpack_format(cls) -> str:
        return '<BbbBHBbBHHBBBBBB'

    def __str__(self) -> str:
        return f'''[PacketSessionData]
    {self.header}
    weather:                {WEATHER_DEFINITION[self.weather]}
    track temperature:      {self.track_temperature} °C
    air temperature:        {self.air_temperature} °C
    track length:           {self.track_length} m
    session type:           {SESSION_TYPE_DEFINITION[self.session_type]}
    track:                  {TRACK_ID_DEFINITION[self.track_id]}
    formula:                {FORMULA_DEFINITION[self.formula]}
    session time left:      {self.session_time_left} sec
    session duration:       {self.session_duration} sec
    pit speed limit:        {self.pit_speed_limit} km/h
    game paused:            {self.game_paused}
    is spectating:          {self.is_spectating}
    spectator car index:    {self.spectator_car_index}
    sli pro native support: {self.sli_pro_native_support}
    num marshall zones:     {self.num_marshall_zones}
    '''
