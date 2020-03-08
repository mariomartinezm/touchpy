import urwid
import subprocess
import re


class Device:
    def __init__(self, name):
        self.name = name
        self.dev_id = 0
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

            dev = Device(name)
            dev.dev_id = int(dev_id)
            dev.properties = self.get_device_properties(dev.name)

            key = "Touchpad " + str(index)
            self.devices.update({key: dev})

        # Get names of mouse devices
        p = re.compile(r'.*mouse', re.IGNORECASE)
        names = p.findall(full_names)

        for name, index in zip(names, range(0, len(names))):
            args = ['xinput', 'list', '--id-only', name]
            dev_id, err = self.__run_command(args)

            dev = Device(name)
            dev.dev_id = int(dev_id)

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

    def get_device_properties(self, dev_name):
        process = subprocess.Popen(['xinput', '--list-props', dev_name],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   universal_newlines=True)

        stdout, setderr = process.communicate()

        properties = {'libinput Tapping Enabled': 0,
                      'libinput Disable While Typing Enabled': 0}

        for prop in properties.keys():
            r = re.compile(r'\s*' + prop + r' \(\d+\):\s+\d',
                           re.IGNORECASE)
            value = r.findall(stdout)[0].split()[-1]
            properties[prop] = int(value)

        return properties


class View(urwid.WidgetWrap):
    def __init__(self, controller):
        self.controller = controller
        urwid.WidgetWrap.__init__(self, self.main_window())

    def on_cb_typing_change(self, w, state):
        self.controller.model.set_disable_while_typing(self.curr_device.name,
                                                       state)

    def on_cb_tapping_change(self, w, state):
        self.controller.model.set_tap_to_click(self.curr_device.name,
                                               state)

    def device_change(self, button, dev_name):
        self.current_device = \
            self.controller.model.get_device_properties(dev_name)

    def button(self, t, fn):
        w = urwid.Button(t, fn)
        return w

    def exit_program(self, w):
        raise urwid.ExitMainLoop()

    def devices_list(self):
        devices = self.controller.model.get_devices()

        if 'Touchpad 0' in devices:
            self.curr_device = devices['Touchpad 0']
        elif 'Mouse 0' in devices:
            self.curr_device = devices['Mouse 0']
        else:
            self.curr_device = None

        widgets = []
        for dev_name, device in devices.items():
            widget = urwid.Button(dev_name)
            urwid.connect_signal(widget, 'click', self.device_change,
                                 device.name)
            widgets.append(widget)

        w = urwid.LineBox(urwid.ListBox(urwid.SimpleListWalker(widgets)))
        w = urwid.Frame(w, urwid.Text('Devices:'))

        return w

    def settings_controls(self):
        properties = self.curr_device.properties

        cb_typing = urwid.CheckBox('Disable while typing',
                                   state=bool(properties['libinput Disable While Typing Enabled']),
                                   on_state_change=self.on_cb_typing_change)
        cb_tapping = urwid.CheckBox('Tap to click',
                                    state=bool(properties['libinput Tapping Enabled']),
                                    on_state_change=self.on_cb_tapping_change)

        widgets = [
            cb_typing,
            cb_tapping,
            self.button('Quit', self.exit_program)
            ]

        w = urwid.LineBox(urwid.ListBox(urwid.SimpleListWalker(widgets)))
        w = urwid.Frame(w, urwid.Text('Settings:'))

        return w

    def main_window(self):
        w = urwid.Columns([('weight', 2, self.devices_list()),
                           ('weight', 2, self.settings_controls())],
                          dividechars=1)

        w = urwid.LineBox(w)

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
