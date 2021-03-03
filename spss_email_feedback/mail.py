from mailcomposer import MailComposer

def _replace_multi_spaces(txt, replace_str):
    rtn = ""
    n_spaces = 0
    for x in txt:
        if x != " ":
            if n_spaces>0:
                if n_spaces == 1:
                    rtn += " "
                else:
                    rtn += replace_str*n_spaces
                n_spaces = 0
            rtn += x
        else:
            n_spaces += 1
    return rtn


def email_body(spss_feedback, letter, name=None, replace_spaces=False,
               replace_str="&nbsp;"):
    if name is None:
        rtn = letter.format("student")
    else:
        rtn = letter.format(name)

    rtn += "\n" + spss_feedback

    if replace_spaces:
        rtn = _replace_multi_spaces(rtn, replace_str=replace_str)
    return(rtn)


def send_email(to, subject, body):
    mc = MailComposer(subject=subject, body_format="html")
    mc.to = to
    mc.body = body
    mc.display()


def process_student(student_id,
                    spss_results,
                    student_ids,
                    email_letter,
                    email_subject,
                    dryrun=True):

    erna, stud_name = student_ids.get(student_id)

    #TODO logging
    if erna is not None:
        if len(spss_results.get_row(student=erna)) != 1:
            rtn = "WARNING: Can't find <{}> ".format(erna) + \
                  "in SPSS data or id occurs multiple times."
            print(rtn)
            return rtn
        else:
            feedback = spss_results.grading_as_text(student=erna, tt=True) + \
                       "\n\n" + \
                       spss_results.data_as_text(student=erna, tt=True)

            body = email_body(feedback, letter=email_letter,
                                   name=stud_name,
                                   replace_spaces=not dryrun)
            to = erna + "@student.eur.nl"
            if not dryrun:
                send_email(to=to, subject=email_subject,
                                body=body)
            else:
                return "NAME: {}\nTO: {}\nSUBJECT: {}\n\n".format(
                            stud_name, to, email_subject) +\
                        body
    else: # erna==NOne
        return stud_name # stud_name contians warning



