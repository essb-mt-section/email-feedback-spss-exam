from .send_mail import DirectSMTP, EmailClient

def process_student(student_id,
                    spss_results,
                    student_ids,
                    email_letter,
                    email_subject,
                    send_mail_object=None):
    """
    send_mail_object: DirectSMTP or EmailClient (if send via local email
    client) otherwise it's a dryrun
    """

    erna, stud_name = student_ids.get(student_id)

    #FIXME logging
    if erna is not None:
        if len(spss_results.get_row(student=erna)) != 1:
            rtn = "WARNING: Can't find <{}> ".format(erna) + \
                  "in SPSS data or id occurs multiple times."
            print(rtn)
            return rtn
        else:
            if stud_name is None:
                body = email_letter.format("student")
            else:
                body = email_letter.format(stud_name)

            body += "\n----\n" + \
                    spss_results.grading_as_markdown(student=erna) + \
                    "\nYour responses\n\n" + \
                    spss_results.data_as_markdown(student=erna) +\
                    "\n----\n"

            to = erna + "@student.eur.nl"
            if isinstance(send_mail_object, (EmailClient, DirectSMTP)):
                send_mail_object.send_mail(recipient_email=to,
                                                subject=email_subject,
                                                body=body)

            return "NAME: {}\nTO: {}\nSUBJECT: {}\n\n".format(
                        stud_name, to, email_subject) +\
                        body
    else: # erna==None
        return stud_name # stud_name contains warning



