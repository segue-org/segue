import json
import mockito

from werkzeug.exceptions import NotFound

from segue.account import AccountController, AccountService, Account, Signer
from segue.errors import SegueValidationError, InvalidLogin, EmailAlreadyInUse, NotAuthorized

from ..support.factories import *
from ..support import SegueApiTestCase, hashie

class AccountServiceTestCases(SegueApiTestCase):
    def setUp(self):
        super(AccountServiceTestCases, self).setUp()
        self.mock_signer = mockito.Mock()
        self.service = AccountService(signer=self.mock_signer)

    def test_invalid_account_raises_validation_error(self):
        account = InvalidAccountFactory.build().to_json()

        with self.assertRaises(SegueValidationError):
            self.service.create(account)

    def test_create_and_retrieve_of_valid_account(self):
        account = ValidAccountFactory.build().to_json()
        account['password'] = 'password' # factory-boy can't keep SQLAlchemy from swallowing the value =/

        saved = self.service.create(account)
        unchecked_retrieval = self.service.get_one(saved.id, check_owner=False)

        checked_retrieval = self.service.get_one(saved.id, by=unchecked_retrieval)

        self.assertEquals(saved, unchecked_retrieval)
        self.assertEquals(saved, checked_retrieval)

        with self.assertRaises(NotAuthorized):
            self.service.get_one(saved.id)

    def test_modify(self):
        account = self.create_from_factory(ValidAccountFactory)
        other_account = self.create_from_factory(ValidAccountFactory)

        new_data = account.to_json()
        new_data['resume'] = 'a big hueon'

        self.service.modify(account.id, new_data, by=account)
        retrieved = self.service.get_one(account.id, by=account)

        self.assertEquals(retrieved.resume, 'a big hueon')

        with self.assertRaises(NotAuthorized):
            self.service.modify(account.id, new_data, by=other_account)

    def test_creation_of_duplicated_account(self):
        existing = ValidAccountFactory.create()
        new_one = ValidAccountFactory.build(email=existing.email).to_json()
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

    def test_lookup_by_email(self):
        account1 = self.create_from_factory(ValidAccountFactory, email='misinfin@example.com')
        account2 = self.create_from_factory(ValidAccountFactory, email='xaxanga@example.com')
        account3 = self.create_from_factory(ValidAccountFactory, email='vetusto@example.com')

        result = self.service.lookup('xaxa')
        self.assertEquals(len(result), 1)

        result = self.service.lookup('@example.com')
        self.assertEquals(len(result), 3)
