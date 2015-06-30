import random

class Hasher(object):
    def __init__(self, length=32, prefix=None):
        self.length = length
        self.prefix = prefix

    def generate(self):
        value = random.getrandbits(self.length * 4)
        return "{2}{0:0{1}X}".format(value, self.length, self.prefix)
