import pandas as pd

ALTTAB = pd.read_excel("~/teaching/44-AMDA/22/results/spss_exam_a_outcome_two_anova.xlsx")
ALTTAB = ALTTAB.rename(columns={"oneway": "correct", "twoway": "alternative"})

def get_alternative_correct(value):
    # helper function
    x = ALTTAB.loc[ALTTAB['correct'] == float(value)]
    if len(x):
        return x["alternative"].values[0]
    else:
        return ""
