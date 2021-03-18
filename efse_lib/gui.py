from os import path
from time import sleep

import PySimpleGUI as _sg
from .spss_results import SPSSResults
from .send_mail import DirectSMTP, DryRun, EmailClient, send_feedback
from . import  __version__, settings
from .const import APPNAME, SEND_PAUSE_DURATION, SEND_PAUSE_AFTER
from .misc import csv2lst, lst2csv, random_element
from .log import log, init_logging
from .windows import log_window, registration_file_window, \
    test_email_address, caution_window, settings_window

def run():
    global settings
    mail_sender = DryRun()

    init_logging()
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

    btn_frame_view = _sg.Frame('View',
        [[_sg.Button("Data", key="view", size=(8, 1))],
         [_sg.Button("Log", key="view_log", size=(8, 1))]])

    btn_send = _sg.Button(button_text=mail_sender.LABEL,
                             key="send", size=(15, 3),
                             visible=True)
    btn_frame_email = _sg.Frame('Send Email', [
        [_sg.Button("Email Settings", key="email", size=(15, 3), visible=True),
         btn_send, _sg.Cancel(size=(15,3))]])

    layout.append([btn_frame_view,
         _sg.Text(' '*29),
         btn_frame_email])

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
                          "additional variables.\n\n(c) Oliver "
                          "Lindemann")
                spss_results = None
                input_fl_spss.update(value="")

            else:
                log("Load SPSS file {}".format(v["fl_spss"]), gui_log=False)

        elif e == "view":
            if spss_results is not None:
                _sg.Print("Data\n", spss_results.df, "\n")
                _sg.Print(spss_results.overview())

        elif e == "view_log":
            log_window()

        elif e == "reg_file":
            lst = registration_file_window(v["reg_file"])
            if lst is not None:
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
                        if fb.startswith("ERROR"):
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
