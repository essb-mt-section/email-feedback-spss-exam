from random import randint
import re
import numpy as np

def replace_multi_spaces(txt, replace_str):
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


class VarnamePattern(object):
    # Helper Class to handle Varnames with numbers

    def __init__(self, prefix, suffix):
        self._pttrn = (prefix, suffix)
        self._regex =  re.compile(r"^" + prefix + r"\d*" + suffix + r"$")

    def match(self, txt):
        return self._regex.match(txt)

    def make(self, number):
        return "{}{}{}".format(self._pttrn[0], number, self._pttrn[1])

    def get_int(self, txt):
        try:
            return int(txt.replace(self._pttrn[0], "").replace(
                                self._pttrn[1], ""))
        except:
            return None


class MarkdownTable(object):

    def __init__(self, column_names):

        if not isinstance(column_names, (list, tuple)):
            raise TypeError("column_names has to be a list or tuple")
        self.table = []
        self.table.append(column_names)
        self.width = list(map(len, column_names))
        self.n_cols = len(column_names)


    def add_row(self, row_data):
        if len(row_data) != self.n_cols:
            raise TypeError("row_data must be an array of the length {}".format(
                self.n_cols))

        #conert to string and check max_width
        for x in range(len(row_data)):
            row_data[x] = str(row_data[x])
            if len(row_data[x])>self.width[x]:
                self.width[x] = len(row_data[x])

        self.table.append(row_data)

    def __str__(self):
        header = True
        rtn = ""
        for row in self.table:
            rtn += "| "
            for w, c in zip(self.width, row):
                rtn += c + " "*(w-len(c)) + " | "
            rtn = rtn[:-1] + "\n"
            if header:
                rtn += "| "
                for w in self.width:
                    rtn += "-"*w + " | "
                rtn = rtn[:-1] + "\n"
                header = False
        return rtn


def csv2lst(csv):
    return list(filter(lambda x: len(x),
                       map(lambda x: x.strip(), csv.split(","))))


def lst2csv(lst):
    return ", ".join(map(str, lst))


def is_equal_after_rounding(a, b, decimals):
    # TRUE if the a equals b after both numbers being rounded
    return np.round(a, decimals=decimals) == np.round(b, decimals=decimals)


def random_element(a_list):
    return a_list[randint(0, len(a_list))]
