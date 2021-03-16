from os import path
from time import sleep
import re

import PySimpleGUI as _sg
import pandas as pd
from .spss_results import SPSSResults
from .send_mail import DirectSMTP, DryRun, EmailClient, send_feedback
from . import APPNAME, __version__, settings
from .misc import csv2lst, lst2csv, random_element

SEND_PAUSE_AFTER = 50
SEND_PAUSE_DURATION = 10
DEBUG_REPLACE_RECIPIENT_EMAIL = None
#DEBUG_REPLACE_RECIPIENT_EMAIL = "ol@limetree.de"

def run():
    global settings
    mail_sender = DryRun()

    _sg.theme('SystemDefault1')
    layout = []
    input_fl_spss = _sg.InputText("", size=(60, 1), enable_events=True,
                                   key="fl_spss")
    layout.append([_sg.Frame('Result File',
                             [[_sg.Text("SPSS result file (csv):",
                                        size=(20, 1)),
                               input_fl_spss,
                               _sg.FileBrowse(size=(6, 1),
                                        initial_folder = settings.last_folder,
                                        file_types=(("*.csv", "*.csv"),))
                               ]])])

    txt_regs = _sg.Multiline(default_text="", size=(90, 5),
                             key="registrations", enable_events=True)
    txt_n_selected = _sg.Text("", size=(40, 1))
    layout.append([_sg.Frame('Selected student IDs (comma-separated list)',
                             [[txt_regs],
                              [_sg.Button(button_text="clear", key="reg_clear"),
                               _sg.Button(button_text="all", key="reg_all"),
                               _sg.Input(key="reg_file", enable_events=True,
                                         visible=False),
                               _sg.FileBrowse(button_text="from csv file",
                                            target="reg_file",
                                            size=(10, 1),
                                            initial_folder=settings.last_folder,
                                            file_types=(("*.csv","*.csv"),)),
                               txt_n_selected]
                              ]
                             )])

    btn_send = _sg.Button(button_text=mail_sender.LABEL,
                             key="send", size=(20, 2),
                             visible=True)

    layout.append(
        [_sg.Button("View Data", key="view", size=(14, 2)),
         _sg.Button("Email Settings", key="email", size=(14, 2),
                    visible=True),
         btn_send,
         _sg.Cancel(size=(12, 2))]
    )

    window = _sg.Window("{} ({})".format(APPNAME, __version__), layout)
    old_selected = None
    spss_results = None
    test_email_send = False
    while True:
        e, v = window.read(timeout=500)
        window.Refresh()

        if e == "Cancel" or e is None:
            break

        elif e == "fl_spss":
            try:
                spss_results = SPSSResults(file=v["fl_spss"])
            except:
                spss_results = None

            if spss_results is not None and spss_results.is_incomplete:
                _sg.Print("ERROR: {} is not usable result csv file.\n "
                          "".format(spss_results.filename),
                          "\nThe following columns are missing in the "
                          "data file:", str(spss_results.missing_columns),
                          "\n\nPlease use the export function **with "
                          "details advanced** and selected all "
                          "file additional variables.\n\n(c) Oliver "
                          "Lindemann")
                spss_results = None
                input_fl_spss.update(value="")

        elif e == "view":
            if spss_results is not None:
                _sg.Print("Data\n", spss_results.df, "\n")
                _sg.Print(spss_results.overview())

        elif e == "reg_file":
            lst = registration_file_window(v["reg_file"])
            txt_regs.update(value=lst2csv(lst))

        elif e == "reg_clear":
            txt_regs.update(value="")

        elif e == "reg_all":
            if spss_results is not None:
                txt_regs.update(value=lst2csv(spss_results.student_ids))

        elif e == "email":
            settings, mail_sender = settings_window(settings, mail_sender)
            if isinstance(mail_sender, DirectSMTP):
                log("Connecting to SMTP server {}".format(
                    mail_sender.smtp_server))
                try:
                    mail_sender.log_in()
                    log("Login succeeded! You are ready to go.")
                    mail_sender.close()
                except Exception as e:
                    log("\nERROR {}\n\nI can't log in to the SMTP "
                              "server. "
                              "Please check settings and password.".format(e))
                    mail_sender = DryRun()

            if isinstance(mail_sender, DryRun):
                btn_send.update(text=mail_sender.LABEL)
            else:
                btn_send.update(text="send " + mail_sender.LABEL)


        elif e == "send":
            regs = csv2lst(txt_regs.get())
            if spss_results is None:
                _sg.popup_ok("No SPSS result file")
                continue

            if isinstance(mail_sender, (EmailClient, DirectSMTP)) and\
                                len(regs)>0:

                if isinstance(mail_sender, DirectSMTP) and not test_email_send:
                    adress = test_email_address()
                    if adress is not None:
                        # SEND TEST EMAIL
                        log("\nTest Email: {0}".format(adress))
                        stud_id = random_element(spss_results.student_ids)
                        fb = send_feedback(student_id=stud_id,
                                           spss_results=spss_results,
                                           email_letter=settings.body,
                                           email_subject=settings.subject,
                                           feedback_answers=settings.feedback_answers,
                                           feedback_total_scores=settings.feedback_total_scores,
                                           mail_sender=mail_sender,
                                           redirect_email_address=adress)
                        log(fb)
                        test_email_send = True
                        continue

                if not caution_window("Do you really want to send {} "
                                  "emails {}?".format(len(regs),
                                                      mail_sender.LABEL)):
                    continue

            if len(regs) >= 1:
                test_email_send = True
                # TODO quitting send process manual break
                for cnt, stud_id in enumerate(regs):
                    log("\nProcess {0}".format(stud_id))
                    fb = send_feedback(student_id=stud_id,
                                       spss_results=spss_results,
                                       email_letter=settings.body,
                                       email_subject=settings.subject,
                                       feedback_answers=settings.feedback_answers,
                                       feedback_total_scores=settings.feedback_total_scores,
                                       mail_sender=mail_sender)

                    if isinstance(mail_sender, (DryRun, DirectSMTP)):
                        if cnt>=1:
                            # shorten feedback
                            log(fb.split("\n")[0])
                            #gui_log("...")
                        else:
                            log(fb)
                        if fb.startswith("WARNING"):
                            log("-" * 80 + "\n")
                        if fb.startswith("ERROR"):
                            log("-" * 80 + "\n")
                            break # END LOOP

                        if isinstance(mail_sender, (DirectSMTP, DryRun)):
                            if cnt % SEND_PAUSE_AFTER==(SEND_PAUSE_AFTER-1):
                                log("\n** Pause sending for {} seconds." 
                                          "**".format(SEND_PAUSE_DURATION))

                                for x in range(SEND_PAUSE_DURATION*10):
                                    window.Refresh()
                                    sleep(1/10)

                log("** DONE! **")

            else:
                _sg.popup_ok("No student IDs selected!")

        elif e == "__TIMEOUT__":
            if txt_regs.get() != old_selected:
                old_selected = txt_regs.get()
                lst = csv2lst(old_selected)
                txt_n_selected.update(value="Selected: {}".format(len(lst)))

    if isinstance(mail_sender, DirectSMTP) and \
            mail_sender.is_logged_in:
        mail_sender.close()

    try:
        if path.isfile(v["fl_spss"]):
            settings.last_folder = path.split(v["fl_spss"])[0]
    except:
        pass

    window.close()
    settings.save()
    return


def log(txt):
    for l in str(txt).split("\n"):
        _sg.Print(l)
        # TODO timestamps log_file

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


