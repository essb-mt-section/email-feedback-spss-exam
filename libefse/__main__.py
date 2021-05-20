from . import gui, APPNAME, __version__
import sys as _sys

def run():
    if _sys.version_info[0] != 3 or _sys.version_info[1]<5:

        raise RuntimeError("{} {} ".format(APPNAME, __version__) +
                          "is not compatible with Python {0}.{1}.".format(
                                                        _sys.version_info[0],
                                                        _sys.version_info[1]) +
                          "\n\nPlease use Python 3.5 or higher.")

    gui.run()

if __name__ == "__main__":
    run()