import smtplib
from email.message import EmailMessage

from markdown import markdown
try:
    from mailcomposer import MailComposer
except:
    MailComposer = None

from .spss_results import SPSSResults
from .consts import NAME_PLACE_HOLDER


class SendMailObject(object):
    LABEL = ""

    def __init__(self):
        self.error = False

class DryRun(SendMailObject):
    LABEL = "Dry Run"

    def send_mail(self, recipient_email, subject, body):
        #print("TO: {}\SUBJECT:{}\n{}".format(recipient_email, subject, body))
        pass


class EmailClient(SendMailObject):
    LABEL = "via email client"

    def __init__(self, body_format="html"):
        super().__init__()
        if MailComposer is None:
            self.error = "ERROR: Please install 'mailcomposer' via pip."
        self.body_format = body_format

    def send_mail(self, recipient_email, subject, body):
        """returns error message"""

        if self.error:
            return self.error

        try:
            mc = MailComposer(subject=subject, body_format=self.body_format)
        except:
            self.error =  "ERROR: No email client found"
            return self.error

        mc.to = recipient_email
        txt = markdown(body, extensions=['markdown.extensions.tables'])
        mc.body = txt.replace("\n", "")
        mc.display()

        return self.error


class DirectSMTP(SendMailObject):
    LABEL = "directly via SMTP"

    def __init__(self, smtp_server, user, sender_address, port, reply_to=None,
                    password=None,
                    debug_replace_recipient_email=None):
        super().__init__()
        self.smtp_server = smtp_server
        self.user = user
        self.sender_address = sender_address
        self.password = password
        self.port = port
        if isinstance(reply_to, str) and len(reply_to)>4:
            self.reply_to = reply_to
        else:
            self.reply_to = None
        if isinstance(debug_replace_recipient_email, str):
            self._debug_replace_recipient = debug_replace_recipient_email
        else:
            self._debug_replace_recipient = None
        self._smtp = None

    def log_in(self):
        if self.is_logged_in:
            self.close()

        self._smtp = smtplib.SMTP_SSL(host=self.smtp_server, port=self.port)
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
        """returns error message"""

        if self.error:
            return self.error

        if not self.is_logged_in:
            self.log_in()

        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = self.sender_address
        if self._debug_replace_recipient is not None:
            msg['To'] = self._debug_replace_recipient
        else:
            msg['To'] = recipient_email
        if self.reply_to is not None:
            msg['Reply-To'] = self.reply_to

        body = markdown(body, extensions=[
            'markdown.extensions.tables'])
        msg.set_content(body.replace("\n", ""), subtype="html")
        self._smtp.send_message(msg)

        return self.error

def send_feedback(student_id,
                  spss_results,
                  email_letter,
                  email_subject,
                  feedback_answers,
                  feedback_total_scores,
                  mail_sender=None,
                  redirect_email_address=None):
    """
    send_mail_object: DirectSMTP or EmailClient (if send via local email
    client) otherwise it's a dryrun
    """
    assert(isinstance(spss_results, SPSSResults))
    stud_name = spss_results.get_full_name(student_id)
    if isinstance(redirect_email_address, str):
        email_address = redirect_email_address
    else:
        email_address = spss_results.get_email(student_id)

    if email_address is None:
        rtn = "WARNING: Can't find <{}> ".format(student_id) + \
              "in SPSS data or id occurs multiple times."
        return rtn

    else:
        t = email_letter.upper().find(NAME_PLACE_HOLDER)
        if t>=0:
            email_letter = email_letter[:t] + "{}" +\
                           email_letter[(t+len(NAME_PLACE_HOLDER)):]
        if stud_name is None:
            body = email_letter.format("student")
        else:
            body = email_letter.format(stud_name)

        body += "\n\n----\n"
        if feedback_total_scores:
            body += spss_results.totalscore_as_markdown(student=student_id)
        else:
            body += "Student id: {}".format(student_id)
        if feedback_answers:
            body += "\n\nYour responses\n\n" + \
                spss_results.answers_as_markdown(student=student_id)
        body += "\n----\n"

        error = False
        if isinstance(mail_sender, EmailClient):
            error = mail_sender.send_mail(recipient_email=email_address,
                                  subject=email_subject,
                                  body=body)
        elif isinstance(mail_sender,DirectSMTP):
            try:
                error = mail_sender.send_mail(recipient_email=email_address,
                                  subject=email_subject,
                                  body=body)
            except Exception as e:
                error = "ERROR: Can't send email. {}".format(e)

        if error:
            print(error)
            return error
        else:
            return "NAME: {}\nTO: {}\nSUBJECT: {}\n\n".format(
                    stud_name, email_address, email_subject) +\
                    body