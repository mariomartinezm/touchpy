import logging
from controller import Controller


def main():
    Controller().main()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, filename='touchpy.log')
    main()
