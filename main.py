
# Открыть файл, указанный в аргументе
# Игнорировать переносы строк, пробелы, табуляции
# Русские С, E, х приводить к латинским
# Если заканчивается на : - это метка
# Если начинается на : - надо заменять на адрес метки
# Выводить в формате:
# nn    cc  mm
# где nn - номер строки, cc - код, mm - мнемокод
# кроме меток, для которых нет номера строки и кода

import sys


def main():
    try:
        if len(sys.argv) != 2:
            raise RuntimeError("No file name specified.\r\nUsage: python main.py <filename>")
        mnemo_dict = {}
        reverse_dict = {}
        with open("codes.txt", "r", encoding="UTF8") as codes:
            for n,line in enumerate(codes):
                if line.endswith("\r\n"):
                    line = line[:-2]
                if line.endswith("\n"):
                    line = line[:-1]
                line = line.upper().replace('С', 'C').replace('Е', 'E').replace('Х', 'X')
                line = line.replace('А', 'A').replace('К', 'K').replace('В', 'B')
                mnemo_code = line.split("\t")
                mnemo_err(len(mnemo_code) == 2, n, line, "must be exactly one tab")
                mnemo = mnemo_code[0]
                mnemo_err(len(mnemo) != 0, n, line, "mnemo is empty")
                mnemo_err(mnemo[0] != ' ' and mnemo[0] != '\t' and mnemo[-1] != ' ' and mnemo[-1] != '\t',
                          n, line, "mnemo must not begin or end with space characters")
                mnemo_err(mnemo not in mnemo_dict, n, line, f"mnemo '{mnemo}' duplicate")
                code = mnemo_code[1]
                mnemo_err(len(code) == 2, n, line, "code must be 2 hex characters")
                try:
                    _ = int(code, 16)
                except Exception:
                    mnemo_err(False, n, line, f"code '{code}' is not hexadecimal")
                mnemo_err(code not in reverse_dict, n, line, f"code '{code}' duplicate")
                mnemo_dict[mnemo] = code
                reverse_dict[code] = mnemo
        del reverse_dict
        generated_code = [] # array of triples (line num, code, mnemo+comment)
        label_addrs = {}    # name -> addr
        addr = 0
        with open(sys.argv[1], "r", encoding="UTF8") as input_file:
            for n,line in enumerate(input_file):
                line = line.lstrip()
                if line.endswith("\r\n"):
                    line = line[:-2]
                if line.endswith("\n"):
                    line = line[:-1]
                mnemo = ""
                pos = line.find("//")
                if pos >= 0:
                    mnemo = line[:pos]
                else:
                    mnemo = line
                mnemo = mnemo.rstrip().upper().replace('С', 'C').replace('Е', 'E')
                mnemo = mnemo.replace('Х', 'X').replace('А', 'A').replace('К', 'K').replace('В', 'B')
                if len(mnemo) == 0:
                    generated_code.append((-1, -1, line))
                elif mnemo.startswith(":"):
                    generated_code.append((addr, mnemo, line))
                    addr += 1
                elif mnemo.endswith(":"):
                    label_addrs[mnemo[:-1]] = addr
                    generated_code.append((-1, -1, line))
                else:
                    compilation_err(mnemo in mnemo_dict, n, line, f"Unknown mnemo {mnemo}")
                    code = mnemo_dict[mnemo]
                    generated_code.append((addr, code, line))
                    addr += 1
        # Replace labels and print output
        with open(sys.argv[1]+".mk56", "w", encoding="UTF8") as output_file:
            for addr,code,mnemo in generated_code:
                if addr == -1: # Empty line or label
                    print(mnemo, file=output_file)
                elif code.startswith(":"):
                    label = code[1:]
                    compilation_err(label in label_addrs, addr, mnemo, f"label {label} not found")
                    print(f"{addr:02}\t{label_addrs[label]:02}\t{mnemo}", file=output_file)
                else:
                    print(f"{addr:02}\t{code}\t{mnemo}", file=output_file)
    except Exception as e:
        print(f"EXCEPTION: {e}")


def err(cond, text):
    if not cond:
        raise RuntimeError(text)


def mnemo_err(cond, n, line, text):
    err(cond, f"Error in 'codes.txt' line {n}\r\n{line}\r\n{text}")


def compilation_err(cond, n, line, text):
    err(cond, f"Compilation error at line {n}\r\n{line}\r\n{text}")


main()
