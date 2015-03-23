import random

class Hasher(object):
    def __init__(self, length=32):
        self.length = length

    def generate(self):
        value = random.getrandbits(self.length * 4)
        return "{0:0{1}X}".format(value, self.length)

