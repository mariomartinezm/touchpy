import urwid


class View(urwid.WidgetWrap):
    def __init__(self, controller):
        self.controller = controller

        devices = self.controller.model.get_devices()

        if 'device 0' in devices:
            self.curr_device = devices['device 0']
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
        self.curr_device = device

        self.frame_settings = None
        self.frame_settings = self.settings_widgets()

        options = self.columns.options(width_amount=2)
        self.columns.contents = [(self.frame_devices, options),
                                 (self.frame_settings, options)]


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
            widget = urwid.Button(device.name)
            urwid.connect_signal(widget, 'click', self.device_change,
                                 device)
            widget = urwid.AttrWrap(widget, 'button_normal', 'button_select')
            widgets.append(widget)

        w = urwid.LineBox(urwid.ListBox(urwid.SimpleListWalker(widgets)))
        w = urwid.AttrWrap(w, 'inner_border')
        w = urwid.Frame(w, urwid.Text(('header', 'Devices:')))

        return w

    def settings_widgets(self):
        properties = self.curr_device.properties

        cb_typing = None
        cb_tapping = None
        self.text_speed = None

        widgets = []
        for p, val in properties.items():
            if p == 'libinput Disable While Typing Enabled':
                cb_typing = urwid.CheckBox('Disable while typing',
                                           state=bool(properties[p]),
                                           on_state_change=self.on_cb_typing_change)
                cb_typing = urwid.AttrWrap(cb_typing, 'text_label')
            elif p == 'libinput Tapping Enabled':
                cb_tapping = urwid.CheckBox('Tap to click',
                        state=bool(properties[p]),
                        on_state_change=self.on_cb_tapping_change)
                cb_tapping = urwid.AttrWrap(cb_tapping, 'text_label')
            elif p == 'libinput Accel Speed':
                self.text_speed = urwid.Text(('text_val',
                    str(properties[p])))

        if cb_typing is not None:
            widgets.append(cb_typing)

        if cb_typing is not None:
            widgets.append(cb_tapping)

        if self.text_speed is not None:
            if (cb_typing is not None) or (cb_tapping is not None):
                widgets.append(urwid.Divider(div_char='-'))

            widgets.append(urwid.GridFlow([urwid.Text(('text_label', 'Cursor speed: ')),
                self.text_speed],
                15, 0, 0, 'left'))
            widgets.append(urwid.Divider(div_char='-'))

        widgets.append(self.button('Quit', self.exit_program))

        w = urwid.LineBox(urwid.ListBox(urwid.SimpleListWalker(widgets)))
        w = urwid.AttrWrap(w, 'inner_border')
        w = urwid.Frame(w, urwid.Text(('header', 'Settings:')))

        return w

    def main_window(self):
        self.frame_devices = self.devices_list()
        self.frame_settings = self.settings_widgets()

        self.columns = urwid.Columns([('weight', 2, self.frame_devices),
                                      ('weight', 2, self.frame_settings)],
                                      dividechars=1)

        w = urwid.LineBox(self.columns)
        w = urwid.AttrWrap(w, 'outer_border')

        return w
