#!/usr/bin/env python3
"""O. Lindemann"""

if __name__ == "__main__":
    import spss_email_feedback as sef
    from spss_email_feedback import gui

    if sef.settings.direct_smtp:
        so = sef.DirectSMTP(smtp_server=sef.settings.smtp_server,
                                   user=sef.settings.user,
                                   sender_address=sef.settings.sender_email,
                                   password=None)
    else:
        so = sef.EmailClient()

    gui.run(email_letter=sef.settings.body,
            email_subject=sef.settings.subject,
            send_mail_object=so)
