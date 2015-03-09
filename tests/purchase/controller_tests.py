import json
import mockito

from ..support import SegueApiTestCase
from ..support.factories import *

class PurchaseControllerTestCases(SegueApiTestCase):
    def setUp(self):
        super(PurchaseControllerTestCases, self).setUp()
        self.mock_service = self.mock_controller_dep('purchases', 'service')
        self.mock_jwt(self.mock_owner)
