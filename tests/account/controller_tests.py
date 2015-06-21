import json
import mockito

from werkzeug.exceptions import NotFound

from segue.errors import SegueValidationError

from segue.account.controllers import AccountController
from segue.account.errors import InvalidLogin, EmailAlreadyInUse, NotAuthorized, NoSuchAccount, InvalidResetPassword

from ..support.factories import *
from ..support import SegueApiTestCase, hashie


class AccountControllerTestCases(SegueApiTestCase):
    def setUp(self):
        super(AccountControllerTestCases, self).setUp()
        self.mock_service = self.mock_controller_dep('accounts', 'service')
        self.mock_controller_dep('sessions', 'service', self.mock_service)
        self.mock_owner = self.mock_controller_dep('proposals', 'current_user', ValidAccountFactory.create())

        self.mock_jwt(self.mock_owner)

    def _build_validation_error(self):
        error_1 = hashie(validator='minLength', relative_path=['xonga']);
        error_2 = hashie(validator='maxLength', relative_path=['other']);
        return SegueValidationError([error_1, error_2])

    def test_invalid_entities_become_422_error(self):
        data = { "arbitrary": "json that will be mocked out anyway" }
        raw_json = json.dumps(data)
        validation_error = self._build_validation_error()
        mockito.when(self.mock_service).create(data).thenRaise(validation_error)

        response = self.jpost('/accounts', data=raw_json)
        errors = json.loads(response.data)['errors']

        self.assertEquals(errors[0]['field'], 'xonga')
        self.assertEquals(errors[1]['field'], 'other')
        self.assertEquals(response.status_code, 422)
        self.assertEquals(response.content_type, 'application/json')

    def test_existing_email_becomes_422_error(self):
        data = { "arbitrary": "json that will be mocked out anyway" }
        raw_json = json.dumps(data)
        mockito.when(self.mock_service).create(data).thenRaise(EmailAlreadyInUse('le@email'))

        response = self.jpost('/accounts', data=raw_json)
        errors = json.loads(response.data)['errors']

        self.assertEquals(len(errors), 1)
        self.assertEquals(errors[0]['field'], 'email')
        self.assertEquals(errors[0]['label'], 'already_in_use')
        self.assertEquals(errors[0]['value'], 'le@email')
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
        self.assertEquals(errors['message'], "bad login")
        self.assertEquals(response.status_code, 400)

    def test_create_account(self):
        data = { "email": "email@example.com", "password": "12345" }
        raw_json = json.dumps(data)
        mock_account = ValidAccountFactory.create()
        mockito.when(self.mock_service).create(data).thenReturn(mock_account);

        response = self.jpost('/accounts', data=raw_json)
        content  = json.loads(response.data)['resource']

        self.assertEquals(content['email'], mock_account.email)

    def test_get_one_account_valid_owner(self):
        mock_account = ValidAccountFactory.build()
        mockito.when(self.mock_service).get_one(123, by=self.mock_owner).thenReturn(mock_account)

        response = self.jget('/accounts/123')
        content = json.loads(response.data)['resource']

        self.assertEquals(response.status_code, 200)
        self.assertEquals(content['email'], mock_account.email)

    def test_get_one_account_invalid_owner(self):
        other_owner = ValidAccountFactory.build()
        self.mock_jwt(other_owner)
        mockito.when(self.mock_service).get_one(456, by=other_owner).thenRaise(NotAuthorized)

        response = self.jget('/accounts/456')

        self.assertEquals(response.status_code, 403)

    def test_ask_for_reset_password(self):
        mockito.when(self.mock_service).ask_reset('email@example.com').thenReturn(None)
        mockito.when(self.mock_service).ask_reset('other@example.com').thenRaise(NoSuchAccount)

        response = self.jpost('/accounts/reset', data=json.dumps({'email':'email@example.com'}))
        self.assertEquals(response.data, '')
        self.assertEquals(response.status_code, 200)

        response = self.jpost('/accounts/reset', data=json.dumps({'email':'other@example.com'}))
        self.assertEquals(response.status_code, 404)

    def test_proceed_with_reset_password(self):
        account = self.build_from_factory(ValidAccountFactory, id=1234)
        reset = self.build_from_factory(ValidResetFactory, account=account)
        mockito.when(self.mock_service).get_reset(1234, 'ABCD1234').thenReturn(reset)
        mockito.when(self.mock_service).get_reset(1234, 'XXXX9999').thenRaise(InvalidResetPassword)

        response = self.client.get('/accounts/1234/reset/ABCD1234')
        destination = response.headers['Location']
        self.assertEquals(response.status_code, 302)
        self.assertEquals(destination, 'http://localhost:9000/#/account/1234/reset/ABCD1234')

        response = self.client.get('/accounts/1234/reset/XXXX9999')
        self.assertEquals(response.status_code, 400)

    def test_perform_password_reset(self):
        data = { "hash_code": "ABCD1234", "password": "12345" }
        raw_json = json.dumps(data)
        reset = self.build_from_factory(ValidResetFactory)
        mockito.when(self.mock_service).perform_reset(1234, 'ABCD1234', '12345').thenReturn(reset)
        mockito.when(self.mock_service).perform_reset(7890, 'XXXX9999', '12345').thenRaise(InvalidResetPassword)

        response = self.jpost('/accounts/1234/reset/ABCD1234', data=raw_json)
        content = json.loads(response.data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(content['email'], reset.account.email)
