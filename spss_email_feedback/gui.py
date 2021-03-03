import PySimpleGUI as _sg

from .data_files import SPSSResults, StudentIDs, Registrations
from .process import process_student
from .send_mail import EmailClient, DirectSMTP


def run(email_letter, email_subject, send_mail_object):
    _sg.theme('SystemDefault1')
    layout = []
    layout.append([_sg.Frame('Files',
                             [[_sg.Text("All student IDs (tsv):", size=(20,
                                                                         1)),
                               _sg.InputText(
                                   "", size=(60, 1),
                                   key="fl_student_id"),
                               _sg.FileBrowse(size=(6, 1))],
                              [_sg.Text("SPSS result file (csv):", size=(20,
                                                                         1)),
                               _sg.InputText(
                                   "", size=(60, 1),
                                   key="fl_spss"),
                               _sg.FileBrowse(size=(6, 1), file_types=(("*.csv",
                                                                        "*.csv"),))
                               ]])])

    layout.append([_sg.Frame('For which students?',
                             [[_sg.Text("Registration file (csv):", size=(20,
                                                                         1)),
                               _sg.InputText(
                                   "", size=(60, 1),
                                   key="fl_registrations"),
                               _sg.FileBrowse(size=(6, 1), file_types=(("*.csv",
                                                                        "*.csv"),))],
                              [_sg.Text("or single student ID:", size=(20, 1)),
                               _sg.InputText(
                                   "", size=(10, 1), key="single_id")]]
                             )])

    layout.append(
        [_sg.Button("View Data", key="view", size=(24, 2)),
         _sg.Checkbox('Dry Run', key="dryrun", default=True,
                      size=(10, 1)),
         _sg.Button("Send Feedback", key="send", size=(24, 2)),
         _sg.Cancel(size=(12, 2))]
    )

    window = _sg.Window('SPSS Email feedback'.format(), layout)

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
                _sg.Print("\n\nRegistrations\n", registrations.df)

        elif e == "send":
            single_id = v["single_id"]
            if v["dryrun"]:
                current_mail_object = None
            else:
                current_mail_object = send_mail_object
                if isinstance(send_mail_object, DirectSMTP) and \
                    send_mail_object.password is None:
                    pass # FIXME define password

            if len(single_id) > 1:
                fb = process_student(student_id=single_id,
                                     spss_results=spss_results,
                                     student_ids=ids,
                                     email_letter=email_letter,
                                     email_subject=email_subject,
                                     send_mail_object=current_mail_object)
                if v["dryrun"]:
                    _sg.Print(fb) # TODO always output
                    #todo maybe loggin here

            elif registrations is not None:
                for stud_id, reg_name in registrations:
                    _sg.Print("\nProcess {0} ({1})".format(stud_id, reg_name))
                    fb = process_student(student_id=stud_id,
                                         spss_results=spss_results,
                                         student_ids=ids,
                                         email_letter=email_letter,
                                         email_subject=email_subject,
                                         send_mail_object=current_mail_object)

                    if v["dryrun"]:
                        _sg.Print(fb[:50])
                        if fb.startswith("WARNING"):
                            _sg.Print("-"*80+"\n")
                        elif len(fb) > 50:
                            _sg.Print("...")



        else:
            break

    if isinstance(send_mail_object, DirectSMTP) and \
            send_mail_object.is_logged_in:
        send_mail_object.close()

    window.close()
    return
