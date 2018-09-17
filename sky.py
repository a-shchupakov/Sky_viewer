import os
import argparse
from modules import sky_gui
from tkinter import *


def check_version():
    if sys.version_info < (3, 3):
        print('Use python >= 3.3', file=sys.stderr)
        sys.exit()


def raise_error():
    print('Usage error.\r\nTry using ./sky.py --help')
    sys.exit()


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--height', type=int, default=600,
                        help='Base height of a window. Default value is 600')
    parser.add_argument('--width', type=int, default=900,
                        help='Base width of a window. \nDefault value is 900')
    parser.add_argument('--fov', type=int, default=65,
                        help='Field of view in percents (from 1 to 100).  Default value is 65')
    parser.add_argument('-b', '--bright', type=str, default='more 0',
                        help='Choose brightness filter. There are two options - "less" or "more". Then choose apparent'
                             'magnitude value. For example "more 5" entails displaying stars which magnitude value more'
                             'than 5. The brighter an object appears, the lower its magnitude value '
                             '(i.e. inverse relation).')
    parser.add_argument('-m', '--music', type=str, default='Thunderbird.mp3',
                        help='Choose music file which will be played. Default file is "Thunderbird.mp3".'
                             'You can disable it in app by pressing RMB')
    return parser


def check_fov(fov):
    if not (1 <= fov <= 100):
        raise_error()


def check_bright(bright):
    if bright:
        info = bright.split()
        if not (info[0] == 'more' or info[0] == 'less'):
            raise_error()
        value = None
        try:
            value = float(info[1])
        except (ValueError, IndexError):
            raise_error()
        else:
            if not (0 <= value < 100):
                raise_error()


def main():
    check_version()
    parser = create_parser()
    args = parser.parse_args()

    base_width = args.width
    base_height = args.height
    fov = args.fov
    bright = args.bright
    music_path = args.music

    check_fov(fov)
    check_bright(bright)

    master = sky_gui.ConfigurationWindow(canvas_width=base_width, canvas_height=base_height, fov=fov, bright=bright,
                                         music_path=music_path)

    master.mainloop()


if __name__ == '__main__':
    main()
