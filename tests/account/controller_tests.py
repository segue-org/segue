import json
import mockito

from werkzeug.exceptions import NotFound

from segue.account import AccountController, AccountService, Account, Signer
from segue.errors import SegueValidationError, InvalidLogin, EmailAlreadyInUse

from support.factories import *
from support import SegueApiTestCase, hashie


class AccountControllerTestCases(SegueApiTestCase):
    def setUp(self):
        super(AccountControllerTestCases, self).setUp()
        self.mock_service = self.mock_controller_dep('accounts', 'service')
        self.mock_controller_dep('sessions', 'service', self.mock_service)

    def _build_validation_error(self):
        error_1 = hashie(validator='minLength', relative_path=['field']);
        error_2 = hashie(validator='maxLength', relative_path=['other']);
        return SegueValidationError([error_1, error_2])

    def test_invalid_entities_become_422_error(self):
        data = { "arbitrary": "json that will be mocked out anyway" }
        raw_json = json.dumps(data)
        validation_error = self._build_validation_error()
        mockito.when(self.mock_service).create(data).thenRaise(validation_error)

        response = self.jpost('/accounts', data=raw_json)
        errors = json.loads(response.data)['errors']

        self.assertEquals(errors[0]['field'], 'field')
        self.assertEquals(errors[1]['field'], 'other')
        self.assertEquals(response.status_code, 422)
        self.assertEquals(response.content_type, 'application/json')

    def test_json_input_is_sent_to_service_for_creation(self):
        data = { "arbitrary": "json that will be mocked out anyway" }
        raw_json = json.dumps(data)
        mockito.when(self.mock_service).create(data).thenReturn('bla')

        response = self.jpost('/accounts', data=raw_json)

        mockito.verify(self.mock_service).create(data)
        self.assertEquals(response.status_code, 201)

    def test_valid_login_works_and_returns_a_token(self):
        auth_response = { 'token': 'token', 'account': { 'email': 'email', 'id': 123, 'role': 'role' } }
        data = { "email": "email@example.com", "password": "12345" }
        raw_json = json.dumps(data)
        mockito.when(self.mock_service).login(**data).thenReturn(auth_response);

        response = self.jpost('/sessions', data=raw_json)
        parsed_response = json.loads(response.data)

        mockito.verify(self.mock_service).login(**data)
        self.assertEquals(parsed_response, auth_response)
        self.assertEquals(response.status_code, 200)

    def test_bad_login_returns_400(self):
        data = { "email": "email@example.com", "password": "12345" }
        raw_json = json.dumps(data)
        mockito.when(self.mock_service).login(**data).thenRaise(InvalidLogin);

        response = self.jpost('/sessions', data=raw_json)
        errors   = json.loads(response.data)['errors']

        mockito.verify(self.mock_service).login(**data)
        self.assertEquals(errors, [ "bad login" ])
        self.assertEquals(response.status_code, 400)

    def test_create_account(self):
        data = { "email": "email@example.com", "password": "12345" }
        raw_json = json.dumps(data)
        mock_account = ValidAccountFactory.create()
        mockito.when(self.mock_service).create(data).thenReturn(mock_account);

        response = self.jpost('/accounts', data=raw_json)
        content  = json.loads(response.data)['resource']

        self.assertEquals(content['email'], mock_account.email)


