import json
import mockito

from segue.account import Signer

from support import SegueApiTestCase
from support.factories import *

class SignerTestsCases(SegueApiTestCase):
    def test_wraps_account_with_jwt(self):
        mock_account = ValidAccountFactory.build()
        mock_token   = "token"
        mock_jwt = mockito.Mock()
        mockito.when(mock_jwt).encode_callback(mock_account.to_json()).thenReturn(mock_token)

        signer = Signer(jwt=mock_jwt)
        result = signer.sign(mock_account)

        self.assertEquals(result['account'], mock_account)
        self.assertEquals(result['token'],   mock_token)


