SEND_PAUSE_AFTER = 50
SEND_PAUSE_DURATION = 10
NAME_PLACE_HOLDER = "[NAME]"
DEBUG_REPLACE_RECIPIENT_EMAIL = None
#DEBUG_REPLACE_RECIPIENT_EMAIL = "ol@limetree.de"

### defaults
DEFAULT_BODY = """Dear [NAME],

This email is the feedback for your SPSS exam. The table below contains all 
responses you gave and the correct answers.

<i>Explanation</i>

* Questions 01-09 were about multiple regression
* Questions 10-16 were about ANOVA
* Questions 17-20 were about repeated measures ANOVA

Oliver Lindemann
"""

DEFAULT_SETTINGS={
    "body": DEFAULT_BODY,
    "subject": "SPSS Exam Feedback",
    "sender_email": "xxxx@essb.eur.nl",
    "user": "12345abc@eur.nl",
    "smtp_server": "smtp.office365.com",
    "last_folder": None,
    "feedback_total_scores": False,
    "feedback_answers": True,
}