import json
import mockito

from segue.errors import NotAuthorized

from ..support import SegueApiTestCase
from ..support.factories import *

class CaravanControllerTestCases(SegueApiTestCase):
    def setUp(self):
        super(CaravanControllerTestCases, self).setUp()
        self.mock_service = self.mock_controller_dep('caravans', 'service')
        self.mock_owner   = self.mock_controller_dep('caravans', 'current_user', ValidAccountFactory.create())
        self.mock_jwt(self.mock_owner)

    def test_json_input_is_sent_to_service_for_creation(self):
        data = { "arbitrary": "json that will be mocked out anyway" }
        raw_json = json.dumps(data)
        mock_caravan = ValidCaravanFactory.create()
        mockito.when(self.mock_service).create(data, self.mock_owner).thenReturn(mock_caravan)

        response = self.jpost('/caravans', data=raw_json)

        mockito.verify(self.mock_service).create(data, self.mock_owner)
        self.assertEquals(response.status_code, 201)

    def test_gets_caravan_by_id(self):
        mock_caravan = ValidCaravanFactory.create()
        mockito.when(self.mock_service).get_one(123, self.mock_owner).thenReturn(mock_caravan)
        mockito.when(self.mock_service).get_one(456, self.mock_owner).thenRaise(NotAuthorized)
        mockito.when(self.mock_service).get_one(666, self.mock_owner).thenReturn(None)

        response = self.jget('/caravans/123')
        content = json.loads(response.data)['resource']

        self.assertEquals(response.status_code, 200)
        self.assertEquals(content['name'], mock_caravan.name)
        self.assertEquals(content['city'], mock_caravan.city)

        response = self.jget('/caravans/456')
        self.assertEquals(response.status_code, 403)

        response = self.jget('/caravans/666')
        self.assertEquals(response.status_code, 404)

    def test_gets_caravan_by_owner(self):
        mock_caravan = ValidCaravanFactory.create()
        mockito.when(self.mock_service).get_by_owner(789, self.mock_owner).thenReturn(mock_caravan)
        mockito.when(self.mock_service).get_by_owner(890, self.mock_owner).thenRaise(NotAuthorized)
        mockito.when(self.mock_service).get_by_owner(666, self.mock_owner).thenReturn(None)

        response = self.jget('/caravans', query_string={'owner_id': u'789'})
        content = json.loads(response.data)['resource']

        self.assertEquals(response.status_code, 200)
        self.assertEquals(content['name'], mock_caravan.name)
        self.assertEquals(content['city'], mock_caravan.city)

        response = self.jget('/caravans', query_string={'owner_id': u'890'})
        self.assertEquals(response.status_code, 403)

        response = self.jget('/caravans/666')
        self.assertEquals(response.status_code, 404)


class CaravanInviteControllerTestCases(SegueApiTestCase):
    def setUp(self):
        super(CaravanInviteControllerTestCases, self).setUp()
        self.mock_service = self.mock_controller_dep('caravan_invites','service')
        self.mock_owner   = self.mock_controller_dep('caravan_invites', 'current_user', ValidAccountFactory.create())
        self.mock_jwt(self.mock_owner)

    def test_list_invites(self):
        mock_invite = ValidCaravanInviteFactory.build()
        mockito.when(self.mock_service).list(123, by=self.mock_owner).thenReturn([mock_invite])
        mockito.when(self.mock_service).list(456, by=self.mock_owner).thenRaise(NotAuthorized)

        response = self.jget('/caravans/123/invites')
        items = json.loads(response.data)['items']
        self.assertEquals(len(items), 1)
        self.assertEquals(items[0]['name'], mock_invite.name)

        response = self.jget('/caravans/456/invites')
        self.assertEquals(response.status_code, 403)

    def test_invite(self):
        data = { "email": "fulano@example.com" }
        raw_json = json.dumps(data)
        mock_invite = ValidCaravanInviteFactory.create()
        mockito.when(self.mock_service).create(123, data, by=self.mock_owner).thenReturn(mock_invite)
        mockito.when(self.mock_service).create(456, data, by=self.mock_owner).thenRaise(NotAuthorized)

        response = self.jpost('/caravans/123/invites', data=raw_json)
        content = json.loads(response.data)['resource']
        self.assertEquals(content['recipient'], mock_invite.recipient)

        response = self.jpost('/caravans/456/invites', data=raw_json)
        self.assertEquals(response.status_code, 403)

    def test_invite_check(self):
        mock_invite = ValidCaravanInviteFactory.create(hash='123ABC')
        mockito.when(self.mock_service).get_by_hash('123ABC').thenReturn(mock_invite)
        mockito.when(self.mock_service).get_by_hash('FFFFFF').thenReturn(None)

        response = self.jget('/caravans/123/invites/123ABC')
        self.assertEquals(response.status_code, 200)

        response = self.jget('/caravans/123/invites/FFFFFF')
        self.assertEquals(response.status_code, 404)
