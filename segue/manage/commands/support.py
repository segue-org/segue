import colorama
import codecs
import sys

F = colorama.Fore
B = colorama.Back
LINE = "\n"

def init_command():
    sys.stdout = codecs.open("/dev/stdout", "w", "utf-8")
    colorama.init()
