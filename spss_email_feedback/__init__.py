__version__ = "0.5"
__author__ = "Oliver Lindemann"

from .data_files import Registrations, StudentIDs, SPSSResults
from .process import process_student
from .send_mail import DirectSMTP, EmailClient
