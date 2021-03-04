__author__  = "Oliver Lindemann"
__version__ = "0.3"

import os
import json
from copy import copy
from appdirs import user_config_dir

class JSONSettings():

    def __init__(self, appname, settings_file_name, defaults):
        """General settings class that saves the settings in a json file.
        If no config file exists it will be created.
        The variables (fields) can be access a properties of the Settings object.

        Changes DEFAULTS to defined the required settings and their defaults.
        """

        self.config_dir = user_config_dir(appname=appname)
        try:
            os.mkdir(self.config_dir)
        except:
            pass
        self.settings_file = os.path.join(self.config_dir, settings_file_name)

        try: #load
            with open(self.settings_file, 'r') as fl:
                settings = json.load(fl)
            saving_required = False
        except:
            settings = defaults
            saving_required = True

        # check all defauls
        for k in defaults:
            if k not in settings:
                settings[k] = defaults[k]
                saving_required = True

        self._fields = settings.keys()
        self.__dict__.update(settings)

        if saving_required:
            self.save()

    def get_dict(self):
        return self.__dict__

    def save(self):
        d = copy(self.__dict__)
        try:
            d.pop("_fields")
        except:
            pass
        try:
            d.pop("settings_file")
        except:
            pass
        try:
            d.pop("config_dir")
        except:
            pass

        with open(self.settings_file, 'w') as fl:
            fl.write(json.dumps(d, indent = 2))
