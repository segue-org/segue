class hashie(dict):
    def __getattr__(self, name):
        return self.__getitem__(name)

    def __setattr__(self, name, value):
        return self.__setitem__(name, value)

    def __getitem__(self, item):
        if not self.has_key(item):
            self.__setitem__(item, hashie())
        return super(hashie, self).__getitem__(item)

    def has_key(self, key, *keys):
        if len(keys) == 0: return super(hashie, self).has_key(key)
        if super(hashie, self).has_key(key):
            return getattr(super(hashie, self).__getitem__(key), 'has_key', lambda x: False)(keys[0], *keys[1:])
        else:
            return False
