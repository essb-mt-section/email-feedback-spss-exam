python -m virtualenv env_efse

.\env_efse\Scripts\pip.exe install pandas, mailcomposer, markdown, appdirs, pysimplegui, pyinstaller
.\env_efse\Scripts\pyinstaller.exe --onefile -w --icon=picts\ESSB_logo.ico email_feedback_spss_exam.py