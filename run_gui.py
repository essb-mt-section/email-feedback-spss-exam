#!/usr/bin/env python3
"""O. Lindemann"""

if __name__ == "__main__":
    from spss_email_feedback import DirectSMTP, EmailClient
    from spss_email_feedback import gui
    from .config import *

    so = DirectSMTP(smtp_server=SMTP_SERVER,user=USER,
                    sender_address=FROM, password=None)
    so = EmailClient()

    gui.run(email_letter=EMAIL_TXT, email_subject=EMAIL_SUBJECT,
            send_mail_object=so)
