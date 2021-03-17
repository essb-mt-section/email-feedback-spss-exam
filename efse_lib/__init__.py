__version__ = "0.7.7"
__author__ = "Oliver Lindemann"

APPNAME = "Email Feedback SPSS Exam"
SEND_PAUSE_AFTER = 50
SEND_PAUSE_DURATION = 10
DEBUG_REPLACE_RECIPIENT_EMAIL = None
#DEBUG_REPLACE_RECIPIENT_EMAIL = "ol@limetree.de"


from . import json_settings, defaults
settings = json_settings.JSONSettings(appname=APPNAME.replace(" ", "_").lower(),
                                      settings_file_name="settings.json",
                                      defaults=defaults.SETTINGS)

from .gui import run