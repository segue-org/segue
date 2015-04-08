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
        mock_caravan = ValidCaravanFactory.build()
        mockito.when(self.mock_service).create(data, self.mock_owner).thenReturn(mock_caravan)

        response = self.jpost('/caravans', data=raw_json)

        mockito.verify(self.mock_service).create(data, self.mock_owner)
        self.assertEquals(response.status_code, 201)

    def test_gets_accounts_caravan(self):
        mock_caravan = ValidCaravanFactory.build()
        mockito.when(self.mock_service).get_one(123, self.mock_owner).thenReturn(mock_caravan)
        mockito.when(self.mock_service).get_one(456, self.mock_owner).thenRaise(NotAuthorized)

        response = self.jget('/caravans/123')
        content = json.loads(response.data)['resource']

        self.assertEquals(response.status_code, 200)
        self.assertEquals(content['name'], mock_caravan.name)
        self.assertEquals(content['city'], mock_caravan.city)

        response = self.jget('/caravans/456')
        self.assertEquals(response.status_code, 403)

