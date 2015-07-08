import colorama
import codecs
import sys

F = colorama.Fore
B = colorama.Back
LINE = "\n"

def init_command():
    sys.stdout = codecs.getwriter('utf8')(sys.stdout)
    sys.stderr = codecs.getwriter('utf8')(sys.stderr)
    colorama.init()
    return sys.stdout

def u(value):
    return (value or '').encode("utf-8")
