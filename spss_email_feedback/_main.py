import pandas as pd

from ._format import MarkdownTable
from ._send_mail import DirectSMTP, EmailClient

class StudentIDs(object):
    def __init__(self, file, sep="\t", col_names=("id", "name", "xx")):
        """A list of all student IDs and Student names as tsv with column
        "name" and "id"

        :param col_names: defines column names. To use first row as column
                        names, set col_names=None
        """

        self.df = pd.read_csv(file, sep=sep,
                              names=col_names)

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


class SPSSResults(object):

    def __init__(self, file, n_questions=20):
        """Reading SPSS of the webteam,
        export csv with details
        """

        self.n_questions = n_questions
        self.df = pd.read_csv(file, sep=";", dtype=str)

        # rename and selecting only relevant data
        rename = {}
        for rn in self.df.columns:
            if rn.endswith("_antw"):
                rename[rn] = rn.replace("_antw", "").replace(
                    "v_", "your_response_")
            elif rn.endswith("_juist"):
                rename[rn] = rn.replace("_juist", "").replace(
                    "v_", "correct_")
            elif rn == "totaal":
                rename[rn] = "score"
            elif rn != "student":
                self.df = self.df.drop(rn, 1)
        self.df.rename(columns=rename, inplace=True)

    def get_row(self, student):
        student = str(student)[:6] # erna without letters
        return self.df.loc[self.df['student'] == student]

    def get_data_dict(self, student):
        """returns data renamed"""
        row = self.get_row(student)
        if len(row) == 0:
            return {}
        return row.to_dict(orient="list")

    def get_score(self, student):
        row = self.get_row(student)
        if len(row) == 0:
            return None
        else:
            return int(row["score"])

    def grade_from_score(self, score, guessing_score=0, max_grade=10,
                         ndigits=1):
        return (round((score - guessing_score) /
                      (self.n_questions - guessing_score) * max_grade,
                      ndigits=ndigits))

    def data_as_markdown(self, student):
        data = self.get_data_dict(student)
        if len(data)==0:
            return ""

        md = MarkdownTable(["Questions", "Response", "Correct"])
        for x in range(1, self.n_questions+1):
            md.add_row([x, data["your_response_{}".format(x)][0],
                        data["correct_{}".format(x)][0]])
        return str(md)

    def grading_as_markdown(self, student):
        score = self.get_score(student)
        if score is None:
            return ""

        md = MarkdownTable(["Student", "Score", "Grade"])
        md.add_row([student, score, self.grade_from_score(score=score)])
        return str(md)


class Registrations(object):

    def __init__(self, file, col_name="Name", col_id="Student ID"):
        """iteration object for the registrations

        reads a csv file with the registered students (names and ids).
        :param file: csv-file with column names
        :param col_name: column the contains the student name
        :param col_id: column the contains the student id
        """

        self.df = pd.read_csv(file, sep=",")
        self.df.rename(columns={col_name: "name", col_id: "id"}, inplace=True)

    def __iter__(self):
        return zip(self.df["id"], self.df["name"])


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



