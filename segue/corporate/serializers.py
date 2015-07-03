from ..json import SQLAlchemyJsonSerializer

class CorporateJsonSerializer(SQLAlchemyJsonSerializer):
    _serializer_name = 'normal'
    _child_serializers = dict(owner='SafeAccountJsonSerializer')
    def serialize_child(self, child):
        return self._child_serializers.get(child, False)

class CorporateEmployeeJsonSerializer(SQLAlchemyJsonSerializer):
    _serializer_name = 'normal'
    def serialize_child(self, child):
        return dict(corporate='CorporateJsonSerializer').get(child, False)

class ShortCorporateEmployeeJsonSerializer(CorporateEmployeeJsonSerializer):
    _serializer_name = 'short'

    def hide_field(self, child):
        return child not in ['name', 'badge_name', 'email', 'document', 'status']
    def serialize_child(self, child):
        return False;
