import re
import subprocess
import logging
from device import Device


class Model:
    """
    A class responsible for interfacing with libinput
    """
    def __init__(self):
        logging.debug('Getting device names...')
        args = ['xinput', 'list', '--name-only']
        device_names, err = self.__run_command(args)
        device_names = device_names.splitlines()
        logging.debug(f'Done, got {len(device_names)} devices.')

        # Since libinput does not expose the device type to the caller, it
        # is neccesary to use the device's properties to determine if the
        # device will be supported
        self.devices = {}
        dev_index = 0

        for dev_name in device_names:
            properties = self.get_device_properties(dev_name)

            dev_prop = {p: val for p, val in properties.items()
                        if p in
                        ['libinput Tapping Enabled',
                         'libinput Disable While Typing Enabled',
                         'libinput Accel Speed']}

            if len(dev_prop) > 0:
                device = Device(dev_name)
                device.properties = dev_prop

                key = f"device {dev_index}"
                self.devices[key] = device

                dev_index += 1

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

    def get_device_properties(self, dev_name):
        args = ['xinput', '--list-props', dev_name]
        output, err = self.__run_command(args)

        # Discard the first line since it contains the device name
        properties = {}
        for line in output.splitlines()[1:]:
            match = re.search('\s(.*)\s+\((.*)\):\s+(.*)', line)
            properties[match.group(1)] = match.group(3)

        return properties
