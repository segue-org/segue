from ..json import SQLAlchemyJsonSerializer

class CaravanJsonSerializer(SQLAlchemyJsonSerializer):
    _serializer_name = 'normal'

