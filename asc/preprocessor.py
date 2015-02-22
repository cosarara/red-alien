import re
import os

def remove_comments(text):
    comment_symbols = ['//', "'"]
    pattern = "(//|')(.*?)$"
    replace = lambda s: re.sub(pattern, "", s)
    # remove comments only in nontext lines
    text = "\n".join([replace(s) if (len(s) > 1 and s[0] != "=") else s
                      for s in text.split("\n")])
    return text

def preprocess(text_script, include_path, symbols=None):
    line_n = 0
    lines = text_script.split("\n")
    if symbols is None:
        symbols = []
    while True:
        try:
            line = lines[line_n]
        except IndexError:
            break
        line = remove_comments(line)
        lines[line_n] = line
        if not line.strip():
            del lines[line_n]
            continue
        words = line.split(" ")
        command = words[0]
        if command == "#define":
            name = words[1]
            value = ' '.join(words[2:])
            symbols.append((name, value))
            del lines[line_n]
            continue
        elif command == "#include":
            name = words[1]
            name = name.strip("<>\"")
            t = None
            for d in include_path:
                fname = os.path.join(d, name)
                if os.path.isfile(fname):
                    with open(fname) as f:
                        t = f.read()
                    break
            if t is None:
                raise FileNotFoundError("#include'd file {} not found".format(name))
            lines = lines[:line_n] + t.split('\n') + lines[line_n+1:]
        elif "#if" in command:
            name = words[1]
            if (command == "#ifdef" and not name in list(zip(*symbols))[0] or
                command == "#ifndef" and name in list(zip(*symbols))[0]):
                # remove all till matching #endif
                opened_ifs = 1
                while opened_ifs != 0:
                    del lines[line_n]
                    try:
                        c = lines[line_n].split()
                    except IndexError:
                        raise Exception("unmatched #if")
                    if "#if" in c[0]:
                        opened_ifs += 1
                    elif "#endif" in c[0]:
                        opened_ifs -= 1
                del lines[line_n]
                continue
            else:
                line_n_bak = line_n
                # remove the matching #endif
                opened_ifs = 1
                while opened_ifs != 0:
                    line_n += 1
                    try:
                        c = lines[line_n].split()
                    except IndexError:
                        raise Exception("unmatched #if")
                    if "#if" in c[0]:
                        opened_ifs += 1
                    elif "#endif" in c[0]:
                        opened_ifs -= 1
                del lines[line_n]
                del lines[line_n_bak]
                line_n = line_n_bak
                continue
        else:
            # Replace #define'd symbols
            for name, value in symbols:
                # Because CAMERA mustn't conflict with CAMERA_START
                try:
                    line = re.sub(r"(^|\s)"+name+r"($|\s)", r"\g<1>"+value+r"\g<2>", line)
                except:
                    print(name, value, line)
                    print("Error on line", line_n)
                    raise
            lines[line_n] = line
            line_n += 1
    return '\n'.join(lines)
