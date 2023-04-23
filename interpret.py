
# Jana Veronika Moskvová - xmoskv01
# 2. IPP projekt - interpret

import sys
import xml.etree.ElementTree as ET
import re

def getLabels(source, labels):
    i = 0
    size = len(source)
    while i < size:
        if (source[i][1].attrib.get('opcode') and source[i][1].attrib['opcode'].lower() == "label"):
            if isLabel(source[i][1][0]):
                if labels.get(source[i][1][0].text):
                    return 52
                else:
                    labels[source[i][1][0].text] = source[i][0]
            else:
                return 53
        i += 1

    return 0


def transformString(string):
    if string is None:
        return ""

    i = 0
    bs = []
    result = list(string)
    while i < len(string):
        if string[i] == "\\":
            bs.append(i)
        i += 1
    for pos in bs:
        seq = string[pos+1:pos+4]
        result[pos] = chr(int(seq))
        result[pos+1] = result[pos+2] = result[pos+3] = ""

    return "".join(result)


def isVar(var):
    if var.attrib.get('type'):
        if var.attrib.get('type') == "var":
            if re.match(r'\A(LF|GF|TF)@[a-zA-Z\-_$&%*!?][a-zA-Z0-9_\-$&%*!?]*\Z', var.text):
                return True

    return False


def isLabel(label):
    if label.attrib.get('type'):
        if label.attrib.get('type') == "label":
            if re.match(r'\A[a-zA-Z$\*&_%!?-][a-zA-Z$\*&_%!?\d-]*\Z', label.text):
                return True
    return False


def isConst(const):
    if const.attrib.get('type'):
        if const.attrib['type'] == "int":
            try:
                int(const.text)
                return "int"
            except ValueError:
                exit(32)
        elif const.attrib['type'] == "nil":
            if const.text == "nil":
                return "nil"
        elif const.attrib['type'] == "bool":
            if const.text == "true" or const.text == "false":
                return "bool"
        elif const.attrib['type'] == "string":
            if not(const.text) or re.match(r'\A([^\\]|\\\d{3})*\Z', const.text):
                const.text = transformString(const.text)
                return "string"
    return ""


def isSymb(symb):
    if isVar(symb) or isConst(symb):
        return True
    return False


class instructionRunner:
    def __init__(self, interpretData):
        self.data = interpretData

    def instructionMatch(self, opcode, args):
        result = 0
        match opcode:
            case "move":
                result = self.MoveInstruction(args)
            case "createframe":
                result = self.CreateFrameInstruction(args)
            case "pushframe":
                result = self.PushFrameInstruction(args)
            case "popframe":
                result = self.PopFrameInstruction(args)
            case "defvar":
                result = self.DefVarInstruction(args)
            case "call":
                result = self.CallInstruction(args)
            case "return":
                result = self.ReturnInstruction(args)
            case "pushs":
                result = self.PushsInstruction(args)
            case "pops":
                result = self.PopsInstruction(args)
            case "add":
                result = self.AddInstruction(args)
            case "sub":
                result = self.SubInstruction(args)
            case "mul":
                result = self.MulInstruction(args)
            case "idiv":
                result = self.IDivInstruction(args)
            case "lt":
                result = self.LTInstruction(args)
            case "gt":
                result = self.GTInstruction(args)
            case "eq":
                result = self.EQInstruction(args)
            case "and":
                result = self.AndInstruction(args)
            case "or":
                result = self.OrInstruction(args)
            case "not":
                result = self.NotInstruction(args)
            case "int2char":
                result = self.Int2CharInstruction(args)
            case "stri2int":
                result = self.Stri2IntInstruction(args)
            case "read":
                result = self.ReadInstruction(args)
            case "write":
                result = self.WriteInstruction(args)
            case "concat":
                result = self.ConcatInstruction(args)
            case "strlen":
                result = self.StrLenInstruction(args)
            case "getchar":
                result = self.GetCharInstruction(args)
            case "setchar":
                result = self.SetCharInstruction(args)
            case "type":
                result = self.TypeInstruction(args)
            case "label":
                result = self.LabelInstruction(args)
            case "jump":
                result = self.JumpInstruction(args)
            case "jumpifeq":
                result = self.JumpIfEQInstruction(args)
            case "jumpifneq":
                result = self.JumpIfNEQInstruction(args)
            case "exit":
                result = self.ExitInstruction(args)
            case "dprint":
                result = self.DPrintInstruction(args)
            case "break":
                result = self.BreakInstruction(args)
            case _:
                result = 32
        return result

    def MoveInstruction(self, args):
        if len(args) != 2 or not isVar(args[0]) or not isSymb(args[1]):
            return 32

        arg1 = args[0].text.split('@', maxsplit=1)
        frame1 = self.data[arg1[0]]
        if frame1 is None:
            return 55
        if len(arg1) < 2 or arg1[1] not in frame1:
            return 54

        if isConst(args[1]):
            self.data[arg1[0]][arg1[1]] = "{}@{}".format(args[1].attrib['type'], args[1].text)
        else:
            arg2 = args[1].text.split('@', maxsplit=1)
            frame2 = self.data[arg2[0]]
            if frame2 is None:
                return 55
            if len(arg2) < 2 or arg2[1] not in frame2:
                return 54
            if frame2[arg2[1]] is None:
                return 56
            self.data[arg1[0]][arg1[1]] = frame2[arg2[1]]
        return 0

    def CreateFrameInstruction(self, args):
        if len(args) != 0:
            return 32
        self.data['TF'] = {}
        return 0

    def PushFrameInstruction(self, args):
        if len(args) != 0:
            return 32
        if self.data['TF'] is None:
            return 55

        self.data['LFs'].append(self.data['LF'])
        self.data['LF'] = self.data['TF']
        self.data['TF'] = None

        return 0

    def PopFrameInstruction(self, args):
        if len(args) != 0:
            return 32

        if self.data['LF'] is None:
            return 55

        self.data['TF'] = self.data['LF']
        if len(self.data['LFs']) == 0:
            self.data['LF'] = None
        else:
            self.data['LF'] = self.data['LFs'].pop()

        return 0

    def DefVarInstruction(self, args):
        if len(args) != 1 or not isVar(args[0]):
            return 32

        arg = args[0].text.split('@', maxsplit=1)
        frame = self.data[arg[0]]
        if frame is None:
            return 55
        if arg[1] in frame:
            return 52
        self.data[arg[0]][arg[1]] = None

        return 0

    def CallInstruction(self, args):
        if len(args) != 1 or not isLabel(args[0]):
            return 32
        if not self.data['labels'].get(args[0].text):
            return 52
        self.data['calls'].append(self.data['opcount'])
        self.data['opcount'] = self.data['labels'][args[0].text]

        return 0

    def ReturnInstruction(self, args):
        if len(args) != 0:
            return 32

        if len(self.data['calls']) == 0:
            return 56

        self.data['opcount'] = self.data['calls'].pop()

        return 0

    def PushsInstruction(self, args):
        if len(args) != 1 or not isSymb(args[0]):
            return 32

        if isConst(args[0]):
            self.data['datas'].append("{}@{}".format(args[0].attrib['type'], args[0].text))
        else:
            arg = args[0].text.split('@', maxsplit=1)
            frame = self.data[arg[0]]
            if frame is None:
                return 55
            if frame.get(arg[1], -1) == -1:
                return 54
            if frame[arg[1]] is None:
                return 56
            self.data['datas'].append(frame[arg[1]])

        return 0

    def PopsInstruction(self, args):
        if len(args) != 1 or not isVar(args[0]):
            return 32

        if len(self.data['datas']) == 0:
            return 56

        arg = args[0].text.split('@', maxsplit=1)
        frame = self.data[arg[0]]
        if frame is None:
            return 55
        try:
            noneTest = frame[arg[1]]
        except KeyError:
            return 54
        self.data[arg[0]][arg[1]] = self.data['datas'].pop()

        return 0

    def AddInstruction(self, args):
        if len(args) != 3 or not isVar(args[0]) or not isSymb(args[1]) or not isSymb(args[2]):
            return 32

        arg1 = args[0].text.split('@', maxsplit=1)
        frame1 = self.data[arg1[0]]
        if frame1 is None:
            return 55
        try:
            noneTest = frame1[arg1[1]]
        except KeyError:
            return 54

        op1 = 0
        op2 = 0

        if isConst(args[1]):
            if not args[1].attrib['type'] == "int":
                return 53
            op1 = int(args[1].text)
        else:
            arg2 = args[1].text.split('@', maxsplit=1)
            frame2 = self.data[arg2[0]]
            if frame2 is None:
                return 55
            try:
                noneTest = frame2[arg2[1]]
            except KeyError:
                return 54
            if frame2[arg2[1]] is None:
                return 56
            value2 = frame2[arg2[1]].split('@', maxsplit=1)
            if len(value2) == 2 and value2[0] == "int":
                op1 = int(value2[1])
            else:
                return 53

        if isConst(args[2]):
            if not args[2].attrib['type'] == "int":
                return 53
            op2 = int(args[2].text)
        else:
            arg3 = args[2].text.split('@', maxsplit=1)
            frame3 = self.data[arg3[0]]
            if frame3 is None:
                return 55
            try:
                noneTest = frame3[arg3[1]]
            except KeyError:
                return 54
            if frame3[arg3[1]] is None:
                return 56
            value3 = frame3[arg3[1]].split('@', maxsplit=1)
            if len(value3) == 2 and value3[0] == "int":
                op2 = int(value3[1])
            else:
                return 53

        result = op1 + op2
        self.data[arg1[0]][arg1[1]] = "{}@{}".format("int", str(result))

        return 0

    def SubInstruction(self, args):
        if len(args) != 3 or not isVar(args[0]) or not isSymb(args[1]) or not isSymb(args[2]):
            return 32

        arg1 = args[0].text.split('@', maxsplit=1)
        frame1 = self.data[arg1[0]]
        if frame1 is None:
            return 55
        try:
            noneTest = frame1[arg1[1]]
        except KeyError:
            return 54

        op1 = 0
        op2 = 0

        if isConst(args[1]):
            if not args[1].attrib['type'] == "int":
                return 53
            op1 = int(args[1].text)
        else:
            arg2 = args[1].text.split('@', maxsplit=1)
            frame2 = self.data[arg2[0]]
            if frame2 is None:
                return 55
            try:
                noneTest = frame2[arg2[1]]
            except KeyError:
                return 54
            if frame2[arg2[1]] is None:
                return 56
            value2 = frame2[arg2[1]].split('@', maxsplit=1)
            if len(value2) == 2 and value2[0] == "int":
                op1 = int(value2[1])
            else:
                return 53

        if isConst(args[2]):
            if not args[2].attrib['type'] == "int":
                return 53
            op2 = int(args[2].text)
        else:
            arg3 = args[2].text.split('@', maxsplit=1)
            frame3 = self.data[arg3[0]]
            if frame3 is None:
                return 55
            try:
                noneTest = frame3[arg3[1]]
            except KeyError:
                return 54
            if frame3[arg3[1]] is None:
                return 56
            value3 = frame3[arg3[1]].split('@', maxsplit=1)
            if len(value3) == 2 and value3[0] == "int":
                op2 = int(value3[1])
            else:
                return 53

        result = op1 - op2
        self.data[arg1[0]][arg1[1]] = "{}@{}".format("int", str(result))

        return 0

    def MulInstruction(self, args):
        if len(args) != 3 or not isVar(args[0]) or not isSymb(args[1]) or not isSymb(args[2]):
            return 32

        arg1 = args[0].text.split('@', maxsplit=1)
        frame1 = self.data[arg1[0]]
        if frame1 is None:
            return 55
        try:
            noneTest = frame1[arg1[1]]
        except KeyError:
            return 54

        op1 = 0
        op2 = 0

        if isConst(args[1]):
            if not args[1].attrib['type'] == "int":
                return 53
            op1 = int(args[1].text)
        else:
            arg2 = args[1].text.split('@', maxsplit=1)
            frame2 = self.data[arg2[0]]
            if frame2 is None:
                return 55
            try:
                noneTest = frame2[arg2[1]]
            except KeyError:
                return 54
            if frame2[arg2[1]] is None:
                return 56
            value2 = frame2[arg2[1]].split('@', maxsplit=1)
            if len(value2) == 2 and value2[0] == "int":
                op1 = int(value2[1])
            else:
                return 53

        if isConst(args[2]):
            if not args[2].attrib['type'] == "int":
                return 53
            op2 = int(args[2].text)
        else:
            arg3 = args[2].text.split('@', maxsplit=1)
            frame3 = self.data[arg3[0]]
            if frame3 is None:
                return 55
            try:
                noneTest = frame3[arg3[1]]
            except KeyError:
                return 54
            if frame3[arg3[1]] is None:
                return 56
            value3 = frame3[arg3[1]].split('@', maxsplit=1)
            if len(value3) == 2 and value3[0] == "int":
                op2 = int(value3[1])
            else:
                return 53

        result = op1 * op2
        self.data[arg1[0]][arg1[1]] = "{}@{}".format("int", str(result))

        return 0

    def IDivInstruction(self, args):
        if len(args) != 3 or not isVar(args[0]) or not isSymb(args[1]) or not isSymb(args[2]):
            return 32

        arg1 = args[0].text.split('@', maxsplit=1)
        frame1 = self.data[arg1[0]]
        if frame1 is None:
            return 55
        try:
            noneTest = frame1[arg1[1]]
        except KeyError:
            return 54

        op1 = 0
        op2 = 0

        if isConst(args[1]):
            if not args[1].attrib['type'] == "int":
                return 53
            op1 = int(args[1].text)
        else:
            arg2 = args[1].text.split('@', maxsplit=1)
            frame2 = self.data[arg2[0]]
            if frame2 is None:
                return 55
            try:
                noneTest = frame2[arg2[1]]
            except KeyError:
                return 54
            if frame2[arg2[1]] is None:
                return 56
            value2 = frame2[arg2[1]].split('@', maxsplit=1)
            if len(value2) == 2 and value2[0] == "int":
                op1 = int(value2[1])
            else:
                return 53

        if isConst(args[2]):
            if not args[2].attrib['type'] == "int":
                return 53
            op2 = int(args[2].text)
        else:
            arg3 = args[2].text.split('@', maxsplit=1)
            frame3 = self.data[arg3[0]]
            if frame3 is None:
                return 55
            try:
                noneTest = frame3[arg3[1]]
            except KeyError:
                return 54
            if frame3[arg3[1]] is None:
                return 56
            value3 = frame3[arg3[1]].split('@', maxsplit=1)
            if len(value3) == 2 and value3[0] == "int":
                op2 = int(value3[1])
            else:
                return 53

        if op2 == 0:
            return 57

        result = int(op1 / op2)
        self.data[arg1[0]][arg1[1]] = "{}@{}".format("int", str(result))

        return 0

    def LTInstruction(self, args):
        if len(args) != 3 or not isVar(args[0]) or not isSymb(args[1]) or not isSymb(args[2]):
            return 32

        arg1 = args[0].text.split('@', maxsplit=1)
        frame1 = self.data[arg1[0]]
        if frame1 is None:
            return 55
        try:
            noneTest = frame1[arg1[1]]
        except KeyError:
            return 54

        op1 = ""
        type1 = ""
        op2 = ""
        type2 = ""

        if isConst(args[1]):
            type1 = args[1].attrib['type']
            op1 = args[1].text
        else:
            arg2 = args[1].text.split('@', maxsplit=1)
            frame2 = self.data[arg2[0]]
            if frame2 is None:
                return 55
            try:
                noneTest = frame2[arg2[1]]
            except KeyError:
                return 54
            if frame2[arg2[1]] is None:
                return 56
            value2 = frame2[arg2[1]].split('@', maxsplit=1)
            type1 = value2[0]
            op1 = value2[1]

        if isConst(args[2]):
            type2 = args[2].attrib['type']
            op2 = args[2].text
        else:
            arg3 = args[2].text.split('@', maxsplit=1)
            frame3 = self.data[arg3[0]]
            if frame3 is None:
                return 55
            try:
                noneTest = frame3[arg3[1]]
            except KeyError:
                return 54
            if frame3[arg3[1]] is None:
                return 56
            value3 = frame3[arg3[1]].split('@', maxsplit=1)
            type2 = value3[0]
            op2 = value3[1]

        if type1 != type2 or type1 == "nil":
            return 53

        if type1 == "int":
            op1 = int(op1)
            op2 = int(op2)

        result = op1 < op2
        self.data[arg1[0]][arg1[1]] = "{}@{}".format("bool", str(result).lower())

        return 0

    def GTInstruction(self, args):
        if len(args) != 3 or not isVar(args[0]) or not isSymb(args[1]) or not isSymb(args[2]):
            return 32

        arg1 = args[0].text.split('@', maxsplit=1)
        frame1 = self.data[arg1[0]]
        if frame1 is None:
            return 55
        try:
            noneTest = frame1[arg1[1]]
        except KeyError:
            return 54

        op1 = ""
        type1 = ""
        op2 = ""
        type2 = ""

        if isConst(args[1]):
            type1 = args[1].attrib['type']
            op1 = args[1].text
        else:
            arg2 = args[1].text.split('@', maxsplit=1)
            frame2 = self.data[arg2[0]]
            if frame2 is None:
                return 55
            try:
                noneTest = frame2[arg2[1]]
            except KeyError:
                return 54
            if frame2[arg2[1]] is None:
                return 56
            value2 = frame2[arg2[1]].split('@', maxsplit=1)
            type1 = value2[0]
            op1 = value2[1]

        if isConst(args[2]):
            type2 = args[2].attrib['type']
            op2 = args[2].text
        else:
            arg3 = args[2].text.split('@', maxsplit=1)
            frame3 = self.data[arg3[0]]
            if frame3 is None:
                return 55
            try:
                noneTest = frame3[arg3[1]]
            except KeyError:
                return 54
            if frame3[arg3[1]] is None:
                return 56
            value3 = frame3[arg3[1]].split('@', maxsplit=1)
            type2 = value3[0]
            op2 = value3[1]

        if type1 != type2 or type1 == "nil":
            return 53

        if type1 == "int":
            op1 = int(op1)
            op2 = int(op2)

        result = op1 > op2
        self.data[arg1[0]][arg1[1]] = "{}@{}".format("bool", str(result).lower())

        return 0

    def EQInstruction(self, args):
        if len(args) != 3 or not isVar(args[0]) or not isSymb(args[1]) or not isSymb(args[2]):
            return 32

        arg1 = args[0].text.split('@', maxsplit=1)
        frame1 = self.data[arg1[0]]
        if frame1 is None:
            return 55
        try:
            noneTest = frame1[arg1[1]]
        except KeyError:
            return 54

        op1 = ""
        type1 = ""
        op2 = ""
        type2 = ""

        if isConst(args[1]):
            type1 = args[1].attrib['type']
            op1 = args[1].text
        else:
            arg2 = args[1].text.split('@', maxsplit=1)
            frame2 = self.data[arg2[0]]
            if frame2 is None:
                return 55
            try:
                noneTest = frame2[arg2[1]]
            except KeyError:
                return 54
            if frame2[arg2[1]] is None:
                return 56
            value2 = frame2[arg2[1]].split('@', maxsplit=1)
            type1 = value2[0]
            op1 = value2[1]

        if isConst(args[2]):
            type2 = args[2].attrib['type']
            op2 = args[2].text
        else:
            arg3 = args[2].text.split('@', maxsplit=1)
            frame3 = self.data[arg3[0]]
            if frame3 is None:
                return 55
            try:
                noneTest = frame3[arg3[1]]
            except KeyError:
                return 54
            if frame3[arg3[1]] is None:
                return 56
            value3 = frame3[arg3[1]].split('@', maxsplit=1)
            type2 = value3[0]
            op2 = value3[1]

        if type1 == "nil" or type2 == "nil":
            result = type1 == type2
            self.data[arg1[0]][arg1[1]] = "{}@{}".format("bool", str(result).lower())
            return 0

        if type1 != type2:
            return 53

        if type1 == "int":
            op1 = int(op1)
            op2 = int(op2)

        result = op1 == op2
        self.data[arg1[0]][arg1[1]] = "{}@{}".format("bool", str(result).lower())

        return 0

    def AndInstruction(self, args):
        if len(args) != 3 or not isVar(args[0]) or not isSymb(args[1]) or not isSymb(args[2]):
            return 32

        arg1 = args[0].text.split('@', maxsplit=1)
        frame1 = self.data[arg1[0]]
        if frame1 is None:
            return 55
        try:
            noneTest = frame1[arg1[1]]
        except KeyError:
            return 54

        op1 = 0
        op2 = 0

        if isConst(args[1]):
            if not args[1].attrib['type'] == "bool":
                return 53
            if args[1].text == "true":
                op1 = True
            else:
                op1 = False
        else:
            arg2 = args[1].text.split('@', maxsplit=1)
            frame2 = self.data[arg2[0]]
            if frame2 is None:
                return 55
            try:
                noneTest = frame2[arg2[1]]
            except KeyError:
                return 54
            if frame2[arg2[1]] is None:
                return 56
            value2 = frame2[arg2[1]].split('@', maxsplit=1)
            if len(value2) == 2 and value2[0] == "bool":
                if value2[1] == "true":
                    op1 = True
                else:
                    op1 = False
            else:
                return 53

        if isConst(args[2]):
            if not args[2].attrib['type'] == "bool":
                return 53
            if args[2].text == "true":
                op2 = True
            else:
                op2 = False
        else:
            arg3 = args[2].text.split('@', maxsplit=1)
            frame3 = self.data[arg3[0]]
            if frame3 is None:
                return 55
            try:
                noneTest = frame3[arg3[1]]
            except KeyError:
                return 54
            if frame3[arg3[1]] is None:
                return 56
            value3 = frame3[arg3[1]].split('@', maxsplit=1)
            if len(value3) == 2 and value3[0] == "bool":
                if value3[1] == "true":
                    op2 = True
                else:
                    op2 = False
            else:
                return 53

        result = op1 and op2
        self.data[arg1[0]][arg1[1]] = "{}@{}".format("bool", str(result).lower())

        return 0

    def OrInstruction(self, args):
        if len(args) != 3 or not isVar(args[0]) or not isSymb(args[1]) or not isSymb(args[2]):
            return 32

        arg1 = args[0].text.split('@', maxsplit=1)
        frame1 = self.data[arg1[0]]
        if frame1 is None:
            return 55
        try:
            noneTest = frame1[arg1[1]]
        except KeyError:
            return 54

        op1 = 0
        op2 = 0

        if isConst(args[1]):
            if not args[1].attrib['type'] == "bool":
                return 53
            if args[1].text == "true":
                op1 = True
            else:
                op1 = False
        else:
            arg2 = args[1].text.split('@', maxsplit=1)
            frame2 = self.data[arg2[0]]
            if frame2 is None:
                return 55
            try:
                noneTest = frame2[arg2[1]]
            except KeyError:
                return 54
            if frame2[arg2[1]] is None:
                return 56
            value2 = frame2[arg2[1]].split('@', maxsplit=1)
            if len(value2) == 2 and value2[0] == "bool":
                if value2[1] == "true":
                    op1 = True
                else:
                    op1 = False
            else:
                return 53

        if isConst(args[2]):
            if not args[2].attrib['type'] == "bool":
                return 53
            if args[2].text == "true":
                op2 = True
            else:
                op2 = False
        else:
            arg3 = args[2].text.split('@', maxsplit=1)
            frame3 = self.data[arg3[0]]
            if frame3 is None:
                return 55
            try:
                noneTest = frame3[arg3[1]]
            except KeyError:
                return 54
            if frame3[arg3[1]] is None:
                return 56
            value3 = frame3[arg3[1]].split('@', maxsplit=1)
            if len(value3) == 2 and value3[0] == "bool":
                if value3[1] == "true":
                    op2 = True
                else:
                    op2 = False
            else:
                return 53

        result = op1 or op2
        self.data[arg1[0]][arg1[1]] = "{}@{}".format("bool", str(result).lower())

        return 0

    def NotInstruction(self, args):
        if len(args) != 2 or not isVar(args[0]) or not isSymb(args[1]):
            return 32

        arg1 = args[0].text.split('@', maxsplit=1)
        frame1 = self.data[arg1[0]]
        if frame1 is None:
            return 55
        try:
            noneTest = frame1[arg1[1]]
        except KeyError:
            return 54

        op1 = 0

        if isConst(args[1]):
            if not args[1].attrib['type'] == "bool":
                return 53
            if args[1].text == "true":
                op1 = True
            else:
                op1 = False
        else:
            arg2 = args[1].text.split('@', maxsplit=1)
            frame2 = self.data[arg2[0]]
            if frame2 is None:
                return 55
            try:
                noneTest = frame2[arg2[1]]
            except KeyError:
                return 54
            if frame2[arg2[1]] is None:
                return 56
            value2 = frame2[arg2[1]].split('@', maxsplit=1)
            if len(value2) == 2 and value2[0] == "bool":
                if value2[1] == "true":
                    op1 = True
                else:
                    op1 = False
            else:
                return 53

        result = not op1
        self.data[arg1[0]][arg1[1]] = "{}@{}".format("bool", str(result).lower())

        return 0

    def Int2CharInstruction(self, args):
        if len(args) != 2 or not isVar(args[0]) or not isSymb(args[1]):
            return 32

        arg1 = args[0].text.split('@', maxsplit=1)
        frame1 = self.data[arg1[0]]
        if frame1 is None:
            return 55
        try:
            noneTest = frame1[arg1[1]]
        except KeyError:
            return 54

        op1 = -1

        if isConst(args[1]):
            if not args[1].attrib['type'] == "int":
                return 53
            op1 = int(args[1].text)
        else:
            arg2 = args[1].text.split('@', maxsplit=1)
            frame2 = self.data[arg2[0]]
            if frame2 is None:
                return 55
            try:
                noneTest = frame2[arg2[1]]
            except KeyError:
                return 54
            if frame2[arg2[1]] is None:
                return 56
            value2 = frame2[arg2[1]].split('@', maxsplit=1)
            if len(value2) == 2 and value2[0] == "int":
                op1 = int(value2[1])
            else:
                return 53

        try:
            result = chr(op1)
            self.data[arg1[0]][arg1[1]] = "{}@{}".format("string", result)
        except ValueError:
            return 58

        return 0

    def Stri2IntInstruction(self, args):
        if (len(args) != 3 or not isVar(args[0]) or not isSymb(args[1]) or not isSymb(args[2])):
            return 32

        arg1 = args[0].text.split('@', maxsplit=1)
        frame1 = self.data[arg1[0]]
        if frame1 is None:
            return 55
        try:
            noneTest = frame1[arg1[1]]
        except KeyError:
            return 54

        op1 = ""
        op2 = -1

        if isConst(args[1]):
            if not args[1].attrib['type'] == "string":
                return 53
            op1 = args[1].text
        else:
            arg2 = args[1].text.split('@', maxsplit=1)
            frame2 = self.data[arg2[0]]
            if frame2 is None:
                return 55
            try:
                noneTest = frame2[arg2[1]]
            except KeyError:
                return 54
            if frame2[arg2[1]] is None:
                return 56
            value2 = frame2[arg2[1]].split('@', maxsplit=1)
            if (len(value2) == 2 and value2[0] == "string"):
                op1 = value2[1]
            else:
                return 53

        if isConst(args[2]):
            if not args[2].attrib['type'] == "int":
                return 53
            op2 = int(args[2].text)
        else:
            arg3 = args[2].text.split('@', maxsplit=1)
            frame3 = self.data[arg3[0]]
            if frame3 is None:
                return 55
            try:
                noneTest = frame3[arg3[1]]
            except KeyError:
                return 54
            if frame3[arg3[1]] is None:
                return 56
            value3 = frame3[arg3[1]].split('@', maxsplit=1)
            if (len(value3) == 2 and value3[0] == "int"):
                op2 = int(value3[1])
            else:
                return 53

        if len(op1) > op2 and op2 >= 0:
            result = op1[op2]
            result = ord(result)
            self.data[arg1[0]][arg1[1]] = "{}@{}".format("int", int(result))
        else:
            return 58

        return 0

    def ReadInstruction(self, args):
        if len(args) != 2 or not isVar(args[0]) or not args[1].text in ["int", "string", "bool"]:
            return 32

        arg = args[0].text.split('@', maxsplit=1)
        frame = self.data[arg[0]]
        if frame is None:
            return 55
        try:
            noneTest = frame[arg[1]]
        except KeyError:
            return 54

        result = self.data['input'].readline()
        if not result:
            self.data[arg[0]][arg[1]] = "{}@{}".format("nil", "nil")
            return 0
        result = result.rstrip("\n")

        if args[1].text == "int":
            try:
                self.data[arg[0]][arg[1]] = "{}@{}".format("int", int(result))
            except ValueError:
                self.data[arg[0]][arg[1]] = "{}@{}".format("nil", "nil")
        elif args[1].text == "string":
            self.data[arg[0]][arg[1]] = "{}@{}".format("string", result)
        elif args[1].text == "bool":
            if result.lower() == "true":
                self.data[arg[0]][arg[1]] = "{}@{}".format("bool", "true")
            else:
                self.data[arg[0]][arg[1]] = "{}@{}".format("bool", "false")

        return 0

    def WriteInstruction(self, args):
        if len(args) != 1 or not isSymb(args[0]):
            return 32

        if isConst(args[0]):
            type1 = args[0].attrib['type']
            op1 = args[0].text
        else:
            arg = args[0].text.split('@', maxsplit=1)
            frame = self.data[arg[0]]
            if frame is None:
                return 55
            try:
                noneTest = frame[arg[1]]
            except KeyError:
                return 54
            if frame[arg[1]] is None:
                return 56
            value1 = frame[arg[1]].split('@', maxsplit=1)
            type1 = value1[0]
            op1 = value1[1]

        if type1 == "string" or type1 == "int" or type1 == "bool":
            print(op1, end='')
        elif type1 == "nil":
            print("", end='')
        return 0

    def ConcatInstruction(self, args):
        if len(args) != 3 or not isVar(args[0]) or not isSymb(args[1]) or not isSymb(args[2]):
            return 32

        arg1 = args[0].text.split('@', maxsplit=1)
        frame1 = self.data[arg1[0]]
        if frame1 is None:
            return 55
        try:
            noneTest = frame1[arg1[1]]
        except KeyError:
            return 54

        op1 = ""
        op2 = ""

        if isConst(args[1]):
            if not args[1].attrib['type'] == "string":
                return 53
            op1 = args[1].text
        else:
            arg2 = args[1].text.split('@', maxsplit=1)
            frame2 = self.data[arg2[0]]
            if frame2 is None:
                return 55
            try:
                noneTest = frame2[arg2[1]]
            except KeyError:
                return 54
            if frame2[arg2[1]] is None:
                return 56
            value2 = frame2[arg2[1]].split('@', maxsplit=1)
            if len(value2) == 2 and value2[0] == "string":
                op1 = value2[1]
            else:
                return 53

        if isConst(args[2]):
            if not args[2].attrib['type'] == "string":
                return 53
            op2 = args[2].text
        else:
            arg3 = args[2].text.split('@', maxsplit=1)
            frame3 = self.data[arg3[0]]
            if frame3 is None:
                return 55
            try:
                noneTest = frame3[arg3[1]]
            except KeyError:
                return 54
            if frame3[arg3[1]] is None:
                return 56
            value3 = frame3[arg3[1]].split('@', maxsplit=1)
            if len(value3) == 2 and value3[0] == "string":
                op2 = value3[1]
            else:
                return 53

        result = op1 + op2
        self.data[arg1[0]][arg1[1]] = "{}@{}".format("string", result)

        return 0

    def StrLenInstruction(self, args):
        if len(args) != 2 or not isVar(args[0]) or not isSymb(args[1]):
            return 32

        arg1 = args[0].text.split('@', maxsplit=1)
        frame1 = self.data[arg1[0]]
        if frame1 is None:
            return 55
        try:
            noneTest = frame1[arg1[1]]
        except KeyError:
            return 54

        op1 = ""

        if isConst(args[1]):
            if not args[1].attrib['type'] == "string":
                return 53
            op1 = args[1].text
        else:
            arg2 = args[1].text.split('@', maxsplit=1)
            frame2 = self.data[arg2[0]]
            if frame2 is None:
                return 55
            try:
                noneTest = frame2[arg2[1]]
            except KeyError:
                return 54
            if frame2[arg2[1]] is None:
                return 56
            value2 = frame2[arg2[1]].split('@', maxsplit=1)
            if len(value2) == 2 and value2[0] == "string":
                op1 = value2[1]
            else:
                return 53

        result = len(op1)
        self.data[arg1[0]][arg1[1]] = "{}@{}".format("int", int(result))

        return 0

    def GetCharInstruction(self, args):
        if len(args) != 3 or not isVar(args[0]) or not isSymb(args[1]) or not isSymb(args[2]):
            return 32

        arg1 = args[0].text.split('@', maxsplit=1)
        frame1 = self.data[arg1[0]]
        if frame1 is None:
            return 55
        try:
            noneTest = frame1[arg1[1]]
        except KeyError:
            return 54

        op1 = ""
        op2 = -1

        if isConst(args[1]):
            if not args[1].attrib['type'] == "string":
                return 53
            op1 = args[1].text
        else:
            arg2 = args[1].text.split('@', maxsplit=1)
            frame2 = self.data[arg2[0]]
            if frame2 is None:
                return 55
            try:
                noneTest = frame2[arg2[1]]
            except KeyError:
                return 54
            if frame2[arg2[1]] is None:
                return 56
            value2 = frame2[arg2[1]].split('@', maxsplit=1)
            if len(value2) == 2 and value2[0] == "string":
                op1 = value2[1]
            else:
                return 53

        if isConst(args[2]):
            if not args[2].attrib['type'] == "int":
                return 53
            op2 = int(args[2].text)
        else:
            arg3 = args[2].text.split('@', maxsplit=1)
            frame3 = self.data[arg3[0]]
            if frame3 is None:
                return 55
            try:
                noneTest = frame3[arg3[1]]
            except KeyError:
                return 54
            if frame3[arg3[1]] is None:
                return 56
            value3 = frame3[arg3[1]].split('@', maxsplit=1)
            if len(value3) == 2 and value3[0] == "int":
                op2 = int(value3[1])
            else:
                return 53

        if len(op1) > op2 and op2 >= 0:
            result = op1[op2]
            self.data[arg1[0]][arg1[1]] = "{}@{}".format("string", result)
        else:
            return 58

        return 0

    def SetCharInstruction(self, args):
        if len(args) != 3 or not isVar(args[0]) or not isSymb(args[1]) or not isSymb(args[2]):
            return 32

        op0 = ""
        op1 = -1
        op2 = ""

        arg1 = args[0].text.split('@', maxsplit=1)
        frame1 = self.data[arg1[0]]
        if frame1 is None:
            return 55
        try:
            noneTest = frame1[arg1[1]]
        except KeyError:
            return 54
        if frame1[arg1[1]] is None:
            return 56
        value1 = frame1[arg1[1]].split('@', maxsplit=1)
        if len(value1) == 2 and value1[0] == "string":
            op0 = value1[1]
        else:
            return 53

        if isConst(args[1]):
            if not args[1].attrib['type'] == "int":
                return 53
            op1 = int(args[1].text)
        else:
            arg2 = args[1].text.split('@', maxsplit=1)
            frame2 = self.data[arg2[0]]
            if frame2 is None:
                return 55
            try:
                noneTest = frame2[arg2[1]]
            except KeyError:
                return 54
            if frame2[arg2[1]] is None:
                return 56
            value2 = frame2[arg2[1]].split('@', maxsplit=1)
            if len(value2) == 2 and value2[0] == "int":
                op1 = int(value2[1])
            else:
                return 53

        if isConst(args[2]):
            if not args[2].attrib['type'] == "string":
                return 53
            op2 = args[2].text
        else:
            arg3 = args[2].text.split('@', maxsplit=1)
            frame3 = self.data[arg3[0]]
            if frame3 is None:
                return 55
            try:
                noneTest = frame3[arg3[1]]
            except KeyError:
                return 54
            if frame3[arg3[1]] is None:
                return 56
            value3 = frame3[arg3[1]].split('@', maxsplit=1)
            if len(value3) == 2 and value3[0] == "string":
                op2 = value3[1]
            else:
                return 53

        result = list(op0)
        if len(op2) != 0 and len(result) > op1 and op1 >= 0:
            result[op1] = op2[0]
        else:
            return 58
        result = "".join(result)

        self.data[arg1[0]][arg1[1]] = "{}@{}".format("string", result)

        return 0

    def TypeInstruction(self, args):
        if len(args) != 2 or not isVar(args[0]) or not isSymb(args[1]):
            return 32

        arg1 = args[0].text.split('@', maxsplit=1)
        frame1 = self.data[arg1[0]]
        if frame1 is None:
            return 55
        try:
            noneTest = frame1[arg1[1]]
        except KeyError:
            return 54

        type1 = ""

        if isConst(args[1]):
            type1 = args[1].attrib['type']
        else:
            arg2 = args[1].text.split('@', maxsplit=1)
            frame2 = self.data[arg2[0]]
            if frame2 is None:
                return 55
            try:
                noneTest = frame2[arg2[1]]
            except KeyError:
                return 54
            if frame2[arg2[1]] is None:
                type1 = ""
            else:
                value2 = frame2[arg2[1]].split('@', maxsplit=1)
                type1 = value2[0]

        self.data[arg1[0]][arg1[1]] = "{}@{}".format("string", type1)

        return 0

    def LabelInstruction(self, args):
        if len(args) != 1 or not isLabel(args[0]):
            return 32

        return 0

    def JumpInstruction(self, args):
        if len(args) != 1 or not isLabel(args[0]):
            return 32

        try:
            noneTest = self.data['labels'][args[0].text]
        except KeyError:
            return 52

        self.data['opcount'] = self.data['labels'][args[0].text]

        return 0

    def JumpIfEQInstruction(self, args):
        if len(args) != 3 or not isLabel(args[0]) or not isSymb(args[1]) or not isSymb(args[2]):
            return 32

        try:
            noneTest = self.data['labels'][args[0].text]
        except KeyError:
            return 52

        op1 = ""
        type1 = ""
        op2 = ""
        type2 = ""

        if isConst(args[1]):
            type1 = args[1].attrib['type']
            op1 = args[1].text
        else:
            arg2 = args[1].text.split('@', maxsplit=1)
            frame2 = self.data[arg2[0]]
            if frame2 is None:
                return 55
            try:
                noneTest = frame2[arg2[1]]
            except KeyError:
                return 54
            if frame2[arg2[1]] is None:
                return 56
            value2 = frame2[arg2[1]].split('@', maxsplit=1)
            type1 = value2[0]
            op1 = value2[1]

        if isConst(args[2]):
            type2 = args[2].attrib['type']
            op2 = args[2].text
        else:
            arg3 = args[2].text.split('@', maxsplit=1)
            frame3 = self.data[arg3[0]]
            if frame3 is None:
                return 55
            try:
                noneTest = frame3[arg3[1]]
            except KeyError:
                return 54
            if frame3[arg3[1]] is None:
                return 56
            value3 = frame3[arg3[1]].split('@', maxsplit=1)
            type2 = value3[0]
            op2 = value3[1]

        if type1 == "nil" or type2 == "nil":
            result = type1 == type2
            if result:
                self.data['opcount'] = self.data['labels'][args[0].text]
            return 0

        if type1 != type2:
            return 53

        if type1 == "int":
            op1 = int(op1)
            op2 = int(op2)

        result = op1 == op2

        if result:
            self.data['opcount'] = self.data['labels'][args[0].text]

        return 0

    def JumpIfNEQInstruction(self, args):
        if len(args) != 3 or not isLabel(args[0]) or not isSymb(args[1]) or not isSymb(args[2]):
            return 32

        try:
            noneTest = self.data['labels'][args[0].text]
        except KeyError:
            return 52

        op1 = ""
        type1 = ""
        op2 = ""
        type2 = ""

        if isConst(args[1]):
            type1 = args[1].attrib['type']
            op1 = args[1].text
        else:
            arg2 = args[1].text.split('@', maxsplit=1)
            frame2 = self.data[arg2[0]]
            if frame2 is None:
                return 55
            try:
                noneTest = frame2[arg2[1]]
            except KeyError:
                return 54
            if frame2[arg2[1]] is None:
                return 56
            value2 = frame2[arg2[1]].split('@', maxsplit=1)
            type1 = value2[0]
            op1 = value2[1]

        if isConst(args[2]):
            type2 = args[2].attrib['type']
            op2 = args[2].text
        else:
            arg3 = args[2].text.split('@', maxsplit=1)
            frame3 = self.data[arg3[0]]
            if frame3 is None:
                return 55
            try:
                noneTest = frame3[arg3[1]]
            except KeyError:
                return 54
            if frame3[arg3[1]] is None:
                return 56
            value3 = frame3[arg3[1]].split('@', maxsplit=1)
            type2 = value3[0]
            op2 = value3[1]

        if type1 == "nil" or type2 == "nil":
            result = type1 == type2
            if not result:
                self.data['opcount'] = self.data['labels'][args[0].text]
            return 0

        if type1 != type2:
            return 53

        if type1 == "int":
            op1 = int(op1)
            op2 = int(op2)

        result = op1 == op2

        if not result:
            self.data['opcount'] = self.data['labels'][args[0].text]

        return 0

    def ExitInstruction(self, args):
        if len(args) != 1 or not isSymb(args[0]):
            return 32

        op0 = -1

        if isConst(args[0]):
            if not args[0].attrib['type'] == "int":
                return 53
            op0 = int(args[0].text)
        else:
            arg = args[0].text.split('@', maxsplit=1)
            frame = self.data[arg[0]]
            if frame is None:
                return 55
            try:
                noneTest = frame[arg[1]]
            except KeyError:
                return 54
            if frame[arg[1]] is None:
                return 56
            value = frame[arg[1]].split('@', maxsplit=1)
            if len(value) == 2 and value[0] == "int":
                op0 = int(value[1])
            else:
                return 53

        if op0 >= 0 and op0 <= 49:
            exit(op0)

        return 57

    def DPrintInstruction(self, args):
        if len(args) != 1 or not isSymb(args[0]):
            return 32

        return 0

    def BreakInstruction(self, args):
        if len(args) != 0:
            return 32

        return 0


class Interpret:
    def __init__(self, args):
        files = self.argsCheck(args)

        sourceFile = files["source"].read()
        inputFile = files["input"]

        try:
            self.source = ET.fromstring(sourceFile)
        except:
            exit(31)

        self.instructions = self.prepareInstructions()
        if ret := self.headerCheck():
            exit(ret)
        if len(self.instructions) == 0:
            exit(0)

        GF = {}
        LF = None
        LFs = []
        TF = None
        calls = []
        datas = []
        labels = {}
        opcount = self.instructions[0][0]

        self.interpretData = {
            "GF": GF,
            "LF": LF,
            "LFs": LFs,
            "TF": TF,
            "calls": calls,
            "datas": datas,
            "labels": labels,
            "opcount": opcount,
            "input": inputFile
        }

    @staticmethod
    def argsCheck(args):
        if len(args) > 3 or len(args) < 2:
            exit(10)
        if "--help" in args:
            if len(args) == 2:
                print("Skript (interpret.py v jazyce Python 3.10) načte XML reprezentaci programu a tento program s využitím vstupu dle parametrů příkazové řádky interpretuje a generuje výstup.")
            else:
                print("Parametr --help nelze kombinovat s jinými argumenty.")
                exit(10)

        source = None
        inp = None

        try:
            for arg in args[1:]:
                if "--source" in arg:
                    filePath = arg.split("=")[1].strip("\"")
                    source = open(filePath, "r")
                elif "--input" in arg:
                    filePath = arg.split("=")[1].strip("\"")
                    inp = open(filePath, "r")
                else:
                    exit(10)
            if source is None:
                source = sys.stdin
            if inp is None:
                inp = sys.stdin
        except IOError:
            exit(11)

        result = {"source": source, "input": inp}
        return result

    def prepareInstructions(self):
        counter = 0
        result = []
        while counter < len(self.source):
            if self.source[counter].tag == "instruction" and self.source[counter].attrib.get('order') and len(self.source[counter].attrib) == 2:
                try:
                    order = int(self.source[counter].attrib['order'])
                except ValueError:
                    return 1
                i = 0
                while i < len(result):
                    if result[i][0] == order:
                        break
                    i += 1
                if order <= 0 or i != len(result):
                    return 1
                result.append([order, self.source[counter]])
            else:
                return 1
            counter += 1
        result.sort(key=lambda x: x[0])

        return result

    def headerCheck(self):
        if self.instructions == 1:
            return 32

        if self.source.attrib.get('language') and (self.source.attrib.get('language') != "IPPcode23" or len(self.source.attrib) > 3):
            return 32
        elif len(self.source.attrib) == 2 and (not self.source.attrib.get('name') and not self.source.attrib.get('description')):
            return 32
        elif len(self.source.attrib) == 3 and (not self.source.attrib.get('name') or not self.source.attrib.get('description')):
            return 32

    def run(self):
        result = 0
        end = False

        runner = instructionRunner(self.interpretData)
        result = getLabels(self.instructions, self.interpretData['labels'])
        if result != 0:
            return result

        while True:
            i = 0
            while i < len(self.instructions):
                if self.instructions[i][0] == self.interpretData["opcount"]:
                    break
                i += 1
            if self.instructions[i][1].attrib.get('opcode') is not None:
                args = []
                if len(self.instructions[i][1].findall("arg1")) > 1:
                    return 32
                args.append(self.instructions[i][1].find("arg1"))
                if args[0] is not None:
                    args.append(self.instructions[i][1].find("arg2"))
                    if len(self.instructions[i][1].findall("arg2")) > 1:
                        return 32
                if args[0] is not None and args[1] is not None:
                    args.append(self.instructions[i][1].find("arg3"))
                    if len(self.instructions[i][1].findall("arg3")) > 1:
                        return 32
                args = [i for i in args if i is not None]
                for arg in args:
                    if arg.text:
                        arg.text = arg.text.strip()
                result = runner.instructionMatch(self.instructions[i][1].attrib.get('opcode').lower(), args)
            else:
                result = 32

            if result != 0:
                break
            i = 0
            while i < len(self.instructions):
                if self.instructions[i][0] == self.interpretData["opcount"]:
                    try:
                        self.interpretData["opcount"] = self.instructions[i+1][0]
                        break
                    except IndexError:
                        end = True
                i += 1

            if end:
                break
        return result


# main
if __name__ == "__main__":
    interpret = Interpret(sys.argv)
    result = interpret.run()
    exit(result)
