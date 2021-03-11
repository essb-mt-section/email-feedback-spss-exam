import smtplib
from email.message import EmailMessage

from markdown import markdown
try:
    from mailcomposer import MailComposer
except:
    MailComposer = None

from .spss_results import SPSSResults

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

    def __init__(self, smtp_server, user, sender_address, password=None,
                 debug_replace_recipient_email=None):
        self.smtp_server = smtp_server
        self.user = user
        self.sender_address = sender_address
        self.password = password
        if isinstance(debug_replace_recipient_email, str):
            self._debug_replace_recipient = debug_replace_recipient_email
        else:
            self._debug_replace_recipient = None
        self._smtp = None

    def log_in(self):
        if self.is_logged_in:
            self.close()

        self._smtp = smtplib.SMTP(host=self.smtp_server, port=587)
        self._smtp.ehlo()
        self._smtp.starttls()
        self._smtp.login(self.user, self.password)

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
        if self._debug_replace_recipient is not None:
            msg['To'] = self._debug_replace_recipient
        else:
            msg['To'] = recipient_email

        body = markdown(body, extensions=[
            'markdown.extensions.tables'])
        msg.set_content(body.replace("\n", ""), subtype="html")
        self._smtp.send_message(msg)


def send_feedback(student_id,
                  spss_results,
                  email_letter,
                  email_subject,
                  feedback_answers,
                  feedback_total_scores,
                  mail_sender=None):
    """
    send_mail_object: DirectSMTP or EmailClient (if send via local email
    client) otherwise it's a dryrun
    """
    assert(isinstance(spss_results, SPSSResults))
    stud_name = spss_results.get_full_name(student_id)
    email_address = spss_results.get_email(student_id)

    if email_address is None:
        rtn = "WARNING: Can't find <{}> ".format(student_id) + \
              "in SPSS data or id occurs multiple times."
        print(rtn)
        return rtn
    else:
        if stud_name is None:
            body = email_letter.format("student")
        else:
            body = email_letter.format(stud_name)

        body += "\n----\n"
        if feedback_total_scores:
            body += spss_results.totalscore_as_markdown(student=student_id)
        else:
            body += "Student id: {}".format(student_id)
        if feedback_answers:
            body += "\n\nYour responses\n\n" + \
                spss_results.answers_as_markdown(student=student_id)
        body += "\n----\n"

        if isinstance(mail_sender, EmailClient):
            mail_sender.send_mail(recipient_email=email_address,
                                  subject=email_subject,
                                  body=body)

        elif isinstance(mail_sender,DirectSMTP):

            try:
                mail_sender.send_mail(recipient_email=email_address,
                                  subject=email_subject,
                                  body=body)
            except Exception as e:
                rtn = "ERROR: Can't send email. {}".format(e)
                print(rtn)
                return rtn

        return "NAME: {}\nTO: {}\nSUBJECT: {}\n\n".format(
                    stud_name, email_address, email_subject) +\
                    body