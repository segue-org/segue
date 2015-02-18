from ..json import SQLAlchemyJsonSerializer

class ProposalJsonSerializer(SQLAlchemyJsonSerializer):
    _serializer_name = 'normal'
    _child_serializers = dict(owner='SafeAccountJsonSerializer',
                              track='TrackSerializer')
    def serialize_child(self, child):
        return self._child_serializers.get(child, False)

class ShortChildProposalJsonSerializer(ProposalJsonSerializer):
    _serializer_name = 'short_child'
    _child_serializers = dict(owner='SafeAccountJsonSerializer',
                              track='ShortTrackSerializer',
                              invites='ShortInviteJsonSerializer')

class InviteJsonSerializer(SQLAlchemyJsonSerializer):
    _serializer_name = 'normal'
    def serialize_child(self, child):
        return dict(proposal='ProposalJsonSerializer').get(child, False)

class ShortInviteJsonSerializer(InviteJsonSerializer):
    _serializer_name = 'short'
    def hide_field(self, child):
        return child not in ['name', 'recipient', 'status']
    def serialize_child(self, child):
        return False;

class SafeInviteJsonSerializer(InviteJsonSerializer):
    _serializer_name = 'safe'
    def hide_field(self, child):
        return child in ['recipient']


class TrackSerializer(SQLAlchemyJsonSerializer):
    _serializer_name = 'normal'

class ShortTrackSerializer(TrackSerializer):
    _serializer_name = 'short'
    def hide_field(self, child):
        return child in ['id','public']
