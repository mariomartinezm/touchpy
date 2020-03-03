import urwid
import subprocess
import re


class Model:
    """
    A class responsible for interfacing with libinput
    """
    def __init__(self):
        # Get device names
        process = subprocess.Popen(['xinput', 'list', '--name-only'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   universal_newlines=True)

        stdout, stderr = process.communicate()

        p = re.compile(r'.*touchpad', re.IGNORECASE)
        names = p.findall(stdout)

        # Get device IDs
        ids = []
        for name in names:
            process = subprocess.Popen(['xinput', 'list', '--id-only',
                                       name],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       universal_newlines=True)

            stdout, stderr = process.communicate()
            ids.append(int(stdout))

        self.devices = {name: dev_id for (name, dev_id) in zip(names, ids)}

    def get_devices(self):
        return self.devices

    def set_disable_while_typing(self, state):
        process = subprocess.Popen(['xinput', '--set-prop',
                                    'SynPS/2 Synaptics TouchPad',
                                    'libinput Disable While Typing Enabled',
                                    str(int(state))],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   universal_newlines=True)

        stdout, stderr = process.communicate()

    def set_tap_to_click(self, state):
        process = subprocess.Popen(['xinput', '--set-prop',
                                    'SynPS/2 Synaptics TouchPad',
                                    'libinput Tapping Enabled',
                                    str(int(state))],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   universal_newlines=True)

        stdout, stderr = process.communicate()

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
        self.controller.model.set_disable_while_typing(state)

    def on_cb_tapping_change(self, w, state):
        self.controller.model.set_tap_to_click(state)

    def device_change(self, button, dev_name):
        self.current_device = \
            self.controller.model.get_device_properties(dev_name)

    def button(self, t, fn):
        w = urwid.Button(t, fn)
        return w

    def exit_program(self, w):
        raise urwid.ExitMainLoop()

    def devices_list(self):
        widgets = []
        for dev_name, dev_id in self.controller.model.get_devices().items():
            widget = urwid.Button(dev_name)
            urwid.connect_signal(widget, 'click', self.device_change, dev_name)
            widgets.append(widget)

        w = urwid.LineBox(urwid.ListBox(urwid.SimpleListWalker(widgets)))
        w = urwid.Frame(w, urwid.Text('Devices:'))

        return w

    def settings_controls(self):
        properties = self.controller.model.get_device_properties('SynPS/2 Synaptics TouchPad')

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
