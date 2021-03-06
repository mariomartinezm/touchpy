import os
import configparser
from ast import literal_eval as make_tuple

HOME = os.getenv('HOME', os.getenv('USERPROFILE'))
XDG_CONF_DIR = os.getenv('XDG_CONF_DIR', os.path.join(HOME, '.config'))
CONF_DIR = os.path.join(XDG_CONF_DIR, 'touchpy')


def create_config_file():
    """ Create configuration file """
    os.makedirs(CONF_DIR, exist_ok=True)
    filename = os.path.join(CONF_DIR, 'config.ini')

    config = configparser.ConfigParser()

    if os.path.isfile(filename):
        config.read(filename)

        palette = [(key, '', '', '',) +
                   make_tuple(config['Theme'][key]) for key in
                   config['Theme']]

        return palette
    else:
        palette = [
                ('outer_border', '', '', '', 'dark cyan', 'black'),
                ('inner_border', '', '', '', 'dark cyan', 'black'),
                ('header', '', '', '', 'yellow, bold', 'black'),
                ('text_label', '', '', '', 'dark magenta', 'black'),
                ('text_val', '', '', '', 'dark cyan', 'black'),
                ('button_normal', '', '', '', 'light green', 'black'),
                ('button_select', '', '', '', 'black', 'light green')
                ]

        config['Theme'] = {p[0]: str((p[4], p[5], )) for p in palette}

        with open(filename, 'w') as configfile:
            config.write(configfile)

        return palette
