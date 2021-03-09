import smtplib
from email.message import EmailMessage

from markdown import markdown

try:
    from mailcomposer import MailComposer
except:
    MailComposer = None


class DryRun(object):
    LABEL = "Dry Run"

    def send_mail(self, recipient_email, subject, body):
        #print("TO: {}\SUBJECT:{}\n{}".format(recipient_email, subject, body))
        pass


class EmailClient(object):
    LABEL = "via email client"
    def __init__(self, body_format="html"):
        if MailComposer is None:
            raise RuntimeError("Please install 'mailcomposer' via pip")
        self.body_format = body_format

    def send_mail(self, recipient_email, subject, body):
        mc = MailComposer(subject=subject, body_format=self.body_format)
        mc.to = recipient_email
        txt = markdown(body, extensions=['markdown.extensions.tables'])
        mc.body = txt.replace("\n", "")
        mc.display()

class DirectSMTP(object):
    LABEL = "directly via SMTP"

    def __init__(self, smtp_server, user, sender_address, password=None):
        self.smtp_server = smtp_server
        self.user = user
        self.sender_address = sender_address
        self.password = password
        self._smtp = None

    def log_in(self):
        if self.is_logged_in:
            self.close()

        self._smtp = smtplib.SMTP(host=self.smtp_server, port=587)
        self._smtp.ehlo()
        self._smtp.starttls()
        try:
            self._smtp.login(self.user, self.password)
        except:
            raise IOError("Can't log in. Password might be incorrect or not "
                          "set.")

    @property
    def is_logged_in(self):
        return self._smtp is not None

    def close(self):
        if self._smtp is not None:
            self._smtp.close()
        self._smtp = None

    def __del__(self):
        self.close()

    def send_mail(self, recipient_email, subject, body):
        if not self.is_logged_in:
            self.log_in()

        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = self.sender_address
        msg['To'] = recipient_email
        msg.set_content(markdown(body), subtype="html")
        self._smtp.send_message(msg)
