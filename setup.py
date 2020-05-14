from setuptools import setup

setup(
    name='touchpy',
    version='0.1',
    description='A simple TUI for managing pointing devices with libinput',
    author='Mario M. M.',
    author_email='mariomartinezmolina@live.com',
    packages=['touchpy'],
    install_requires=['urwid'],
)
