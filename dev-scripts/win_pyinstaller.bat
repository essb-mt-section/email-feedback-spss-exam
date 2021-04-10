python -m virtualenv env_efse

.\env_efse\Scripts\pip.exe install -r requirements.txt
.\env_efse\Scripts\pip.exe install pyinstaller
.\env_efse\Scripts\pyinstaller.exe --onefile -w --icon=picts\ESSB_logo.ico email_feedback_spss_exam.py