# Bully: Anniversary Edition header info string to Python dict/list converter
# Written by Edness   2022-04-03 - 2022-04-08   v1.1

def parse_info(txt):
    try_order = (int, float, str)
    def step_try(name):
        for step in try_order:
            try:
                step(name)
                return step
            except:
                continue

    def fix_eval(txt):
        def fix_list(lst):
            if lst[0] == len(lst) - 1:
                lst = lst[1:]
            for itm in lst:
                if type(itm) is list:
                    itm = fix_list(itm)
                elif type(itm) is dict:
                    itm = fix_dict(itm)
            return lst

        def fix_dict(dct):
            for i in dct:
                if type(dct[i]) is list:
                    dct[i] = fix_list(dct[i])
                elif type(dct[i]) is dict:
                    dct[i] = fix_dict(dct[i])
            return dct

        if type(txt) is list:
            txt = fix_list(txt)
        elif type(txt) is dict:
            txt = fix_dict(txt)
        return txt

    txt = txt.replace("\\", "\\\\")
    txt = txt.replace("\t", "")
    txt = txt.replace("\n", "")

    txt = txt.split(",")
    for i in range(len(txt)):
        ln = txt[i].split("=")
        for j in range(len(ln)):
            temp_ln = ln[j]
            start_skip = 0
            end_skip = len(ln[j])
            while temp_ln.startswith(("{", "[")):
                temp_ln = temp_ln[1:]
                start_skip += 1
            while temp_ln.endswith(("}", "]")):
                temp_ln = temp_ln[:-1]
                end_skip -= 1
            if step_try(temp_ln) is str:
                if not temp_ln.startswith(("\"", "\'")) and not temp_ln.endswith(("\"", "\'")):
                    temp_ln = f"\"{temp_ln}\""
                    if temp_ln == "\"\"":
                        temp_ln = "None"
                    elif temp_ln.lower() == "\"true\"":
                        temp_ln = "True"
                    elif temp_ln.lower() == "\"false\"":
                        temp_ln = "False"
            ln[j] = f"{ln[j][:start_skip]}{temp_ln}{ln[j][end_skip:]}"
        txt[i] = ":".join(ln)
    txt = eval(",".join(txt))
    txt = fix_eval(txt)
    return txt

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Converts the header info strings in Bully: Anniversary Edition to functional dicts and lists.")
    parser.add_argument("txt", type=str)
    args = parser.parse_args()

    #with open(args.txt, "r") as file:
    #    txt = parse_info(file.read())
    txt = parse_info(args.txt)
    print(txt)
