from dataclasses import dataclass
from types import MappingProxyType


@dataclass(frozen=True)
class PacketHeader:
    packet_format: int  # 2026
    game_year: int  # Game year - last two digits e.g. 26
    game_major_version: int  # Game major version - "X.00"
    game_minor_version: int  # Game minor version - "1.XX"
    packet_version: int  # Version of this packet type
    packet_id: int  # Identifier for the packet type
    session_uid: int  # Unique identifier for the session
    session_time: float  # Session timestamp
    frame_identifier: int  # Identifier for the frame the data was retrieved on
    overall_frame_identifier: (
        int  # Overall identifier for the frame the data was retrieved on, doesn't go back after flashbacks
    )
    player_car_index: int  # Index of player's car in the array
    secondary_player_car_index: (
        int  # Index of secondary player's car in the array (splitscreen) - 255 if no second player
    )


@dataclass(frozen=True)
class CarMotionData:
    world_position_x: float  # World space X position - metres
    world_position_y: float  # World space Y position
    world_position_z: float  # World space Z position
    world_velocity_x: float  # Velocity in world space X - metres/s
    world_velocity_y: float  # Velocity in world space Y
    world_velocity_z: float  # Velocity in world space Z
    world_forward_dir_x: int  # World space forward X direction (normalised)
    world_forward_dir_y: int  # World space forward Y direction (normalised)
    world_forward_dir_z: int  # World space forward Z direction (normalised)
    world_right_dir_x: int  # World space right X direction (normalised)
    world_right_dir_y: int  # World space right Y direction (normalised)
    world_right_dir_z: int  # World space right Z direction (normalised)
    g_force_lateral: int  # Lateral G-Force component (quantised)
    g_force_longitudinal: int  # Longitudinal G-Force component (quantised)
    g_force_vertical: int  # Vertical G-Force component (quantised)
    yaw: float  # Yaw angle in radians
    pitch: float  # Pitch angle in radians
    roll: float  # Roll angle in radians


@dataclass(frozen=True)
class PacketMotionData:
    header: PacketHeader
    car_motion_data: list[CarMotionData]


@dataclass(frozen=True)
class MarshalZone:
    zone_start: float  # Fraction (0..1) of way through the lap the marshal zone starts
    zone_flag: int  # -1 = invalid/unknown, 0 = none, 1 = green, 2 = blue, 3 = yellow


@dataclass(frozen=True)
class ActiveAeroZone:
    zone_start: float  # Fraction (0..1) of way through the lap the Active Aero zone starts
    zone_end: float  # Fraction (0..1) of way through the lap the Active Aero zone ends


@dataclass(frozen=True)
class DRSZone:
    zone_start: float  # Fraction (0..1) of way through the lap the DRS zone starts
    zone_end: float  # Fraction (0..1) of way through the lap the DRS zone ends


@dataclass(frozen=True)
class WeatherForecastSample:
    session_type: int  # 0 = unknown, see appendix
    time_offset: int  # Time in minutes the forecast is for
    weather: int  # Weather - 0 = clear, 1 = light cloud, 2 = overcast, 3 = light rain, 4 = heavy rain, 5 = storm
    track_temperature: int  # Track temp. in degrees celsius
    track_temperature_change: int  # Track temp. change - 0 = up, 1 = down, 2 = no change
    air_temperature: int  # Air temp. in degrees celsius
    air_temperature_change: int  # Air temp. change - 0 = up, 1 = down, 2 = no change
    rain_percentage: int  # Rain percentage (0-100)


@dataclass(frozen=True)
class PacketSessionData:
    header: PacketHeader
    weather: int  # Weather - 0 = clear, 1 = light cloud, 2 = overcast, 3 = light rain, 4 = heavy rain, 5 = storm
    track_temperature: int  # Track temp. in degrees celsius
    air_temperature: int  # Air temp. in degrees celsius
    total_laps: int  # Total number of laps in this race
    track_length: int  # Track length in metres
    session_type: int  # 0 = unknown, see appendix
    track_id: int  # -1 for unknown, see appendix
    formula: int  # Formula, 0 = F1 Modern, 1 = F1 Classic, 2 = F2, 3 = F1 Generic, 4 = Beta, 6 = Esports, 8 = F1 World, 9 = F1 Elimination, 13 = F1 26
    session_time_left: int  # Time left in session in seconds
    session_duration: int  # Session duration in seconds
    pit_speed_limit: int  # Pit speed limit in kilometres per hour
    game_paused: int  # Whether the game is paused - network game only
    is_spectating: int  # Whether the player is spectating
    spectator_car_index: int  # Index of the car being spectated
    sli_pro_native_support: int  # SLI Pro support, 0 = inactive, 1 = active
    num_marshal_zones: int
    marshal_zones: list[MarshalZone]  # List of marshal zones - max 21
    safety_car_status: int  # 0 = no safety car, 1 = full, 2 = virtual, 3 = formation lap
    network_game: int  # 0 = offline, 1 = online
    num_weather_forecast_samples: int
    weather_forecast_samples: list[WeatherForecastSample]
    forecast_accuracy: int  # 0 = Perfect, 1 = Approximate
    ai_difficulty: int  # AI difficulty - 0-110
    season_link_identifier: int  # Identifier for season - persists across saves
    weekend_link_identifier: int  # Identifier for weekend - persists across saves
    session_link_identifier: int  # Identifier for session - persists across saves
    pit_stop_window_ideal_lap: int  # Ideal lap to pit on for current strategy (player)
    pit_stop_window_latest_lap: int  # Latest lap to pit on for current strategy (player)
    pit_stop_rejoin_position: int  # Predicted position to rejoin at (player)
    steering_assist: int  # 0 = off, 1 = on
    braking_assist: int  # 0 = off, 1 = low, 2 = medium, 3 = high
    gearbox_assist: int  # 1 = manual, 2 = manual & suggested gear, 3 = auto
    pit_assist: int  # 0 = off, 1 = on
    pit_release_assist: int  # 0 = off, 1 = on
    ers_assist: int  # 0 = off, 1 = on
    drs_assist: int  # 0 = off, 1 = on
    dynamic_racing_line: int  # 0 = off, 1 = corners only, 2 = full
    dynamic_racing_line_type: int  # 0 = 2D, 1 = 3D
    game_mode: int  # Game mode id - see appendix
    rule_set: int  # Ruleset - see appendix
    time_of_day: int  # Local time of day - minutes since midnight
    session_length: int  # 0 = None, 2 = Very Short, 3 = Short, 4 = Medium, 5 = Medium Long, 6 = Long, 7 = Full
    speed_units_lead_player: int  # 0 = MPH, 1 = KPH
    temperature_units_lead_player: int  # 0 = Celsius, 1 = Fahrenheit
    speed_units_secondary_player: int  # 0 = MPH, 1 = KPH
    temperature_units_secondary_player: int  # 0 = Celsius, 1 = Fahrenheit
    num_safety_car_periods: int
    num_virtual_safety_car_periods: int
    num_red_flag_periods: int
    equal_car_performance: int  # 0 = Off, 1 = On
    recovery_mode: int  # 0 = None, 1 = Flashbacks, 2 = Auto-recovery
    flashback_limit: int  # 0 = Low, 1 = Medium, 2 = High, 3 = Unlimited
    surface_type: int  # 0 = Simplified, 1 = Realistic
    low_fuel_mode: int  # 0 = Easy, 1 = Hard
    race_starts: int  # 0 = Manual, 1 = Assisted
    tyre_temperature: int  # 0 = Surface only, 1 = Surface & Carcass
    pit_lane_tyre_sim: int  # 0 = On, 1 = Off
    car_damage: int  # 0 = Off, 1 = Reduced, 2 = Standard, 3 = Simulation
    car_damage_rate: int  # 0 = Reduced, 1 = Standard, 2 = Simulation
    collisions: int  # 0 = Off, 1 = Player-to-Player Off, 2 = On
    collisions_off_for_first_lap_only: int  # 0 = Disabled, 1 = Enabled
    mp_unsafe_pit_release: int  # 0 = On, 1 = Off (Multiplayer)
    mp_off_for_griefing: int  # 0 = Disabled, 1 = Enabled (Multiplayer)
    corner_cutting_stringency: int  # 0 = Regular, 1 = Strict
    parc_ferme_rules: int  # 0 = Off, 1 = On
    pit_stop_experience: int  # 0 = Automatic, 1 = Broadcast, 2 = Immersive
    safety_car: int  # 0 = Off, 1 = 2026 regulations applicable, 2 = 2026 regulations applicable
    safety_car_experience: int  # 0 = Off, 1 = On
    formation_lap: int  # 0 = Off, 1 = On
    formation_lap_experience: int  # 0 = Off, 1 = On
    red_flags: int  # 0 = Off, 1 = On
    affects_licence_level_solo: int  # 0 = Off, 1 = On
    affects_licence_level_mp: int  # 0 = Off, 1 = On
    num_sessions_in_weekend: int
    weekend_structure: list[int]  # Array of session types (see appendix)
    sector_2_lap_distance_start: float  # Distance from start of lap to sector 2 start
    sector_3_lap_distance_start: float  # Distance from start of lap to sector 3 start
    active_aero_track_status: int  # 0 = Off, 1 = On
    num_active_aero_zones_full: int
    active_aero_zones_full: list[ActiveAeroZone]  # Array of active aero zones in full mode
    num_active_aero_zones_partial: int
    active_aero_zones_partial: list[ActiveAeroZone]  # Array of active aero zones in partial mode
    num_drs_zones: int
    drs_zones: list[DRSZone]  # Array of DRS zones
    start_reaction_time: float  # Time for start light reaction (seconds)
    anti_lock_brakes_assist: int  # 0 = off, 1 = on
    traction_control_assist: int  # 0 = off, 1 = on
    dynamic_racing_line_hi_vis: int  # 0 = off, 1 = on
    dynamic_racing_line_colour_blind: int  # 0 = off, 1 = on
    recurring_rewind_prompt: int  # 0 = off, 1 = on


@dataclass(frozen=True)
class LapData:
    last_lap_time_in_ms: int  # Last lap time in milliseconds
    current_lap_time_in_ms: int  # Current lap time in milliseconds
    sector1_time_ms_part: int  # Sector 1 milliseconds part
    sector1_time_minutes_part: int  # Sector 1 whole minute part
    sector2_time_ms_part: int  # Sector 2 time milliseconds part
    sector2_time_minutes_part: int  # Sector 2 whole minute part
    delta_to_car_in_front_ms_part: int  # Delta to car in front milliseconds part
    delta_to_car_in_front_minutes_part: int  # Delta to car in front whole minute part
    delta_to_race_leader_ms_part: int  # Delta to race leader milliseconds part
    delta_to_race_leader_minutes_part: int  # Delta to race leader whole minute part
    lap_distance: float  # Distance around track (meters)
    total_distance: float  # Distance around track (meters)
    safety_car_delta: float  # Safety car delta time (seconds)
    car_position: int  # Car position on track
    current_lap_num: int  # Current lap number
    pit_status: int  # 0 = none, 1 = pitting, 2 = in pit area
    num_pit_stops: int
    sector: int  # 0 = sector 1, 1 = sector 2, 2 = sector 3
    current_lap_invalid: int  # 0 = lap valid, 1 = lap invalid
    penalties: int  # Number of penalties applied to this driver
    total_warnings: int
    corner_cutting_warnings: int
    num_unserved_drive_through_pens: int
    num_unserved_stop_go_pens: int
    grid_position: int  # Grid position of the car
    driver_status: int  # Status of driver - 0 = invalid, 1 = inactive, 2 = active, 3 = finished, 4 = didnotfinish, 5 = disqualified, 6 = not classified, 7 = retired
    result_status: int  # Result status - 0 = invalid, 1 = inactive, 2 = active, 3 = finished, 4 = didnotfinish, 5 = disqualified, 6 = not classified, 7 = retired
    pit_lane_timer_active: int  # 0 = not active, 1 = active
    pit_lane_time_in_lane_in_ms: int  # Time in pit lane (milliseconds)
    pit_stop_timer_in_ms: int  # Time since pit stop began (milliseconds)
    pit_stop_should_serve_pen: int  # 0 = no penalty, 1 = penalty served
    speed_trap_fastest_speed: float  # Fastest speed in the speed trap (km/h)
    speed_trap_fastest_lap: int  # Lap number of fastest speed trap (255 = none)


@dataclass(frozen=True)
class PacketLapData:
    header: PacketHeader
    lap_data: list[LapData]


@dataclass(frozen=True)
class FastestLap:
    car_idx: int  # Index of car this lap time relates to
    lap_time_in_ms: int  # Lap time in milliseconds


@dataclass(frozen=True)
class Retirement:
    car_idx: int  # Index of car that retired


@dataclass(frozen=True)
class DRSDisabled:
    car_idx: int  # Index of car that DRS was disabled for


@dataclass(frozen=True)
class TeamMateInPits:
    car_idx: int  # Index of car that is in pits


@dataclass(frozen=True)
class RaceWinner:
    car_idx: int  # Index of car that won race


@dataclass(frozen=True)
class Penalty:
    penalty_type: int  # Penalty type - see appendix
    infraction_type: int  # Infraction type - see appendix
    car_idx: int  # Index of car that received penalty
    other_car_idx: int  # Index of other car involved (if applicable)
    time: int  # Time in seconds (0 = no time penalty, 1+ = time penalty)
    lap_num: int  # Lap the penalty occurred on
    places_gained: int  # Number of places gained by this penalty


@dataclass(frozen=True)
class SpeedTrap:
    car_idx: int  # Index of car that triggered speed trap
    speed: float  # Speed in km/h


@dataclass(frozen=True)
class StartLights:
    num_lights: int


@dataclass(frozen=True)
class LightsOut:
    time: int  # Time since lights out (milliseconds)


@dataclass(frozen=True)
class DriveThroughPenaltyServed:
    car_idx: int  # Index of car that served penalty


@dataclass(frozen=True)
class StopGoPenaltyServed:
    car_idx: int  # Index of car that served penalty


@dataclass(frozen=True)
class Flashback:
    frame_identifier: int  # Frame identifier for the flashback


@dataclass(frozen=True)
class ButtonStatus:
    button_flags: int  # Bit flags indicating which buttons are pressed


@dataclass(frozen=True)
class RedFlag:
    car_idx: int  # Index of car that triggered red flag


@dataclass(frozen=True)
class Overtake:
    car_idx: int  # Index of car that overtook
    other_car_idx: int  # Index of car that was overtaken


@dataclass(frozen=True)
class SafetyCar:
    car_idx: int  # Index of car that triggered safety car


@dataclass(frozen=True)
class Collision:
    car_idx: int  # Index of car that caused collision
    other_car_idx: int  # Index of other car involved in collision
    time: int  # Time of collision (milliseconds)


type EventDataDetails = (
    FastestLap
    | Retirement
    | DRSDisabled
    | TeamMateInPits
    | RaceWinner
    | Penalty
    | SpeedTrap
    | StartLights
    | LightsOut
    | DriveThroughPenaltyServed
    | StopGoPenaltyServed
    | Flashback
    | ButtonStatus
    | RedFlag
    | Overtake
    | SafetyCar
    | Collision
)


@dataclass(frozen=True)
class PacketEventData:
    header: PacketHeader
    event_string_code: bytes  # 4 character code for the event
    event_details: EventDataDetails


@dataclass(frozen=True)
class LiveryColour:
    r: int  # Red component (0-255)
    g: int  # Green component (0-255)
    b: int  # Blue component (0-255)


@dataclass(frozen=True)
class ParticipantData:
    ai_controlled: int  # Whether the vehicle is AI controlled
    team_id: int  # Team id - see appendix
    nationality: int  # Nationality of the driver
    platform: int  # Platform - 1 = Steam, 3 = PlayStation, 4 = Xbox, 6 = Origin, 255 = unknown
    name: str  # Name of participant in UTF-8 format
    car_number: int
    your_telemetry: int  # The player's telemetry setting, 0 = restricted, 1 = public
    show_online_names: int  # Whether to show online names, 0 = off, 1 = on
    tech_level: int  # F1 World tech level
    ready_status: int  # 0 = not ready, 1 = ready, 2 = spectating


@dataclass(frozen=True)
class PacketParticipantsData:
    header: PacketHeader
    num_players: int
    lobby_players: list[ParticipantData]


@dataclass(frozen=True)
class CarSetupData:
    front_wing: int  # Front wing setting (0-10)
    rear_wing: int  # Rear wing setting (0-10)
    on_throttle: int  # Throttle setting when on throttle (0-100)
    off_throttle: int  # Throttle setting when off throttle (0-100)
    front_brake_bias: int  # Front brake bias (0-100)
    pits_limiter_status: int  # Pit limiter status - 0 = off, 1 = on
    fuel_mix: int  # Fuel mix - 0 = lean, 1 = standard, 2 = rich, 3 = max
    front_brake_pressure: int  # Front brake pressure (0-100)
    rear_brake_pressure: int  # Rear brake pressure (0-100)
    front_tyre_pressure: float  # Front tyre pressure (PSI)
    rear_tyre_pressure: float  # Rear tyre pressure (PSI)
    front_tyre_temperature: int  # Front tyre temperature (celsius)
    rear_tyre_temperature: int  # Rear tyre temperature (celsius)
    engine_power_ice: float  # Engine power output of ICE (W)
    engine_power_mguk: float  # Engine power output of MGU-K (W)
    ers_store_energy: float  # ERS energy store in Joules
    ers_deploy_mode: int  # ERS deployment mode, 0 = none, 1 = medium, 2 = hotlap, 3 = boost
    ers_harvested_this_lap_mguk: float  # ERS energy harvested this lap by MGU-K
    ers_harvested_this_lap_mguh: float  # ERS energy harvested this lap by MGU-H
    ers_harvest_limit_per_lap: float  # ERS energy harvest limit for this lap
    ers_deployed_this_lap: float  # ERS energy deployed this lap


@dataclass(frozen=True)
class PacketCarSetupData:
    header: PacketHeader
    car_setup_data: list[CarSetupData]
    next_front_wing_value: float  # Value of front wing after next pit stop - player only


@dataclass(frozen=True)
class CarTelemetryData:
    speed: int  # Speed of car in kilometres per hour
    throttle: float  # Amount of throttle applied (0.0 to 1.0)
    steer: float  # Steering (-1.0 (full lock left) to 1.0 (full lock right))
    brake: float  # Amount of brake applied (0.0 to 1.0)
    clutch: int  # Amount of clutch applied (0 to 100)
    gear: int  # Gear selected (1-8, N=0, R=-1)
    engine_rpm: int  # Engine RPM
    drs: int  # 0 = off, 1 = on
    rev_lights_percent: int  # Rev lights indicator (percentage)
    rev_lights_bit_value: int  # Rev lights (bit 0 = leftmost LED, bit 14 = rightmost LED)
    brakes_temperature: list[int]  # Brakes temperature (celsius)
    tyres_surface_temperature: list[int]  # Tyres surface temperature (celsius)
    tyres_inner_temperature: list[int]  # Tyres inner temperature (celsius)
    engine_temperature: int  # Engine temperature (celsius)
    tyres_pressure: list[float]  # Tyre pressure (PSI)
    surface_type: list[int]  # Driving surface, see appendices


@dataclass(frozen=True)
class PacketCarTelemetryData:
    header: PacketHeader
    car_telemetry_data: list[CarTelemetryData]
    mfd_panel_index: int  # Index of MFD panel open - 255 = MFD closed
    # Single player, race – 0 = Car setup, 1 = Pits
    # 2 = Damage, 3 = Engine, 4 = Temperatures
    # May vary depending on game mode
    mfd_panel_index_secondary_player: int
    suggested_gear: int  # Suggested gear for the player (1-8), 0 if no gear suggested


@dataclass(frozen=True)
class CarStatusData:
    traction_control: int  # Traction control - 0 = off, 1 = medium, 2 = full
    anti_lock_brakes: int  # 0 (off) - 1 (on)
    fuel_mix: int  # Fuel mix - 0 = lean, 1 = standard, 2 = rich, 3 = max
    front_brake_bias: int  # Front brake bias (percentage)
    pit_limiter_status: int  # Pit limiter status - 0 = off, 1 = on
    fuel_in_tank: float  # Current fuel mass
    fuel_capacity: float  # Fuel capacity
    fuel_remaining_laps: float  # Fuel remaining in terms of laps (value on MFD)
    max_rpm: int  # Cars max RPM, point of rev limiter
    idle_rpm: int  # Cars idle RPM
    max_gears: int  # Maximum number of gears
    drs_allowed: int  # 0 = not allowed, 1 = allowed
    drs_activation_distance: int  # 0 = DRS not available, non-zero - DRS will be available in [X] metres
    actual_tyre_compound: (
        int  # F1 Modern - 16 = C5, 17 = C4, 18 = C3, 19 = C2, 20 = C1, 21 = C0, 22 = C6, 7 = inter, 8 = wet
    )
    # F1 Classic - 9 = dry, 10 = wet
    # F2 – 11 = super soft, 12 = soft, 13 = medium, 14 = hard, 15 = wet
    visual_tyre_compound: int  # F1 visual (can be different from actual compound)
    # 16 = soft, 17 = medium, 18 = hard, 7 = inter, 8 = wet
    # F1 Classic – same as above
    # F2 ‘20, 15 = wet, 19 – super soft, 20 = soft, 21 = medium, 22 = hard
    tyres_age_laps: int  # Age in laps of the current set of tyres
    vehicle_fia_flags: int  # -1 = invalid/unknown, 0 = none, 1 = green, 2 = blue, 3 = yellow
    engine_power_ice: float  # Engine power output of ICE (W)
    engine_power_mguk: float  # Engine power output of MGU-K (W)
    ers_store_energy: float  # ERS energy store in Joules
    ers_deploy_mode: int  # ERS deployment mode, 0 = none, 1 = medium, 2 = hotlap, 3 = boost
    ers_harvested_this_lap_mguk: float  # ERS energy harvested this lap by MGU-K
    ers_harvested_this_lap_mguh: float  # ERS energy harvested this lap by MGU-H
    ers_harvest_limit_per_lap: float  # ERS energy harvest limit for this lap
    ers_deployed_this_lap: float  # ERS energy deployed this lap
    network_paused: int  # Whether the car is paused in a network game


@dataclass(frozen=True)
class PacketCarStatusData:
    header: PacketHeader
    car_status_data: list[CarStatusData]


@dataclass(frozen=True)
class FinalClassificationData:
    position: int  # Finishing position
    num_laps: int  # Number of laps completed
    grid_position: int  # Grid position of the car
    points: int
    num_pit_stops: int
    result_status: int  # Result status - 0 = invalid, 1 = inactive, 2 = active, 3 = finished, 4 = didnotfinish, 5 = disqualified, 6 = not classified, 7 = retired
    result_reason: int  # Result reason - 0 = invalid, 1 = retired, 2 = finished, 3 = terminal damage, 4 = inactive, 5 = not enough laps completed, 6 = black flagged
    # 7 = red flagged, 8 = mechanical failure, 9 = session skipped, 10 = session simulated
    best_lap_time_in_ms: int  # Best lap time of the session in milliseconds
    total_race_time: float  # Total race time in seconds without penalties
    penalties_time: int  # Total penalties accumulated in seconds
    num_penalties: int
    num_tyre_stints: int  # Number of tyres stints up to maximum
    tyre_stints_actual: list[int]  # Actual tyres used by this driver
    tyre_stints_visual: list[int]  # Visual tyres used by this driver
    tyre_stints_end_laps: list[int]  # The lap number stints end on


@dataclass(frozen=True)
class PacketFinalClassificationData:
    header: PacketHeader
    num_cars: int  # Number of cars in the final classification
    classification_data: list[FinalClassificationData]


@dataclass(frozen=True)
class LobbyInfoData:
    ai_controlled: int  # Whether the vehicle is AI (1) or Human (0) controlled
    team_id: int  # Team id - see appendix (65535 if no team currently selected)
    nationality: int  # Nationality of the driver
    platform: int  # 1 = Steam, 3 = PlayStation, 4 = Xbox, 6 = Origin, 255 = unknown
    name: str  # Name of participant in UTF-8 format – null terminated
    # Will be truncated with ... (U+2026) if too long
    car_number: int
    your_telemetry: int  # The player's UDP setting, 0 = restricted, 1 = public
    show_online_names: int  # The player's show online names setting, 0 = off, 1 = on
    tech_level: int  # F1 World tech level
    ready_status: int  # 0 = not ready, 1 = ready, 2 = spectating


@dataclass(frozen=True)
class PacketLobbyInfoData:
    header: PacketHeader
    num_players: int
    lobby_players: list[LobbyInfoData]


@dataclass(frozen=True)
class CarDamageData:
    tyres_wear: list[float]  # Tyre wear (percentage)
    tyres_damage: list[int]  # Tyre damage (percentage)
    brakes_damage: list[int]  # Brakes damage (percentage)
    tyre_blisters: list[int]  # Tyre blisters value (percentage)
    front_left_wing_damage: int  # Front left wing damage (percentage)
    front_right_wing_damage: int  # Front right wing damage (percentage)
    rear_wing_damage: int  # Rear wing damage (percentage)
    floor_damage: int  # Floor damage (percentage)
    diffuser_damage: int  # Diffuser damage (percentage)
    sidepod_damage: int  # Sidepod damage (percentage)
    drs_fault: int  # Indicator for DRS fault, 0 = OK, 1 = fault
    ers_fault: int  # Indicator for ERS fault, 0 = OK, 1 = fault
    gear_box_damage: int  # Gear box damage (percentage)
    engine_damage: int  # Engine damage (percentage)
    engine_mguh_wear: int  # Engine wear MGU-H (percentage)
    engine_es_wear: int  # Engine wear ES (percentage)
    engine_ce_wear: int  # Engine wear CE (percentage)
    engine_ice_wear: int  # Engine wear ICE (percentage)
    engine_mguk_wear: int  # Engine wear MGU-K (percentage)
    engine_tc_wear: int  # Engine wear TC (percentage)
    engine_blown: int  # Engine blown, 0 = OK, 1 = fault
    engine_seized: int  # Engine seized, 0 = OK, 1 = fault


@dataclass(frozen=True)
class PacketCarDamageData:
    header: PacketHeader
    car_damage_data: list[CarDamageData]


@dataclass(frozen=True)
class LapHistoryData:
    lap_time_in_ms: int  # Lap time in milliseconds
    sector1_time_ms_part: int  # Sector 1 milliseconds part
    sector1_time_minutes_part: int  # Sector 1 whole minute part
    sector2_time_ms_part: int  # Sector 2 time milliseconds part
    sector2_time_minutes_part: int  # Sector 2 whole minute part
    sector3_time_ms_part: int  # Sector 3 time milliseconds part
    sector3_time_minutes_part: int  # Sector 3 whole minute part
    lap_valid_bit_flags: int  # 0x01 bit set-lap valid,      0x02 bit set-sector 1 valid
    # 0x04 bit set-sector 2 valid, 0x08 bit set-sector 3 valid


@dataclass(frozen=True)
class TyreStintHistoryData:
    end_lap: int  # Lap the tyre usage ends on (255 if current tyre)
    tyre_actual_compound: int  # Actual tyres used by this driver
    tyre_visual_compound: int  # Visual tyres used by this driver


@dataclass(frozen=True)
class PacketSessionHistoryData:
    header: PacketHeader
    car_idx: int  # Index of the car this lap data relates to
    num_laps: int  # Num laps in the data (including current partial lap)
    num_tyre_stints: int
    best_lap_time_lap_num: int  # Lap the best lap time was achieved on
    best_sector1_lap_num: int  # Lap the best Sector 1 time was achieved on
    best_sector2_lap_num: int  # Lap the best Sector 2 time was achieved on
    best_sector3_lap_num: int  # Lap the best Sector 3 time was achieved on
    lap_history_data: list[LapHistoryData]  # 100 laps of data max
    tyre_stints_history_data: list[TyreStintHistoryData]


@dataclass(frozen=True)
class TyreSetData:
    actual_tyre_compound: int  # Actual tyre compound used
    visual_tyre_compound: int  # Visual tyre compound used
    wear: int  # Tyre wear (percentage)
    available: int  # Whether this set is currently available
    recommended_session: int  # Recommended session for tyre set, see appendix
    life_span: int  # Laps left in this tyre set
    usable_life: int  # Max number of laps recommended for this compound
    lap_delta_time: int  # Lap delta time in milliseconds compared to fitted set
    fitted: int  # Whether the set is fitted or not


@dataclass(frozen=True)
class PacketTyreSetsData:
    header: PacketHeader
    car_idx: int  # Index of the car this data relates to
    tyre_set_data: list[TyreSetData]  # 13 dry + 7 wet
    fitted_idx: int  # Index into array of fitted tyre


@dataclass(frozen=True)
class PacketMotionExData:
    header: PacketHeader
    suspension_position: list[float]  # Note: All wheel arrays have the following order:
    suspension_velocity: list[float]  # RL, RR, FL, FR
    suspension_acceleration: list[float]  # RL, RR, FL, FR
    wheel_speed: list[float]  # Speed of each wheel
    wheel_slip_ratio: list[float]  # Slip ratio for each wheel
    wheel_slip_angle: list[float]  # Slip angles for each wheel
    wheel_lat_force: list[float]  # Lateral forces for each wheel
    wheel_long_force: list[float]  # Longitudinal forces for each wheel
    height_of_cog_above_ground: float  # Height of centre of gravity above ground
    local_velocity_x: float  # Velocity in local space X - metres/s
    local_velocity_y: float  # Velocity in local space Y
    local_velocity_z: float  # Velocity in local space Z
    angular_velocity_x: float  # Angular velocity x-component - radians/s
    angular_velocity_y: float  # Angular velocity y-component
    angular_velocity_z: float  # Angular velocity z-component
    angular_acceleration_x: float  # Angular acceleration x-component - radians/s/s
    angular_acceleration_y: float  # Angular acceleration y-component
    angular_acceleration_z: float  # Angular acceleration z-component
    front_wheels_angle: float  # Current front wheels angle in radians
    wheel_vert_force: list[float]  # Vertical forces for each wheel
    front_aero_height: float  # Front plank edge height above road surface
    rear_aero_height: float  # Rear plank edge height above road surface
    front_roll_angle: float  # Roll angle of the front suspension
    rear_roll_angle: float  # Roll angle of the rear suspension
    chassis_yaw: float  # Yaw angle of the chassis relative to the direction of motion - radians
    chassis_pitch: float  # Pitch angle of the chassis relative to the direction of motion - radians
    wheel_camber: list[float]  # Camber of each wheel in radians
    wheel_camber_gain: list[
        float
    ]  # Camber gain for each wheel in radians, difference between active camber and dynamic camber


@dataclass(frozen=True)
class TimeTrialDataSet:
    car_idx: int  # Index of the car this data relates to
    team_id: int  # Team id - see appendix
    lap_time_in_ms: int  # Lap time in milliseconds
    sector1_time_in_ms: int  # Sector 1 time in milliseconds
    sector2_time_in_ms: int  # Sector 2 time in milliseconds
    sector3_time_in_ms: int  # Sector 3 time in milliseconds
    traction_control: int  # 0 = assist off, 1 = assist on
    gearbox_assist: int  # 0 = assist off, 1 = assist on
    anti_lock_brakes: int  # 0 = assist off, 1 = assist on
    equal_car_performance: int  # 0 = Realistic, 1 = Equal
    custom_setup: int  # 0 = No, 1 = Yes
    valid: int  # 0 = invalid, 1 = valid


@dataclass(frozen=True)
class PacketTimeTrialData:
    header: PacketHeader
    player_session_best_data_set: TimeTrialDataSet  # Player session best data set
    personal_best_data_set: TimeTrialDataSet  # Personal best data set
    rival_data_set: TimeTrialDataSet  # Rival data set


@dataclass(frozen=True)
class PacketLapPositionsData:
    header: PacketHeader
    num_laps: int  # Number of laps in the data
    lap_start: int  # Index of the lap where the data starts, 0 indexed
    # Array holding the position of the car in a given lap, 0 if no record
    position_for_vehicle_idx: list[list[int]]  # 2D array [laps][cars]


@dataclass(frozen=True)
class CarTelemetry2Data:
    active_aero_mode: int  # 0 = Corner mode, 1 = Straight mode
    active_aero_available: int  # 0 = not available, 1 = available
    active_aero_activation_distance: (
        int  # 0 = Active aero not available, non-zero - Active aero will be available in [X] metres
    )
    overtake_available: int  # 0 = not available, 1 = available
    overtake_active: int  # 0 = not active, 1 = active
    overtake_activation_distance: (
        int  # 0 = Overtake Mode not available, non-zero - Overtake Mode will be available in [X] metres
    )
    regulations_2026: int  # 0 = vehicle conforms to pre-2026, 1 = 2026 regulations applicable
    driving_wrong_way: int  # Whether the car is driving the wrong way


@dataclass(frozen=True)
class PacketCarTelemetry2Data:
    header: PacketHeader
    car_telemetry2_data: list[CarTelemetry2Data]


# TODO code to ctor
EVENT_CODES = MappingProxyType(
    {
        "session_started": b"SSTA",
        "session_ended": b"SEND",
        "fastest_lap": b"FTLP",
        "retirement": b"RTMT",
        "drs_enabled": b"DRSE",
        "drs_disabled": b"DRSD",
        "team_mate_in_pits": b"TMPT",
        "chequered_flag": b"CHQF",
        "race_winner": b"RCWN",
        "penalty": b"PENA",
        "speed_trap": b"SPTP",
        "start_lights": b"STLG",
        "lights_out": b"LGOT",
        "drive_through_served": b"DTSV",
        "stop_go_served": b"SGSV",
        "flashback": b"FLBK",
        "button_status": b"BUTN",
        "red_flag": b"RDFL",
        "overtake": b"OVTK",
        "safety_car": b"SCAR",
        "collision": b"COLL",
    }
)
