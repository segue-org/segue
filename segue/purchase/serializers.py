from ..json import SQLAlchemyJsonSerializer

class BuyerJsonSerializer(SQLAlchemyJsonSerializer):
    _serializer_name = 'normal'

class PurchaseJsonSerializer(SQLAlchemyJsonSerializer):
    _serializer_name = 'normal'
    _child_serializers = dict(payments='PaymentJsonSerializer',
                              product='ProductJsonSerializer',
                              customer='AccuntJsonSerializer')
    def serialize_child(self, child):
        return self._child_serializers.get(child, False)

class ShortPurchaseJsonSerializer(SQLAlchemyJsonSerializer):
    _serializer_name = 'short'
    def serialize_child(self, child):
        return False
