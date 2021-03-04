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