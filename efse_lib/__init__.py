__version__ = "0.7.8"
__author__ = "Oliver Lindemann"

import sys as _sys
from . import const
if _sys.version_info[0] != 3 or _sys.version_info[1]<5:

    raise RuntimeError("{} {} ".format(const.APPNAME, __version__) +
                      "is not compatible with Python {0}.{1}.".format(
                                                    _sys.version_info[0],
                                                    _sys.version_info[1]) +
                      "\n\nPlease use Python 3.5 or higher.")

from .json_settings import JSONSettings as _JSONSettings
settings = _JSONSettings(appname=const.APPNAME.replace(" ","_").lower(),
                        settings_file_name="settings.json",
                        defaults=const.DEFAULT_SETTINGS)

from .gui import run