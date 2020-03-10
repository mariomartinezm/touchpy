import urwid
import subprocess
import re
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

    def get_device_properties(self, device):
        args = ['xinput', '--list-props', device.name]
        props_list, err = self.__run_command(args)

        if device.type == DeviceType.Touchpad:
            properties = {'libinput Tapping Enabled': 0,
                          'libinput Disable While Typing Enabled': 0}
        else:
            properties = {}

        for prop in properties.keys():
            r = re.compile(r'\s*' + prop + r' \(\d+\):\s+\d',
                           re.IGNORECASE)
            value = r.findall(props_list)[0].split()[-1]
            properties[prop] = int(value)

        return properties


class View(urwid.WidgetWrap):
    def __init__(self, controller):
        self.controller = controller

        devices = self.controller.model.get_devices()

        if 'Touchpad 0' in devices:
            self.curr_device = devices['Touchpad 0']
        elif 'Mouse 0' in devices:
            self.curr_device = devices['Mouse 0']
        else:
            self.curr_device = None

        urwid.WidgetWrap.__init__(self, self.main_window())

    def on_cb_typing_change(self, w, state):
        self.controller.model.set_disable_while_typing(self.curr_device.name,
                                                       state)

    def on_cb_tapping_change(self, w, state):
        self.controller.model.set_tap_to_click(self.curr_device.name,
                                               state)

    def device_change(self, button, device):
        if device.type == DeviceType.Touchpad:
            options = self.columns.options(width_amount=2)
            self.columns.contents = [(self.frame_devices, options),
                                     (self.frame_touchpad, options)]
        else:
            options = self.columns.options(width_amount=2)
            self.columns.contents = [(self.frame_devices, options),
                                     (self.frame_mouse, options)]

    def button(self, t, fn):
        w = urwid.Button(t, fn)
        return w

    def exit_program(self, w):
        raise urwid.ExitMainLoop()

    def devices_list(self):
        devices = self.controller.model.get_devices()

        widgets = []
        for dev_name, device in devices.items():
            widget = urwid.Button(dev_name)
            urwid.connect_signal(widget, 'click', self.device_change,
                                 device)
            widgets.append(widget)

        w = urwid.LineBox(urwid.ListBox(urwid.SimpleListWalker(widgets)))
        w = urwid.Frame(w, urwid.Text('Devices:'))

        return w

    def touchpad_widgets(self):
        properties = self.curr_device.properties

        prop_name = 'libinput Disable While Typing Enabled'
        cb_typing = urwid.CheckBox('Disable while typing',
                                   state=bool(properties[prop_name]),
                                   on_state_change=self.on_cb_typing_change)

        prop_name = 'libinput Tapping Enabled'
        cb_tapping = urwid.CheckBox('Tap to click',
                                    state=bool(properties[prop_name]),
                                    on_state_change=self.on_cb_tapping_change)

        widgets = [
            cb_typing,
            cb_tapping,
            self.button('Quit', self.exit_program)
            ]

        w = urwid.LineBox(urwid.ListBox(urwid.SimpleListWalker(widgets)))
        w = urwid.Frame(w, urwid.Text('Settings:'))

        return w

    def mouse_widgets(self):
        widgets = [urwid.Text('Placeholder for mouse widgets')]

        w = urwid.LineBox(urwid.ListBox(urwid.SimpleListWalker(widgets)))
        w = urwid.Frame(w, urwid.Text('Settings:'))

        return w

    def main_window(self):
        self.frame_devices = self.devices_list()
        self.frame_touchpad = self.touchpad_widgets()
        self.frame_mouse = self.mouse_widgets()

        if self.curr_device.type == DeviceType.Touchpad:
            self.columns = urwid.Columns([('weight', 2, self.frame_devices),
                                          ('weight', 2, self.frame_touchpad)],
                                         dividechars=1)
        else:
            self.columns = urwid.Columns([('weight', 2, self.frame_devices),
                                          ('weight', 2, self.frame_mouse)],
                                         dividechars=1)

        w = urwid.LineBox(self.columns)

        return w


class Controller:
    """
    A class responsible for running the application.
    """
    def __init__(self):
        self.model = Model()
        self.view = View(self)

    def main(self):
        self.loop = urwid.MainLoop(self.view,
                                   unhandled_input=self.unhandled_input)
        self.loop.run()

    def unhandled_input(self, k):
        if k in ('Q', 'q'):
            raise urwid.ExitMainLoop()


def main():
    Controller().main()


if __name__ == '__main__':
    main()
