from ..json import SQLAlchemyJsonSerializer

class CorporateJsonSerializer(SQLAlchemyJsonSerializer):
    _serializer_name = 'normal'
    _child_serializers = dict(owner='SafeAccountJsonSerializer')
    def serialize_child(self, child):
        return self._child_serializers.get(child, False)

class CorporateInviteJsonSerializer(SQLAlchemyJsonSerializer):
    _serializer_name = 'normal'
    def serialize_child(self, child):
        return dict(corporate='CorporateJsonSerializer').get(child, False)

class ShortCorporateInviteJsonSerializer(CorporateInviteJsonSerializer):
    _serializer_name = 'short'

    def hide_field(self, child):
        return child not in ['name', 'recipient', 'document', 'status']
    def serialize_child(self, child):
        return False;



