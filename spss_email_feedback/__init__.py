__version__ = "0.6.5"
__author__ = "Oliver Lindemann"

APPNAME = "SPSS email feedback"
from . import json_settings, defaults
settings = json_settings.JSONSettings(appname=APPNAME.replace(" ", "_"),
                                      settings_file_name="settings.json",
                                      defaults=defaults.SETTINGS)

from .gui import run