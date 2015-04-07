import json
import mockito

from ..support import SegueApiTestCase
from ..support.factories import *

class PurchaseControllerTestCases(SegueApiTestCase):
    def setUp(self):
        super(PurchaseControllerTestCases, self).setUp()
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
