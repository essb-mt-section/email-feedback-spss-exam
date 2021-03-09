import pandas as pd

from .misc import MarkdownTable
from .send_mail import DirectSMTP, EmailClient

class StudentIDs(object):
    def __init__(self, file):
        """A list of all student IDs and Student names as tsv with column
        "name" and "id"

        :param col_names: defines column names. To use first row as column
                        names, set col_names=None
        """

        REQUIRED_COLS =  ['id', 'name']
        try:
            df = pd.read_csv(file, sep=",")
            self.df = df[REQUIRED_COLS]
        except:
            try:
                df = pd.read_csv(file, sep="\t")
                self.df = df[REQUIRED_COLS]
            except:
                raise RuntimeError("Student ID file not in good shape.")


    def find_id(self, the_id):
        """returns indices
        """

        str_id = str(the_id)[:8].lower() # erna if email
        idx = []
        for c, x in enumerate(self.df['id']):
            if x.find(str_id)>-1:
                idx.append(c)
        return idx

    def get(self, the_id):
        """returns (id, name) or (None, warning text)
        """

        idx = self.find_id(the_id)
        if len(idx) == 1:
            return (self.df.loc[idx[0]]['id'],
                    self.df.loc[idx[0]]['name'])
        else:
            if len(idx) == 0:
                warn = "WARNING: Can't find {} in student IDs .".format(the_id)
            else:
                warn = "WARNING: Found {} multiple ({}) time in student " +\
                      "IDs.".format(the_id, len(idx))
            print(warn)
            return None, warn

    @property
    def ids(self):
        return self.df['id']

    @property
    def names(self):
        return self.df['names']

class SPSSResults(object):

    def __init__(self, file):
        """Reading SPSS of the webteam,
        export csv with details
        """

        self.df = pd.read_csv(file, sep=";", dtype=str)
        self.n_questions = 0
        for x in self.df.columns:
            if x.endswith("vraag") and x.startswith("v_"):
                self.n_questions += 1

    def get_row(self, student):
        student = str(student)[:6] # erna without letters
        return self.df.loc[self.df['student'] == student]

    def get_score(self, student):
        row = self.get_row(student)
        if len(row) == 0:
            return None
        else:
            return int(row["totaal"])

    def grade_from_score(self, score, guessing_score=0, max_grade=10,
                         ndigits=1):
        return (round((score - guessing_score) /
                      (self.n_questions - guessing_score) * max_grade,
                      ndigits=ndigits))


    def get_answers(self, student):
        row = self.get_row(student)
        if len(row) == 0:
            return None

        dd =  row.to_dict(orient="list")
        data=[]
        for x in range(1, self.n_questions+1):
            data.append([x, dd["v_{}_antw".format(x)][0],
                        dd["v_{}_juist".format(x)][0]])

        return pd.DataFrame(data, columns=["Question", "Answer", "Correct"])

    def answers_as_markdown(self, student):
        answers = self.get_answers(student)
        if answers is None:
            return ""

        md = MarkdownTable(list(answers.columns))
        for _, data in answers.iterrows():
            md.add_row(list(data))
        return str(md)

    def totalscore_as_markdown(self, student):
        score = self.get_score(student)
        if score is None:
            return ""

        md = MarkdownTable(["Student", "Score", "Grade"])
        md.add_row([student, score, self.grade_from_score(score=score)])
        return str(md)

    def overview(self):
        txt = "Questions: {}\n".format(self.n_questions)
        txt += "Students: {}\n".format(len(self.df))
        txt += "Moments: {}".format(pd.unique(self.df['moment']))
        return txt


def process_student(student_id,
                    spss_results,
                    student_ids,
                    email_letter,
                    email_subject,
                    feedback_answers,
                    feedback_total_scores,
                    mail_sender=None):
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

            body += "\n----\n"
            if feedback_total_scores:
                body += spss_results.totalscore_as_markdown(student=erna)
            else:
                body += "Student id: {}".format(erna)
            if feedback_answers:
                body += "\nYour responses\n\n" + \
                    spss_results.answers_as_markdown(student=erna)
            body += "\n----\n"

            to = erna + "@student.eur.nl" # TODO eur email could be in settings
            if isinstance(mail_sender, (EmailClient, DirectSMTP)):
                mail_sender.send_mail(recipient_email=to,
                                      subject=email_subject,
                                      body=body)

            return "NAME: {}\nTO: {}\nSUBJECT: {}\n\n".format(
                        stud_name, to, email_subject) +\
                        body
    else: # erna==None
        return stud_name # stud_name contains warning



