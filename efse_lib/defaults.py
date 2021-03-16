BODY = """Dear {},

This email is the feedback for your SPSS exam. The table below contains all 
responses you gave and the correct answers.

<i>Explanation</i>

* Questions 01-09 were about multiple regression
* Questions 10-16 were about ANOVA
* Questions 17-20 were about repeated measures ANOVA

Oliver Lindemann
"""

SETTINGS={
    "body": BODY,
    "subject": "SPSS Exam Feedback",
    "sender_email": "lindemann@essb.eur.nl",
    "user": "63596oli@eur.nl",
    "smtp_server": "smtp.office365.com",
    "last_folder": None,
    "feedback_total_scores": False,
    "feedback_answers": True,
}