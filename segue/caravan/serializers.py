from ..json import SQLAlchemyJsonSerializer

class CaravanJsonSerializer(SQLAlchemyJsonSerializer):
    _serializer_name = 'normal'

class CaravanInviteJsonSerializer(SQLAlchemyJsonSerializer):
    _serializer_name = 'normal'
    def serialize_child(self, child):
        return dict(caravan='CaravanJsonSerializer').get(child, False)

class ShortCaravanInviteJsonSerializer(CaravanInviteJsonSerializer):
    _serializer_name = 'short'

    def hide_field(self, child):
        return child not in ['name', 'recipient', 'status']
    def serialize_child(self, child):
        return False;



