#!/usr/bin/env python3
"""O. Lindemann"""

EMAIL_SUBJECT = "SPSS Feedback"
EMAIL_TXT = """Dear {},

This email is the feedback for your SPSS exam. The table below contains all response you gave and the correct answers.

<i>Explanations</i>:
    Questions 1-9 were about multiple regression
    Questions 10-16 were about ANOVA
    Questions 17-20 were about repeated measures ANOVA

    total_score:  Total number of correct answers
    'nan' means that no answer was registered

Oliver Lindemann
"""

if __name__ == "__main__":
    from spss_email_feedback import gui

    gui.run(email_letter=EMAIL_TXT,
            email_subject=EMAIL_SUBJECT)
