#!/usr/bin/env python3
"""O. Lindemann"""

from os import path
import spss_email_feedback as sef

if __name__ == "__main__":
    ## via python code
    folder = "/home/oliver/science/teaching/44-AMDA/20/results/spss/"
    ids = sef.StudentIDs(file=path.join(folder, "all_students.csv"))
    registrations = sef.Registrations(
        file=path.join(folder, "B44-SPSS-feedback-1.csv"))
    spss_results = sef.SPSSResults(file=path.join(folder,
                            "results_256.csv"), n_questions=20)

    ## single subject
    rtn = sef.process_student(student_id=552324,
                              spss_results=spss_results,
                              student_ids=ids,
                              email_letter=sef.settings.body,
                              email_subject=sef.settings.subject,
                              feedback_answers=sef.settings.feedback_answers,
                              feedback_total_scores=sef.settings.feedback_total_scores,
                              mail_sender=None) # dry run,
    # else send_mail_object=sef.EmailClient() or sef.DirectSMTP(...)

    ## or multiple subjects using registration file
    # for student_id in registrations:
    #    print("Process {0}".format(student_id))
    #    sef.process_student(student_id=student_id,
    #                        spss_results=spss_results,
    #                        student_ids=ids,
    #                        email_letter=sef.settings.body,
    #                        email_subject=sef.settings.subject,
    #                        send_mail_object=None)
