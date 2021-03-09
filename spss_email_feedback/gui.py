from os import path
import PySimpleGUI as _sg
import pandas as pd
from .main import SPSSResults, StudentIDs, process_student
from .send_mail import DirectSMTP, DryRun, EmailClient
from . import APPNAME, __version__, settings
from .misc import csv2lst, lst2csv

def run():
    global settings
    mail_sender = DryRun()

    _sg.theme('SystemDefault1')
    layout = []
    layout.append([_sg.Frame('Files',
                             [[_sg.Text("All student IDs (csv):", size=(20,1)),
                               _sg.InputText(
                                   "", size=(60, 1),
                                   key='fl_student_id'),
                               _sg.FileBrowse(size=(6, 1),
                                              initial_folder = settings.last_folder)],
                              [_sg.Text("SPSS result file (csv):", size=(20,
                                                                         1)),
                               _sg.InputText(
                                   "", size=(60, 1),
                                   key="fl_spss"),
                               _sg.FileBrowse(size=(6, 1),
                                        initial_folder = settings.last_folder,
                                        file_types=(("*.csv", "*.csv"),))
                               ]])])

    txt_regs = _sg.Multiline(default_text="", size=(90, 5),
                             key="registrations", enable_events=True)
    txt_n_selected = _sg.Text("", size=(40, 1))
    layout.append([_sg.Frame('Selected student(s) (comma-separated list)',
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

    send_button = _sg.Button(button_text=mail_sender.LABEL,
                             key="send", size=(20, 2),
                             visible=True)

    layout.append(
        [_sg.Button("View Data", key="view", size=(14, 2)),
         _sg.Button("Email Settings", key="email", size=(14, 2),
                    visible=True),
         send_button,
         _sg.Cancel(size=(12, 2))]
    )

    window = _sg.Window("{} ({})".format(APPNAME, __version__), layout)
    old_selected = None
    while True:
        e, v = window.read(timeout=500)
        window.Refresh()

        if e == "Cancel" or e is None:
            break

        try:
            ids = StudentIDs(file=v["fl_student_id"])
        except:
            ids = None

        try:
            spss_results = SPSSResults(file=v["fl_spss"],
                                       n_questions=20)
        except:
            spss_results = None


        if e == "view":
            if ids is not None:
                _sg.Print("Student IDs\n", ids.df)
            if spss_results is not None:
                _sg.Print("\n\nSPSS results\n", spss_results.df)

        elif e == "reg_file":
            lst = registration_file_window(v["reg_file"])
            txt_regs.update(value=lst2csv(lst))

        elif e == "reg_clear":
            txt_regs.update(value="")

        elif e == "reg_all":
            if ids is not None:
                txt_regs.update(value=lst2csv(ids.ids))


        elif e == "email":
            settings, mail_sender = settings_window(settings, mail_sender)
            if isinstance(mail_sender, DryRun):
                send_button.update(text=mail_sender.LABEL)
            else:
                send_button.update(text="send " + mail_sender.LABEL)

        elif e == "send":
            regs = csv2lst(txt_regs.get())
            dryrun = isinstance(mail_sender, DryRun)
            if len(regs) == 1:
                fb = process_student(student_id=regs[0],
                                     spss_results=spss_results,
                                     student_ids=ids,
                                     email_letter=settings.body,
                                     email_subject=settings.subject,
                                     feedback_answers=settings.feedback_answers,
                                     feedback_total_scores=settings.feedback_total_scores,
                                     mail_sender=mail_sender)
                if dryrun:
                    _sg.Print(fb) # TODO always output
                    #todo maybe loggin here

            elif len(regs) >1:
                for stud_id in regs:
                    _sg.Print("\nProcess {0}".format(stud_id))
                    fb = process_student(student_id=stud_id,
                                         spss_results=spss_results,
                                         student_ids=ids,
                                         email_letter=settings.body,
                                         email_subject=settings.subject,
                                         feedback_answers=settings.feedback_answers,
                                         feedback_total_scores=settings.feedback_total_scores,
                                         mail_sender=mail_sender)

                    if dryrun:
                        _sg.Print(fb[:50])
                        if fb.startswith("WARNING"):
                            _sg.Print("-"*80+"\n")
                        elif len(fb) > 50:
                            _sg.Print("...")

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

def _entry(text, key, settings_dict):
    return [_sg.Text(text +":", size=(10, 1)),
            _sg.InputText(settings_dict[key], size=(40, 1), key=key)]


def settings_window(settings, mail_sender):
    _sg.theme('SystemDefault1')
    send_types = [DryRun.LABEL, EmailClient.LABEL, DirectSMTP.LABEL]
    layout = []
    s_dict = settings.get_dict()
    try:
        default_passwd = mail_sender.password
    except:
        default_passwd = ""

    layout.append([_sg.Frame('Email:',
                   [[_sg.Text("Type: ", size=(10, 1)),
                     _sg.Combo(send_types,key="send_type",
                                         default_value=mail_sender.LABEL) ],
                    _entry("Subject", "subject", s_dict),
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


    layout.append([_sg.Frame('SMTP Settings',
                   [_entry("Server", "smtp_server", s_dict),
                    _entry("User", "user", s_dict),
                    [_sg.Text("Password", size=(10, 1)),
                     _sg.Input(size=(40,1), default_text=default_passwd,
                               key='passwd',  password_char='*')]
                    ]),
                   _sg.Save(size=(10,2)), _sg.Cancel(size=(10,2))
                   ])

    window =  _sg.Window('ForceGUI {}: Settings'.format(__version__), layout)

    while True:
        event, values = window.read()

        if event=="Save":

            for key in ["body", "subject", "sender_email", "user",
                        "smtp_server", "feedback_answers", "feedback_total_scores"]:
                if key == "body":
                    values[key] = values[key].strip() + "\n"
                s_dict[key] = values[key]
            settings.save()

            if values["send_type"] == DryRun.LABEL:
                mail_sender = DryRun()
                break

            elif values["send_type"] == EmailClient.LABEL:
                mail_sender = EmailClient()
                break

            elif values["send_type"] == DirectSMTP.LABEL:
                if len(values["passwd"])==0:
                    _sg.popup('Please enter a SMTP password!')
                else:
                    mail_sender = DirectSMTP(smtp_server=settings.smtp_server,
                                       user=settings.user,
                                       sender_address=settings.sender_email,
                                       password=values["passwd"])
                    break
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


