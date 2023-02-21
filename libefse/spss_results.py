from os import path
import pandas as pd

from .misc import MarkdownTable, VarnamePattern
from .alternative_correct import get_alternative_correct
# get_alternative_correct = None No alternative correct

class SPSSResults(object):

    ptn_question = VarnamePattern("v_", "_vraag")
    ptn_answer = VarnamePattern("v_", "_antw")
    ptn_correct = VarnamePattern("v_", "_juist")
    ptn_correctly_answered = VarnamePattern("v_", "_r")

    def __init__(self, file):
        """Reading SPSS of the webteam,
        export csv with details advanced, include erna voornaam tussenvoegsel achternaam
        """

        self.filename = path.split(file)[1]
        self.df = pd.read_csv(file, sep=";", dtype=str, encoding='cp1252')
        self._q_ids = [] # question ids

        for x in self.df.columns:
            if SPSSResults.ptn_question.match(x):
                self._q_ids.append(SPSSResults.ptn_question.get_int(x))

        self.n_questions = len(self._q_ids)
        self.missing_columns = []
        if self.n_questions == 0:
            self.missing_columns.append("questions")

        #check further required variables
        for required in ["totaal", "student", "erna",  "voornaam",
                         "tussenvoegsel","achternaam"]:
            if required not in self.df.columns:
                self.missing_columns.append(required)

    @property
    def is_incomplete(self):
        return len(self.missing_columns)>0

    @property
    def student_ids(self):
        return list(self.df['student'])

    def find_student_ids(self, pattern):
        """returns iterator over all matching ids
        """

        str_id = str(pattern)[:6].lower() # first numbers if erna or email
        return filter(lambda x: x.find(str_id)>=0, self.df['student'])

    def get_row(self, student):
        # allows emails, erna, student id
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
        #alternative_correct: pd.data frame with alternative correct answers
        row = self.get_row(student)
        if len(row) == 0:
            return None

        dd =  row.to_dict(orient="list")
        data=[]
        for x in range(1, self.n_questions+1):
            correct = dd["v_{}_juist".format(x)][0]
            if get_alternative_correct is not None:
                alternative = get_alternative_correct(value = correct)
                data.append([x, dd["v_{}_antw".format(x)][0],
                            correct, alternative])
            else:
                data.append([x, dd["v_{}_antw".format(x)][0], correct])

        if get_alternative_correct is not None:
            return pd.DataFrame(data, columns=["Question", "Answer", "Correct", "Correct2"])
        else:
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

    def get_email(self, student, domain="@student.eur.nl"):
        row = self.get_row(student)
        if len(row)==0:
            return None
        else:
            try:
                return row["erna"].iloc[0] + domain
            except:
                return None

    def get_full_name(self, student):
        row = self.get_row(student)
        if len(row)==0:
            return None
        else:
            rtn = ""
            for col in ["voornaam", "tussenvoegsel", "achternaam"]:
                try:
                    rtn += row[col].iloc[0] + " "
                except:
                    pass

        return rtn.strip()
