#!/usr/bin/env python3
"""O. Lindemann"""

EMAIL_SUBJECT = "SPSS Feedback"
EMAIL_TXT = """Dear {},

This email is the feedback for your SPSS exam. The table below contains all 
responses you gave and the correct answers.

<i>Explanation</i>

* Questions 01-09 were about multiple regression
* Questions 10-16 were about ANOVA
* Questions 17-20 were about repeated measures ANOVA
* total_score:  Total number of correct answers
* 'nan' means that no answer was registered

Oliver Lindemann
"""

FROM = "lindemann@essb.eur.nl"
USER = "63596oli@eur.nl"
SMTP_SERVER = "smtp.office365.com"

if __name__ == "__main__":
    from spss_email_feedback import DirectSMTP, EmailClient
    from spss_email_feedback import gui

    so = DirectSMTP(smtp_server=SMTP_SERVER,user=USER,
                    sender_address=FROM, password=None)
    so = EmailClient()

    gui.run(email_letter=EMAIL_TXT, email_subject=EMAIL_SUBJECT,
            send_mail_object = so )
