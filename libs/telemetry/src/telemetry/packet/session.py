import struct
from dataclasses import dataclass
from typing import ClassVar

from .base import BasePacket
from .constants import BYTES_ORDER
from .header import PacketHeader


@dataclass(frozen=True)
class MarshalZone:
    zone_start: float
    zone_flag: int

    STRUCT_FMT: ClassVar[str] = "<fb" if BYTES_ORDER == "little" else ">fb"
    SIZE: ClassVar[int] = struct.calcsize(STRUCT_FMT)

    @classmethod
    def from_bytes(cls, data: bytes) -> "MarshalZone":
        if len(data) < cls.SIZE:
            raise ValueError(
                f"buffer too small: need {cls.SIZE} bytes, got {len(data)}"
            )
        zone_start, zone_flag = struct.unpack(cls.STRUCT_FMT, data[: cls.SIZE])
        return cls(zone_start=zone_start, zone_flag=zone_flag)

    def to_bytes(self) -> bytes:
        return struct.pack(self.STRUCT_FMT, self.zone_start, self.zone_flag)


@dataclass(frozen=True)
class WeatherForecastSample:
    session_type: int
    time_offset: int
    weather: int
    track_temperature: int
    track_temperature_change: int
    air_temperature: int
    air_temperature_change: int
    rain_percentage: int

    STRUCT_FMT: ClassVar[str] = "<3B4bB" if BYTES_ORDER == "little" else ">3B4bB"
    SIZE: ClassVar[int] = struct.calcsize(STRUCT_FMT)

    @classmethod
    def from_bytes(cls, data: bytes) -> "WeatherForecastSample":
        if len(data) < cls.SIZE:
            raise ValueError(
                f"buffer too small: need {cls.SIZE} bytes, got {len(data)}"
            )
        (
            session_type,
            time_offset,
            weather,
            track_temperature,
            track_temperature_change,
            air_temperature,
            air_temperature_change,
            rain_percentage,
        ) = struct.unpack(cls.STRUCT_FMT, data[: cls.SIZE])
        return cls(
            session_type=session_type,
            time_offset=time_offset,
            weather=weather,
            track_temperature=track_temperature,
            track_temperature_change=track_temperature_change,
            air_temperature=air_temperature,
            air_temperature_change=air_temperature_change,
            rain_percentage=rain_percentage,
        )

    def to_bytes(self) -> bytes:
        return struct.pack(
            self.STRUCT_FMT,
            self.session_type,
            self.time_offset,
            self.weather,
            self.track_temperature,
            self.track_temperature_change,
            self.air_temperature,
            self.air_temperature_change,
            self.rain_percentage,
        )


@dataclass(frozen=True)
class PacketSessionData(BasePacket):
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
    num_marshal_zones: int
    marshal_zones: list[MarshalZone]
    safety_car_status: int
    network_game: int
    num_weather_forecast_samples: int
    weather_forecast_samples: list[WeatherForecastSample]
    forecast_accuracy: int
    ai_difficulty: int
    season_link_identifier: int
    weekend_link_identifier: int
    session_link_identifier: int
    pit_stop_window_ideal_lap: int
    pit_stop_window_latest_lap: int
    pit_stop_rejoin_position: int
    steering_assist: int
    braking_assist: int
    gearbox_assist: int
    pit_assist: int
    pit_release_assist: int
    ers_assist: int
    drs_assist: int
    dynamic_racing_line: int
    dynamic_racing_line_type: int
    game_mode: int
    rule_set: int
    time_of_day: int
    session_length: int
    speed_units_lead_player: int
    temperature_units_lead_player: int
    speed_units_secondary_player: int
    temperature_units_secondary_player: int
    num_safety_car_periods: int
    num_virtual_safety_car_periods: int
    num_red_flag_periods: int
    equal_car_performance: int
    recovery_mode: int
    flashback_limit: int
    surface_type: int
    low_fuel_mode: int
    race_starts: int
    tyre_temperature: int
    pit_lane_tyre_sim: int
    car_damage: int
    car_damage_rate: int
    collisions: int
    collisions_off_for_first_lap_only: int
    mp_unsafe_pit_release: int
    mp_off_for_griefing: int
    corner_cutting_stringency: int
    parc_ferme_rules: int
    pit_stop_experience: int
    safety_car: int
    safety_car_experience: int
    formation_lap: int
    formation_lap_experience: int
    red_flags: int
    affects_licence_level_solo: int
    affects_licence_level_mp: int
    num_sessions_in_weekend: int
    weekend_structure: list[int]
    sector2_lap_distance_start: float
    sector3_lap_distance_start: float

    PRE_FMT: ClassVar[str] = (
        "<BbbBHbBHHBBBBBBB" if BYTES_ORDER == "little" else ">BbbBHbBHHBBBBBBB"
    )
    PRE_SIZE: ClassVar[int] = struct.calcsize(PRE_FMT)

    MID_FMT: ClassVar[str] = "<BBB" if BYTES_ORDER == "little" else ">BBB"
    MID_SIZE: ClassVar[int] = struct.calcsize(MID_FMT)

    TAIL_FMT: ClassVar[str] = (
        "<BBIII14BI33B12Bff" if BYTES_ORDER == "little" else ">BBIII14BI33B12Bff"
    )
    TAIL_SIZE: ClassVar[int] = struct.calcsize(TAIL_FMT)

    SIZE: ClassVar[int] = (
        PacketHeader.SIZE
        + PRE_SIZE
        + 21 * MarshalZone.SIZE
        + MID_SIZE
        + 64 * WeatherForecastSample.SIZE
        + TAIL_SIZE
    )

    @classmethod
    def parse(
        cls, header: PacketHeader, data: bytes
    ) -> tuple["PacketSessionData", bytes]:
        data = cls._require_bytes(
            data,
            cls.PRE_SIZE
            + 21 * MarshalZone.SIZE
            + cls.MID_SIZE
            + 64 * WeatherForecastSample.SIZE
            + cls.TAIL_SIZE,
        )

        offset = 0

        (
            weather,
            track_temperature,
            air_temperature,
            total_laps,
            track_length,
            session_type,
            track_id,
            formula,
            session_time_left,
            session_duration,
            pit_speed_limit,
            game_paused,
            is_spectating,
            spectator_car_index,
            sli_pro_native_support,
            num_marshal_zones,
        ) = struct.unpack(cls.PRE_FMT, data[offset : offset + cls.PRE_SIZE])
        offset += cls.PRE_SIZE

        marshal_zones = []
        for _ in range(21):
            zone = MarshalZone.from_bytes(data[offset : offset + MarshalZone.SIZE])
            marshal_zones.append(zone)
            offset += MarshalZone.SIZE

        (
            safety_car_status,
            network_game,
            num_weather_forecast_samples,
        ) = struct.unpack(cls.MID_FMT, data[offset : offset + cls.MID_SIZE])
        offset += cls.MID_SIZE

        weather_forecast_samples = []
        for _ in range(64):
            sample = WeatherForecastSample.from_bytes(
                data[offset : offset + WeatherForecastSample.SIZE]
            )
            weather_forecast_samples.append(sample)
            offset += WeatherForecastSample.SIZE

        (
            forecast_accuracy,
            ai_difficulty,
            season_link_identifier,
            weekend_link_identifier,
            session_link_identifier,
            pit_stop_window_ideal_lap,
            pit_stop_window_latest_lap,
            pit_stop_rejoin_position,
            steering_assist,
            braking_assist,
            gearbox_assist,
            pit_assist,
            pit_release_assist,
            ers_assist,
            drs_assist,
            dynamic_racing_line,
            dynamic_racing_line_type,
            game_mode,
            rule_set,
            time_of_day,
            session_length,
            speed_units_lead_player,
            temperature_units_lead_player,
            speed_units_secondary_player,
            temperature_units_secondary_player,
            num_safety_car_periods,
            num_virtual_safety_car_periods,
            num_red_flag_periods,
            equal_car_performance,
            recovery_mode,
            flashback_limit,
            surface_type,
            low_fuel_mode,
            race_starts,
            tyre_temperature,
            pit_lane_tyre_sim,
            car_damage,
            car_damage_rate,
            collisions,
            collisions_off_for_first_lap_only,
            mp_unsafe_pit_release,
            mp_off_for_griefing,
            corner_cutting_stringency,
            parc_ferme_rules,
            pit_stop_experience,
            safety_car,
            safety_car_experience,
            formation_lap,
            formation_lap_experience,
            red_flags,
            affects_licence_level_solo,
            affects_licence_level_mp,
            num_sessions_in_weekend,
            *weekend_structure,
            sector2_lap_distance_start,
            sector3_lap_distance_start,
        ) = struct.unpack(cls.TAIL_FMT, data[offset : offset + cls.TAIL_SIZE])

        return cls(
            header=header,
            weather=weather,
            track_temperature=track_temperature,
            air_temperature=air_temperature,
            total_laps=total_laps,
            track_length=track_length,
            session_type=session_type,
            track_id=track_id,
            formula=formula,
            session_time_left=session_time_left,
            session_duration=session_duration,
            pit_speed_limit=pit_speed_limit,
            game_paused=game_paused,
            is_spectating=is_spectating,
            spectator_car_index=spectator_car_index,
            sli_pro_native_support=sli_pro_native_support,
            num_marshal_zones=num_marshal_zones,
            marshal_zones=marshal_zones,
            safety_car_status=safety_car_status,
            network_game=network_game,
            num_weather_forecast_samples=num_weather_forecast_samples,
            weather_forecast_samples=weather_forecast_samples,
            forecast_accuracy=forecast_accuracy,
            ai_difficulty=ai_difficulty,
            season_link_identifier=season_link_identifier,
            weekend_link_identifier=weekend_link_identifier,
            session_link_identifier=session_link_identifier,
            pit_stop_window_ideal_lap=pit_stop_window_ideal_lap,
            pit_stop_window_latest_lap=pit_stop_window_latest_lap,
            pit_stop_rejoin_position=pit_stop_rejoin_position,
            steering_assist=steering_assist,
            braking_assist=braking_assist,
            gearbox_assist=gearbox_assist,
            pit_assist=pit_assist,
            pit_release_assist=pit_release_assist,
            ers_assist=ers_assist,
            drs_assist=drs_assist,
            dynamic_racing_line=dynamic_racing_line,
            dynamic_racing_line_type=dynamic_racing_line_type,
            game_mode=game_mode,
            rule_set=rule_set,
            time_of_day=time_of_day,
            session_length=session_length,
            speed_units_lead_player=speed_units_lead_player,
            temperature_units_lead_player=temperature_units_lead_player,
            speed_units_secondary_player=speed_units_secondary_player,
            temperature_units_secondary_player=temperature_units_secondary_player,
            num_safety_car_periods=num_safety_car_periods,
            num_virtual_safety_car_periods=num_virtual_safety_car_periods,
            num_red_flag_periods=num_red_flag_periods,
            equal_car_performance=equal_car_performance,
            recovery_mode=recovery_mode,
            flashback_limit=flashback_limit,
            surface_type=surface_type,
            low_fuel_mode=low_fuel_mode,
            race_starts=race_starts,
            tyre_temperature=tyre_temperature,
            pit_lane_tyre_sim=pit_lane_tyre_sim,
            car_damage=car_damage,
            car_damage_rate=car_damage_rate,
            collisions=collisions,
            collisions_off_for_first_lap_only=collisions_off_for_first_lap_only,
            mp_unsafe_pit_release=mp_unsafe_pit_release,
            mp_off_for_griefing=mp_off_for_griefing,
            corner_cutting_stringency=corner_cutting_stringency,
            parc_ferme_rules=parc_ferme_rules,
            pit_stop_experience=pit_stop_experience,
            safety_car=safety_car,
            safety_car_experience=safety_car_experience,
            formation_lap=formation_lap,
            formation_lap_experience=formation_lap_experience,
            red_flags=red_flags,
            affects_licence_level_solo=affects_licence_level_solo,
            affects_licence_level_mp=affects_licence_level_mp,
            num_sessions_in_weekend=num_sessions_in_weekend,
            weekend_structure=list(weekend_structure),
            sector2_lap_distance_start=sector2_lap_distance_start,
            sector3_lap_distance_start=sector3_lap_distance_start,
        ), data[
            cls.PRE_SIZE
            + 21 * MarshalZone.SIZE
            + cls.MID_SIZE
            + 64 * WeatherForecastSample.SIZE
            + cls.TAIL_SIZE :
        ]

    def to_bytes(self) -> bytes:
        if len(self.marshal_zones) != 21:
            raise ValueError("marshal_zones must contain exactly 21 items")
        if len(self.weather_forecast_samples) != 64:
            raise ValueError("weather_forecast_samples must contain exactly 64 items")
        if len(self.weekend_structure) != 12:
            raise ValueError("weekend_structure must contain exactly 12 items")

        result = self.header.to_bytes()
        result += struct.pack(
            self.PRE_FMT,
            self.weather,
            self.track_temperature,
            self.air_temperature,
            self.total_laps,
            self.track_length,
            self.session_type,
            self.track_id,
            self.formula,
            self.session_time_left,
            self.session_duration,
            self.pit_speed_limit,
            self.game_paused,
            self.is_spectating,
            self.spectator_car_index,
            self.sli_pro_native_support,
            self.num_marshal_zones,
        )

        for zone in self.marshal_zones:
            result += zone.to_bytes()

        result += struct.pack(
            self.MID_FMT,
            self.safety_car_status,
            self.network_game,
            self.num_weather_forecast_samples,
        )

        for sample in self.weather_forecast_samples:
            result += sample.to_bytes()

        result += struct.pack(
            self.TAIL_FMT,
            self.forecast_accuracy,
            self.ai_difficulty,
            self.season_link_identifier,
            self.weekend_link_identifier,
            self.session_link_identifier,
            self.pit_stop_window_ideal_lap,
            self.pit_stop_window_latest_lap,
            self.pit_stop_rejoin_position,
            self.steering_assist,
            self.braking_assist,
            self.gearbox_assist,
            self.pit_assist,
            self.pit_release_assist,
            self.ers_assist,
            self.drs_assist,
            self.dynamic_racing_line,
            self.dynamic_racing_line_type,
            self.game_mode,
            self.rule_set,
            self.time_of_day,
            self.session_length,
            self.speed_units_lead_player,
            self.temperature_units_lead_player,
            self.speed_units_secondary_player,
            self.temperature_units_secondary_player,
            self.num_safety_car_periods,
            self.num_virtual_safety_car_periods,
            self.num_red_flag_periods,
            self.equal_car_performance,
            self.recovery_mode,
            self.flashback_limit,
            self.surface_type,
            self.low_fuel_mode,
            self.race_starts,
            self.tyre_temperature,
            self.pit_lane_tyre_sim,
            self.car_damage,
            self.car_damage_rate,
            self.collisions,
            self.collisions_off_for_first_lap_only,
            self.mp_unsafe_pit_release,
            self.mp_off_for_griefing,
            self.corner_cutting_stringency,
            self.parc_ferme_rules,
            self.pit_stop_experience,
            self.safety_car,
            self.safety_car_experience,
            self.formation_lap,
            self.formation_lap_experience,
            self.red_flags,
            self.affects_licence_level_solo,
            self.affects_licence_level_mp,
            self.num_sessions_in_weekend,
            *self.weekend_structure,
            self.sector2_lap_distance_start,
            self.sector3_lap_distance_start,
        )

        return result
