import json
import mockito

from segue.account.jwt import Signer
from segue.account.models import TokenJsonSerializer

from ..support import SegueApiTestCase
from ..support.factories import *

class SignerTestsCases(SegueApiTestCase):
    def test_wraps_account_with_jwt(self):
        mock_credentials = ValidAccountFactory.build()
        mock_token   = "token"
        mock_json = { 123: 456 }

        mock_serializer = mockito.Mock()
        mock_jwt = mockito.Mock()

        mockito.when(mock_serializer).emit_json_for(mock_credentials).thenReturn(mock_json)
        mockito.when(mock_jwt).encode_callback(mock_json).thenReturn(mock_token)

        signer = Signer(jwt=mock_jwt, serializer=mock_serializer)
        result = signer.sign(mock_credentials)

        self.assertEquals(result['credentials'], mock_credentials)
        self.assertEquals(result['token'],   mock_token)


