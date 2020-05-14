import enum


class DeviceType(enum.Enum):
    Unknown = 0
    Touchpad = 1
    Mouse = 2


class Device:
    def __init__(self, name):
        self.name = name
        self.dev_id = 0
        self.type = DeviceType.Unknown
        self.properties = {}
