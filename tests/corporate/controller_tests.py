import json
import mockito

from segue.errors import NotAuthorized

from ..support import SegueApiTestCase
from ..support.factories import *

class CorporateControllerTestCases(SegueApiTestCase):
    def setUp(self):
        super(CorporateControllerTestCases, self).setUp()
        self.mock_service = self.mock_controller_dep('corporates', 'service')
        self.mock_owner   = self.mock_controller_dep('corporates', 'current_user', ValidAccountFactory.create())
        self.mock_jwt(self.mock_owner)

    def test_json_input_is_sent_to_service_for_creation(self):
        data = { "arbitrary": "json that will be mocked out anyway" }
        raw_json = json.dumps(data)
        mock_corporate = ValidCorporateFactory.create()
        mockito.when(self.mock_service).create(data, self.mock_owner).thenReturn(mock_corporate)

        response = self.jpost('/corporates', data=raw_json)

        mockito.verify(self.mock_service).create(data, self.mock_owner)
        self.assertEquals(response.status_code, 201)

    def test_gets_corporate_by_id(self):
        mock_corporate = ValidCorporateFactory.create()
        mockito.when(self.mock_service).get_one(123, self.mock_owner).thenReturn(mock_corporate)
        mockito.when(self.mock_service).get_one(456, self.mock_owner).thenRaise(NotAuthorized)
        mockito.when(self.mock_service).get_one(666, self.mock_owner).thenReturn(None)

        response = self.jget('/corporates/123')
        content = json.loads(response.data)['resource']

        self.assertEquals(response.status_code, 200)
        self.assertEquals(content['name'], mock_corporate.name)
        self.assertEquals(content['city'], mock_corporate.city)

        response = self.jget('/corporates/456')
        self.assertEquals(response.status_code, 403)

        response = self.jget('/corporates/666')
        self.assertEquals(response.status_code, 404)

    def test_gets_corporate_by_owner(self):
        mock_corporate = ValidCorporateFactory.create()
        mockito.when(self.mock_service).get_by_owner(789, self.mock_owner).thenReturn(mock_corporate)
        mockito.when(self.mock_service).get_by_owner(890, self.mock_owner).thenRaise(NotAuthorized)
        mockito.when(self.mock_service).get_by_owner(666, self.mock_owner).thenReturn(None)

        response = self.jget('/corporates', query_string={'owner_id': u'789'})
        content = json.loads(response.data)['resource']

        self.assertEquals(response.status_code, 200)
        self.assertEquals(content['name'], mock_corporate.name)
        self.assertEquals(content['city'], mock_corporate.city)

        response = self.jget('/corporates', query_string={'owner_id': u'890'})
        self.assertEquals(response.status_code, 403)

        response = self.jget('/corporates/666')
        self.assertEquals(response.status_code, 404)
