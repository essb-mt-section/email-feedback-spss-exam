from os import path
import PySimpleGUI as _sg

from ._main import SPSSResults, StudentIDs, Registrations, process_student
from ._send_mail import DirectSMTP, DryRun, EmailClient
from . import APPNAME, __version__, settings

def run():
    global settings
    mail_sender = DryRun()

    _sg.theme('SystemDefault1')
    layout = []
    layout.append([_sg.Frame('Files',
                             [[_sg.Text("All student IDs (tsv):", size=(20,
                                                                         1)),
                               _sg.InputText(
                                   "", size=(60, 1),
                                   key="fl_student_id"),
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

    layout.append([_sg.Frame('For which student(s)?',
                             [[_sg.Text("Single student ID:", size=(20, 1)),
                               _sg.InputText(
                                   "", size=(10, 1), key="single_id")],
                              [_sg.Text("or registration file (csv):", size=(20,
                                                                         1)),
                               _sg.InputText(
                                   "", size=(60, 1),
                                   key="fl_registrations"),
                               _sg.FileBrowse(size=(6, 1),
                                            initial_folder=settings.last_folder,
                                            file_types=(("*.csv","*.csv"),))
                            ]]
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

    while True:
        e, v = window.read()
        window.Refresh()

        if e == "Cancel":
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

        try:
            registrations = Registrations(file=v["fl_registrations"])
        except:
            registrations = None

        if e == "view":
            if ids is not None:
                _sg.Print("Student IDs\n", ids.df)
            if spss_results is not None:
                _sg.Print("\n\nSPSS results\n", spss_results.df)
            if registrations is not None:
                _sg.Print("\n\nRegistrations\n", registrations.ids)

        elif e == "email":
            settings, mail_sender = settings_window(settings, mail_sender)
            if isinstance(mail_sender, DryRun):
                send_button.update(text=mail_sender.LABEL)
            else:
                send_button.update(text="send " + mail_sender.LABEL)

        elif e == "send":
            single_id = v["single_id"]

            dryrun = isinstance(mail_sender, DryRun)
            if len(single_id) > 1:
                fb = process_student(student_id=single_id,
                                     spss_results=spss_results,
                                     student_ids=ids,
                                     email_letter=settings.body,
                                     email_subject=settings.subject,
                                     mail_sender=mail_sender)
                if dryrun:
                    _sg.Print(fb) # TODO always output
                    #todo maybe loggin here

            elif registrations is not None:
                for stud_id in registrations:
                    _sg.Print("\nProcess {0}".format(stud_id))
                    fb = process_student(student_id=stud_id,
                                         spss_results=spss_results,
                                         student_ids=ids,
                                         email_letter=settings.body,
                                         email_subject=settings.subject,
                                         mail_sender=mail_sender)

                    if dryrun:
                        _sg.Print(fb[:50])
                        if fb.startswith("WARNING"):
                            _sg.Print("-"*80+"\n")
                        elif len(fb) > 50:
                            _sg.Print("...")



        else:
            break

    if isinstance(mail_sender, DirectSMTP) and \
            mail_sender.is_logged_in:
        mail_sender.close()

    if path.isfile(v["fl_spss"]):
        settings.last_folder = path.split(v["fl_spss"])[0]

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
                                   key="body")]
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
                        "smtp_server"]:
                if key == "body":
                    values[key].strip() + "\n"
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