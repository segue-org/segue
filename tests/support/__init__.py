import unittest
import mockito

import segue, segue.core

import settings

from factories import *
from hashie import hashie

class SegueApiTestCase(unittest.TestCase):
    def setUp(self):
        super(SegueApiTestCase, self).setUp()

        self.app = segue.Application(settings_override=settings)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        segue.core.db.create_all()

    def tearDown(self):
        super(SegueApiTestCase, self).tearDown()
        segue.core.db.drop_all()
        self.app_context.pop()

    def mock_controller_dep(self, blueprint, prop, replacement = None):
        if not replacement:
            replacement = mockito.Mock()
        setattr(self.app.blueprints[blueprint].controller, prop, replacement)
        return replacement

    def jpost(self, *args, **kw):
        return self.jrequest(self.client.post, *args, **kw)

    def jget(self, *args, **kw):
        return self.jrequest(self.client.get, *args, **kw)

    def jrequest(self, method, *args, **kw):
        kw.setdefault('content_type', 'application/json')
        return method(*args, **kw)
