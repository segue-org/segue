import json
import mockito

from werkzeug.exceptions import NotFound

from segue.account import AccountController, AccountService, Account, Signer
from segue.errors import SegueValidationError, InvalidLogin, EmailAlreadyInUse

from ..support.factories import *
from ..support import SegueApiTestCase, hashie

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

    def test_creation_of_duplicated_account(self):
        existing = ValidAccountFactory.create()
        new_one = ValidAccountFactory.build(email=existing.email).to_json(all_fields=True)
        new_one['password'] = 'password';

        with self.assertRaises(EmailAlreadyInUse):
            self.service.create(new_one)

    def test_login_given_valid_credential(self):
        account = self.create_from_factory(ValidAccountFactory, password="right")

        result = self.service.login(email=account.email, password="right")
        mockito.verify(self.mock_signer).sign(account)

        with self.assertRaises(InvalidLogin):
            self.service.login(email=account.email, password="wrong")

        with self.assertRaises(InvalidLogin):
            self.service.login(email='random-email', password="right")
