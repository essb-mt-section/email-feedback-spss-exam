__version__ = "0.6.5"
__author__ = "Oliver Lindemann"

APPNAME = "SPSS email feedback"
from . import _json_settings, _defaults
from ._send_mail import DirectSMTP, EmailClient, DryRun
from ._main import process_student, Registrations, StudentIDs, SPSSResults

settings = _json_settings.JSONSettings(appname=APPNAME.replace(" ","_"),
                                       settings_file_name="settings.json",
                                       defaults=_defaults.SETTINGS)
