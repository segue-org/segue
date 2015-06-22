from sqlalchemy import or_

class FilterStrategies(object):
    def needle(self, needle, as_user=None, **kw):
        if not needle and len(kw) == 0: return []
        universe = self.given(**kw)

        filters = []
        joins = []
        for method_name in dir(self):
            if not method_name.startswith("by_"): continue
            if not needle: continue
            method = getattr(self, method_name)
            criterium = method(needle)
            if criterium is None: continue
            filters.append(criterium)

        if as_user and as_user.role != 'admin':
            universe.append(self.enforce_user(as_user))

        universe.append(or_(*filters))

        return universe

    def given(self, as_user=None, **criteria):
        result = []
        for key, value in criteria.items():
            method = getattr(self, "by_"+key)
            result.append(method(value, as_user=as_user))
        if as_user and as_user.role != 'admin':
            result.append(self.enforce_user(as_user))
        return result

    def joins_for(self, queryset, **criteria):
        result = queryset
        for key, value in criteria.items():
            method = getattr(self, "join_for_"+key, None)
            if not method: continue
            result = method(result)
        return result

    def all_joins(self, queryset):
        result = queryset
        for method_name in dir(self):
            if not method_name.startswith("join_for_"): continue
            method = getattr(self, method_name)
            result = method(result)
        return result
