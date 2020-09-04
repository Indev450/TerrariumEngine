last_line_printed = ""

def printline(line):
    global last_line_printed
    print('\r' + line + ' '*(len(last_line_printed)-len(line)), end='')
    last_line_printed = line