from flask import url_for
from segue.json import SimpleJson

class BaseResponse(SimpleJson):
    @classmethod
    def create(cls, list_or_entity, *args, **kw):
        if isinstance(list_or_entity, list):
            return [ cls(e, *args, **kw) for e in list_or_entity ]
        if list_or_entity:
            return cls(list_or_entity, *args, **kw)

    def __init__(self):
        self.__dict__["$type"] = self.__class__.__name__

    def add_link(self, name, collection_or_entity, route='', **route_parms):
        if not hasattr(self, 'links'):
            self.links = {}
        if collection_or_entity is None: return
        self.links[name] = { "href": url_for(route, **route_parms) }
        if isinstance(collection_or_entity, int):
            self.links[name]['count'] = collection_or_entity
        elif isinstance(collection_or_entity, list):
            self.links[name]['count'] = len(collection_or_entity)


