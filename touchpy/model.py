import re
import subprocess
from device import Device
from device import DeviceType


class Model:
    """
    A class responsible for interfacing with libinput
    """
    def __init__(self):
        # Get names of all devices managed by libinput
        args = ['xinput', 'list', '--name-only']
        full_names, err = self.__run_command(args)

        # Get names of touchpad devices
        p = re.compile(r'.*touchpad', re.IGNORECASE)
        names = p.findall(full_names)

        self.devices = {}

        for name, index in zip(names, range(0, len(names))):
            args = ['xinput', 'list', '--id-only', name]
            dev_id, err = self.__run_command(args)

            device = Device(name)
            device.dev_id = int(dev_id)
            device.type = DeviceType.Touchpad
            device.properties = self.get_device_properties(device)

            key = "Touchpad " + str(index)
            self.devices.update({key: device})

        # Get names of mouse devices
        p = re.compile(r'.*mouse', re.IGNORECASE)
        names = p.findall(full_names)

        for name, index in zip(names, range(0, len(names))):
            args = ['xinput', 'list', '--id-only', name]
            dev_id, err = self.__run_command(args)

            dev = Device(name)
            dev.dev_id = int(dev_id)
            dev.type = DeviceType.Mouse

            key = "Mouse " + str(index)
            self.devices.update({key: dev})

    def __run_command(self, args):
        process = subprocess.Popen(args,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   universal_newlines=True)

        output, err = process.communicate()

        return output, err

    def get_devices(self):
        return self.devices

    def set_disable_while_typing(self, dev_name, state):
        args = ['xinput', '--set-prop', dev_name,
                'libinput Disable While Typing Enabled', str(int(state))]
        self.__run_command(args)

    def set_tap_to_click(self, dev_name, state):
        args = ['xinput', '--set-prop', dev_name,
                'libinput Tapping Enabled', str(int(state))]
        self.__run_command(args)

    def set_cursor_speed(self, dev_name, speed):
        args = ['xinput', '--set-prop', dev_name,
                'libinput Accel Speed', str(speed)]
        self.__run_command(args)

    def get_device_properties(self, device):
        args = ['xinput', '--list-props', device.name]
        props_list, err = self.__run_command(args)

        if device.type == DeviceType.Touchpad:
            properties = {'libinput Tapping Enabled': 0,
                          'libinput Disable While Typing Enabled': 0,
                          'libinput Accel Speed': 0.0}
        else:
            properties = {'libinput Accel Speed': 0}

        for prop in properties.keys():
            r = re.compile(r'\s*' + prop + r' \(\d+\):\s+.+',
                           re.IGNORECASE)
            value = r.findall(props_list)[0].split()[-1]

            if prop == 'libinput Accel Speed':
                properties[prop] = float(value)
            else:
                properties[prop] = int(value)

        return properties
