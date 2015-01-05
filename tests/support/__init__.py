import unittest

import lib, lib.core

import settings

class SegueApiTestCase(unittest.TestCase):
    def setUp(self):
        super(SegueApiTestCase, self).setUp()

        self.app = lib.Application(settings_override=settings)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        lib.core.db.create_all()

    def tearDown(self):
        super(SegueApiTestCase, self).tearDown()
        lib.core.db.drop_all()
        self.app_context.pop()
