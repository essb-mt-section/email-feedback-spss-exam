__version__ = "0.7.8"
__author__ = "Oliver Lindemann"

from . import json_settings, const
settings = json_settings.JSONSettings(appname=
                        const.APPNAME.replace(" ","_").lower(),
                        settings_file_name="settings.json",
                        defaults=const.DEFAULT_SETTINGS)

from .gui import run