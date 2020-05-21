import urwid
from model import Model
from view import View
import settings


class Controller:
    """
    A class responsible for running the application.
    """
    def __init__(self):
        self.palette = settings.create_config_file()

        self.model = Model()
        self.view = View(self)

    def main(self):
        self.loop = urwid.MainLoop(self.view,
                                   self.palette,
                                   unhandled_input=self.unhandled_input)
        self.loop.run()

    def unhandled_input(self, k):
        if k in ('Q', 'q'):
            raise urwid.ExitMainLoop()
        if k in ('H', 'h'):
            self.view.on_speed_change(increase=False)
        if k in ('L', 'l'):
            self.view.on_speed_change(increase=True)
