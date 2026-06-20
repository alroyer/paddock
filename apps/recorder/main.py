from telemetry.packet import (
    PacketCarDamageData,
    PacketCarSetupData,
    PacketCarStatusData,
    PacketCarTelemetryData,
    PacketEventData,
    PacketFinalClassificationData,
    PacketLapData,
    PacketLapPositionsData,
    PacketLobbyInfoData,
    PacketMotionData,
    PacketMotionExData,
    PacketParticipantsData,
    PacketSessionData,
    PacketSessionHistoryData,
    PacketTimeTrialData,
    PacketTyreSetsData,
)


def main():
    print("PacketMotionData size:", PacketMotionData.SIZE)
    print("PacketSessionData size **:", PacketSessionData.SIZE)
    print("PacketLapData size:", PacketLapData.SIZE)
    print("PacketEventData size **:", PacketEventData.SIZE)
    print("PacketParticipantsData size:", PacketParticipantsData.SIZE)
    print("PacketCarSetupData size:", PacketCarSetupData.SIZE)
    print("PacketCarTelemetryData size:", PacketCarTelemetryData.SIZE)
    print("PacketCarStatusData size:", PacketCarStatusData.SIZE)
    print("PacketFinalClassificationData size:", PacketFinalClassificationData.SIZE)
    print("PacketLobbyInfoData size:", PacketLobbyInfoData.SIZE)
    print("PacketCarDamageData size:", PacketCarDamageData.SIZE)
    print("PacketSessionHistoryData size:", PacketSessionHistoryData.SIZE)
    print("PacketTyreSetsData size:", PacketTyreSetsData.SIZE)
    print("PacketMotionExData size: **", PacketMotionExData.SIZE)
    print("PacketTimeTrialData size:", PacketTimeTrialData.SIZE)
    print("PacketLapPositionsData size:", PacketLapPositionsData.SIZE)


if __name__ == "__main__":
    main()
