import json
import mockito

from werkzeug.exceptions import NotFound

from segue.account import AccountController, AccountService, Account, Signer
from segue.errors import SegueValidationError

from support import SegueApiTestCase, ValidAccountFactory, InvalidAccountFactory, hashie

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

class AccountServiceTestCases(SegueApiTestCase):
    def setUp(self):
        super(AccountServiceTestCases, self).setUp()
        self.mock_signer = mockito.Mock()
        self.service = AccountService(signer=self.mock_signer)

    def test_invalid_account_raises_validation_error(self):
        account = InvalidAccountFactory.build().to_json(all_fields=True)

        with self.assertRaises(SegueValidationError):
            self.service.create(account)

    def test_create_and_retrieve_of_valid_account(self):
        account = ValidAccountFactory.build().to_json(all_fields=True)
        account['password'] = 'password' # factory-boy can't keep SQLAlchemy from swallowing the value =/

        saved = self.service.create(account)
        retrieved = self.service.get_one(saved.id)

        self.assertEquals(saved, retrieved)

    def test_login_given_valid_credential(self):
        account = ValidAccountFactory.build().to_json(all_fields=True)
        account['password'] = 'password' # factory-boy can't keep SQLAlchemy from swallowing the value =/
        mockito.when(self.mock_signer).sign(account).thenReturn()
        saved = self.service.create(account)

        result = self.service.login(email=account['email'], password="password")

        mockito.verify(self.mock_signer).sign(account)

class AccountControllerTestCases(SegueApiTestCase):
    def setUp(self):
        super(AccountControllerTestCases, self).setUp()
        self.mock_service = self.mock_controller_dep('accounts', 'service')
        self.mock_controller_dep('sessions', 'service', self.mock_service)

    def _build_validation_error(self):
        error_1 = hashie(message="m1", schema_path=["1","2"])
        error_2 = hashie(message="m2", schema_path=["3","4"])

        return SegueValidationError([error_1, error_2])

    def test_invalid_entities_become_400_error(self):
        data = { "arbitrary": "json that will be mocked out anyway" }
        raw_json = json.dumps(data)
        validation_error = self._build_validation_error()
        mockito.when(self.mock_service).create(data).thenRaise(validation_error)

        response = self.jpost('/account', data=raw_json)
        errors = json.loads(response.data)['errors']

        self.assertEquals(errors['1.2'], 'm1')
        self.assertEquals(errors['3.4'], 'm2')
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.content_type, 'application/json')

    def test_json_input_is_sent_to_service_for_creation(self):
        data = { "arbitrary": "json that will be mocked out anyway" }
        raw_json = json.dumps(data)
        mockito.when(self.mock_service).create(data).thenReturn('bla')

        response = self.jpost('/account', data=raw_json)

        mockito.verify(self.mock_service).create(data)
        self.assertEquals(response.status_code, 201)

    def test_valid_login_works_and_returns_a_token(self):
        auth_response = { 'token': 'token', 'account': { 'email': 'email', 'id': 123, 'role': 'role' } }
        data = { "email": "email@example.com", "password": "12345" }
        raw_json = json.dumps(data)
        mockito.when(self.mock_service).login(**data).thenReturn(auth_response);

        response = self.jpost('/session', data=raw_json)
        parsed_response = json.loads(response.data)

        mockito.verify(self.mock_service).login(**data)
        self.assertEquals(parsed_response, auth_response)
        self.assertEquals(response.status_code, 200)
