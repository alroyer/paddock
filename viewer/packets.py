from dataclasses import dataclass


@dataclass
class PacketHeader:
    packet_format: int
    game_year: int
    game_major_version: int
    game_minor_version: int
    packet_version: int
    packet_id: int
    session_uid: int
    session_time: float
    frame_identifier: int
    overall_frame_identifier: int
    player_car_index: int
    secondary_player_car_index: int


@dataclass
class CarMotionData:
    world_position_x: float
    world_position_y: float
    world_position_z: float
    world_velocity_x: float
    world_velocity_y: float
    world_velocity_z: float
    world_forward_dir_x: int
    world_forward_dir_y: int
    world_forward_dir_z: int
    world_right_dir_x: int
    world_right_dir_y: int
    world_right_dir_z: int
    gforce_lateral: float
    gforce_longitudinal: float
    gforce_vertical: float
    yaw: float
    pitch: float
    roll: float


@dataclass
class PacketMotionData:
    header: PacketHeader
    car_motion_data: list[CarMotionData]


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


@dataclass
class LapData:
    last_lap_time_ms: int
    current_lap_time_ms: int
    sector1_time_ms: int
    sector1_time_minutes: int
    sector2_time_ms: int
    sector2_time_minutes: int
    delta_to_car_in_front_ms: int
    delta_to_race_leader_ms: int
    lap_distance: float
    total_distance: float
    safety_car_delta: float
    car_position: int
    current_lap_num: int
    pit_status: int
    num_pit_stops: int
    sector: int
    current_lap_invalid: int
    penalties: int
    total_warnings: int
    corner_cutting_warnings: int
    num_unserved_drive_through_pens: int
    num_unserved_stop_go_pens: int
    grid_position: int
    driver_status: int
    result_status: int
    pit_lane_timer_active: int
    pit_lane_time_in_lane_ms: int
    pit_stop_timer_ms: int
    pit_stop_should_serve_pen: int


@dataclass
class PacketLapData:
    header: PacketHeader
    lap_data: list[LapData]
    time_trial_pb_car_index: int
    time_trial_rival_car_index: int


# TODO: EventDataDetails


@dataclass
class ParticipantData:
    ai_controlled: int
    driver_id: int
    network_id: int
    team_id: int
    my_team: int
    race_number: int
    nationality: int
    name: str
    your_telemetry: int
    show_online_names: int
    platform: int


@dataclass
class PacketParticipantsData:
    header: PacketHeader
    num_active_cars: int
    participants: list[ParticipantData]


@dataclass
class CarSetupData:
    front_wing: int
    rear_wing: int
    on_throttle: int
    off_throttle: int
    front_camber: float
    rear_camber: float
    front_toe: float
    rear_toe: float
    front_suspension: int
    rear_suspension: int
    front_anti_roll_bar: int
    rear_anti_roll_bar: int
    front_suspension_height: int
    rear_suspension_height: int
    brake_pressure: int
    brake_bias: int
    rear_left_tire_pressure: float
    rear_right_tire_pressure: float
    front_left_tire_pressure: float
    front_right_tire_pressure: float
    ballast: int
    fuel_load: float


@dataclass
class PacketCarSetupData:
    header: PacketHeader
    car_setups: list[CarSetupData]


@dataclass
class CarTelemetryData:
    speed: int
    throttle: float
    steer: float
    brake: float
    clutch: int
    gear: int
    engine_rpm: int
    drs: int
    rev_lights_percent: int
    rev_lights_bit_value: int
    brakes_temperature: list[int]
    tires_surface_temperature: list[int]
    tires_inner_temperature: list[int]
    engine_temperature: int
    tyres_pressure: list[float]
    surface_type: int


@dataclass
class PacketCarTelemetryData:
    header: PacketHeader
    car_telemetry_data: list[CarTelemetryData]
    mfd_panel_index: int
    mdf_panel_index_secondary_player: int
    suggested_gear: int


@dataclass
class CarStatusData:
    traction_control: int
    anti_lock_brakes: int
    fuel_mix: int
    front_brake_bias: int
    pit_limiter_status: int
    fuel_in_tank: float
    fuel_capacity: float
    fuel_remaining_laps: float
    max_rpm: int
    idle_rpm: int
    max_gears: int
    drs_allowed: int
    drs_activation_distance: float
    actual_tire_compound: int
    visual_tire_compound: int
    tire_age_laps: int
    vehicle_fia_flags: int
    engine_power_ice: float
    engine_power_mgu_k: float
    ers_store_energy: float
    ers_deploy_mode: int
    ers_harvested_this_lap_mgu_k: float
    ers_harvested_this_lap_mgu_h: float
    ers_deployed_this_lap: float
    network_paused: int


@dataclass
class PacketCarStatusData:
    header: PacketHeader
    car_status_data: list[CarStatusData]


@dataclass
class FinalClassificationData:
    position: int
    num_laps: int
    grid_position: int
    points: int
    num_pit_stops: int
    result_status: int
    best_lap_time_in_ms: int
    total_race_time: float
    penalties_time: int
    num_penalties: int
    num_tyre_stints: int
    type_stints_actual: list[int]
    type_stints_visual: list[int]
    tyre_stints_end_lap: list[int]


@dataclass
class PacketFinalClassificationData:
    header: PacketHeader
    num_cars: int
    classification_data: list[FinalClassificationData]


@dataclass
class LobbyInfoData:
    ai_controlled: int
    team_id: int
    natiobality: int
    platform: int
    name: str
    car_number: int
    ready_status: int


@dataclass
class PacketLobbyInfoData:
    header: PacketHeader
    num_players: int
    lobby_info_data: list[LobbyInfoData]


@dataclass
class CarDamageData:
    tyres_wear: list[float]
    tyres_damage: list[int]
    brakes_damage: list[int]
    front_left_wing_damage: int
    front_right_wing_damage: int
    rear_wing_damage: int
    floor_damage: int
    diffuser_damage: int
    sidepod_damage: int
    drs_fault: int
    ers_fault: int
    gear_box_damage: int
    engine_damage: int
    engine_mgu_h_wear: int
    engine_es_wear: int
    engine_ce_wear: int
    engine_ice_wear: int
    engine_mgu_k_wear: int
    engine_tc_wear: int
    engine_blown: int
    engine_seized: int


@dataclass
class PacketCarDamageData:
    header: PacketHeader
    car_damage_data: list[CarDamageData]


@dataclass
class LapHistoryData:
    lap_time_in_ms: int
    sector1_time_in_ms: int
    sector1_time_in_minutes: int
    sector2_time_in_ms: int
    sector2_time_in_minutes: int
    sector3_time_in_ms: int
    sector3_time_in_minutes: int
    lap_validity_bit_flags: int


@dataclass
class TyreStintHistoryData:
    end_lap: int
    tyre_actual_compound: int
    tyre_visual_compound: int


@dataclass
class PacketLapHistoryData:
    header: PacketHeader
    car_index: int
    num_laps: int
    num_tyre_stints: int
    best_lap_time_num: int
    best_sector1_lap_num: int
    best_sector2_lap_num: int
    best_sector3_lap_num: int
    lap_history_data: list[LapHistoryData]
    tyre_stint_history_data: list[TyreStintHistoryData]


@dataclass
class TyreSetData:
    actual_tyre_compound: int
    visual_tyre_compound: int
    wear: int
    available: int
    recommended_session: int
    life_span: int
    usable_life: int
    lap_delta_time: int
    fitted: int


@dataclass
class PacketTyreSetsData:
    header: PacketHeader
    car_index: int
    tyre_set_data: list[TyreSetData]
    fitted_index: int


@dataclass
class PacketMotionExData:
    header: PacketHeader
    suspension_position: list[float]
    suspension_velocity: list[float]
    suspension_acceleration: list[float]
    wheel_speed: list[float]
    wheel_slip_ratio: list[float]
    wheel_slip_angle: list[float]
    wheel_lat_force: list[float]
    wheel_long_force: list[float]
    height_of_cog_above_ground: float
    local_velocity_x: float
    local_velocity_y: float
    local_velocity_z: float
    angular_velocity_x: float
    angular_velocity_y: float
    angular_velocity_z: float
    angular_acceleration_x: float
    angular_acceleration_y: float
    angular_acceleration_z: float
    front_wheels_angle: float
    wheel_vert_force: list[float]
