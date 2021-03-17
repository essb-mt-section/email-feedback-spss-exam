from os import path
import re

import PySimpleGUI as _sg
import pandas as pd
from .send_mail import DirectSMTP, DryRun, EmailClient
from . import  APPNAME, __version__, __author__, DEBUG_REPLACE_RECIPIENT_EMAIL
from .log import get_log_file


def _entry(text, key, settings_dict):
    return [_sg.Text(text +":", size=(10, 1)),
            _sg.InputText(settings_dict[key], size=(40, 1), key=key)]

def caution_window(message):
    _sg.theme('DarkRed1')
    rtn = _sg.popup_yes_no(message, title="Caution")=="Yes"
    _sg.theme('SystemDefault1')
    return rtn


def test_email_address():

    _sg.theme('SystemDefault1')
    yes = _sg.Button("Yes", size=(20,2), key="yes", disabled=True)
    layout = [[_sg.Text("To:", size=(3, 1)),
            _sg.InputText("", size=(40, 1), key="address", enable_events=True)],
            [_sg.Text("Send a test email to the email address?")],
            [yes, _sg.Button("No", size=(10,2), key="no")]]
    win = _sg.Window('Sending Test Email'.format(__version__), layout)

    vaild_email = re.compile(r"[^@]+@[^@]+\.[^@]+")
    while True:
        event, values = win.read()
        win.refresh()

        if event == "address":
            invalid = vaild_email.match(values["address"]) is None
            yes.update(disabled=invalid)
            continue
        elif event == "yes":
            rtn = values["address"]
            break
        rtn = None
        break

    win.close()
    return rtn

def settings_window(settings, mail_sender):
    _sg.theme('SystemDefault1')
    #send_type = (DryRun, EmailClient, DirectSMTP)
    layout = []
    s_dict = settings.get_dict()
    try:
        default_passwd = mail_sender.password
    except:
        default_passwd = ""

    rd_dryrun = _sg.Radio(DryRun.LABEL, "RADIO1", enable_events=True,
              default=isinstance(mail_sender, DryRun))
    rd_client = _sg.Radio(EmailClient.LABEL, "RADIO1", enable_events=True,
                               default=isinstance(mail_sender, EmailClient))
    rd_smtp =_sg.Radio(DirectSMTP.LABEL, "RADIO1", enable_events=True,
              default=isinstance(mail_sender, DirectSMTP))

    layout.append([_sg.Frame('Email:',
                   [_entry("Subject", "subject", s_dict),
                    _entry("Sender", "sender_email", s_dict),
                    [_sg.Multiline(default_text=s_dict["body"],
                                   size=(80, 15),
                                   key="body")],
                    [_sg.Checkbox("Feedback total scores",
                                  key="feedback_total_scores",
                                  default=s_dict["feedback_total_scores"]),
                     _sg.Checkbox("Feedback all answers",
                                  key="feedback_answers",
                                  default=s_dict["feedback_answers"])]
                    ])])

    frame_smtp_settings = _sg.Frame('SMTP Settings',
                   [_entry("Server", "smtp_server", s_dict),
                    _entry("User", "user", s_dict),
                    [_sg.Text("Password", size=(10, 1)),
                     _sg.Input(size=(40,1), default_text=default_passwd,
                               key='passwd',  password_char='*')]
                    ], visible=isinstance(mail_sender, DirectSMTP))
    layout.append([frame_smtp_settings])
    layout.append([_sg.Frame('Type:', [[rd_dryrun, rd_client, rd_smtp]]),
                   _sg.Save(size=(10,2)), _sg.Cancel(size=(10,2))])

    window =  _sg.Window('Email Settings'.format(__version__), layout)

    while True:
        event, values = window.read()
        if event=="Save":

            for key in ["body", "subject", "sender_email", "user",
                        "smtp_server", "feedback_answers", "feedback_total_scores"]:
                if key == "body":
                    values[key] = values[key].strip() + "\n"
                s_dict[key] = values[key]
            settings.save()

            if rd_dryrun.get():
                mail_sender = DryRun()
                break

            elif rd_client.get():
                mail_sender = EmailClient()
                break

            elif rd_smtp.get():
                if len(values["passwd"])==0:
                    _sg.popup('Please enter a SMTP password!')
                else:
                    mail_sender = DirectSMTP(smtp_server=settings.smtp_server,
                               user=settings.user,
                               sender_address=settings.sender_email,
                               password=values["passwd"],
                               debug_replace_recipient_email=
                                                 DEBUG_REPLACE_RECIPIENT_EMAIL)
                    break
        elif isinstance(event, int): # change of ratio button
            frame_smtp_settings.update(visible=rd_smtp.get())

        else:
            break

    window.close()
    return settings, mail_sender


def registration_file_window(reg_file):
    _sg.theme('SystemDefault1')
    df = pd.read_csv(reg_file, sep=",")

    layout = [[_sg.Frame('{}'.format(path.split(reg_file)[1]), [
        [_sg.Text("Select ID column:", size=(15, 1)),
         _sg.Combo(values=list(df.columns), size=(10, 1),
                   key="column")]])],
              [_sg.OK(size=(10, 1))]
              ]

    window = _sg.Window("Registration file", layout)
    e, v = window.read()
    window.close()
    try:
        return list(df.loc[:, v["column"]])
    except:
        return None

def log_window():
    log_file = get_log_file()
    with open(log_file) as f:
        lines = f.readlines()

    _sg.theme('SystemDefault1')
    info = "{}, Version {}, (c) {}".format(APPNAME, __version__, __author__)
    layout = [[_sg.Text(log_file)],
              [_sg.Multiline("".join(lines), size=(80, 50))],
              [_sg.Button("Delete Log", key="delete", size=(10,2) ),
               _sg.CloseButton("Close", size=(20,2))]]
    window = _sg.Window(info, layout)

    while True:
        e, v = window.read()
        if e=="delete":
            # Open the file with writing permission
            myfile = open(log_file, 'w')
            myfile.close()
        break

    window.close()
