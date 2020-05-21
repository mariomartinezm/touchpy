import urwid
from device import DeviceType


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

        self.curr_device = device

    def on_speed_change(self, increase=True):
        speed = float(self.text_speed.text)

        if increase is True and speed < 1.0:
            speed = speed + 0.1
        elif increase is False and speed > -1.0:
            speed = speed - 0.1

        self.controller.model.set_cursor_speed(self.curr_device.name, speed)
        self.text_speed.set_text(('text_val', '{:.1f}'.format(speed)))

    def button(self, t, fn):
        w = urwid.Button(t, fn)
        w = urwid.AttrWrap(w, 'button_normal', 'button_select')
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
            widget = urwid.AttrWrap(widget, 'button_normal', 'button_select')
            widgets.append(widget)

        w = urwid.LineBox(urwid.ListBox(urwid.SimpleListWalker(widgets)))
        w = urwid.AttrWrap(w, 'inner_border')
        w = urwid.Frame(w, urwid.Text(('header', 'Devices:')))

        return w

    def touchpad_widgets(self):
        properties = self.curr_device.properties

        prop_name = 'libinput Disable While Typing Enabled'
        cb_typing = urwid.CheckBox('Disable while typing',
                                   state=bool(properties[prop_name]),
                                   on_state_change=self.on_cb_typing_change)
        cb_typing = urwid.AttrWrap(cb_typing, 'text_label')

        prop_name = 'libinput Tapping Enabled'
        cb_tapping = urwid.CheckBox('Tap to click',
                                    state=bool(properties[prop_name]),
                                    on_state_change=self.on_cb_tapping_change)
        cb_tapping = urwid.AttrWrap(cb_tapping, 'text_label')

        prop_name = 'libinput Accel Speed'
        self.text_speed = urwid.Text(('text_val',
                                     str(properties[prop_name])))

        widgets = [
            cb_typing,
            cb_tapping,
            urwid.Divider(div_char='-'),
            urwid.GridFlow([urwid.Text(('text_label', 'Cursor speed: ')),
                           self.text_speed],
                           15, 0, 0, 'left'),
            urwid.Divider(div_char='-'),
            self.button('Quit', self.exit_program)
            ]

        w = urwid.LineBox(urwid.ListBox(urwid.SimpleListWalker(widgets)))
        w = urwid.AttrWrap(w, 'inner_border')
        w = urwid.Frame(w, urwid.Text(('header', 'Settings:')))

        return w

    def mouse_widgets(self):
        widgets = [urwid.Text('Placeholder for mouse widgets')]

        w = urwid.LineBox(urwid.ListBox(urwid.SimpleListWalker(widgets)))
        w = urwid.AttrWrap(w, 'inner_border')
        w = urwid.Frame(w, urwid.Text(('header', 'Settings:')))

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
        w = urwid.AttrWrap(w, 'outer_border')

        return w
