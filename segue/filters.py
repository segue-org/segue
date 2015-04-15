from sqlalchemy import or_

class FilterStrategies(object):
    def needle(self, needle, as_user=None):
        if not needle: return []
        result = []
        for method_name in dir(self):
            if not method_name.startswith("by_"): continue
            method = getattr(self, method_name)
            filter_ = method(needle)
            if filter_ is None: continue
            result.append(filter)

        if not as_user or as_userl.role == 'admin':
            return or_(*result)
        else:
            return [ self.enforce_user(as_user), or_(*result)  ]

    def given(self, as_user=None, **criteria):
        result = []
        for key, value in criteria.items():
            method = getattr(self, "by_"+key)
            result.append(method(value, as_user=as_user))
        if as_user and as_user.role != 'admin':
            result.append(self.enforce_user(as_user))
        return result
