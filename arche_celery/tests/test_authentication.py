from unittest import TestCase

from pyramid import testing
from pyramid.request import apply_request_extensions


class WorkerAuthTests(TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    @property
    def _cut(self):
        from arche_celery.authentication import CeleryWorkerAuthenticationPolicy
        return CeleryWorkerAuthenticationPolicy

    def test_remember_forget_blocked(self):
        obj = self._cut()
        self.assertRaises(NotImplementedError, obj.remember, None, None)
        self.assertRaises(NotImplementedError, obj.forget, None)

    def test_unauthenticated_userid(self):
        request = testing.DummyRequest()
        request._celery_userid = 'hello'
        obj = self._cut()
        self.assertEqual(obj.unauthenticated_userid(request), 'hello')
        self.assertEqual(obj.authenticated_userid(request), 'hello')

    def test_integration(self):
        from arche_celery.authentication import worker_auth
        worker_auth(self.config.registry)
        request = testing.DummyRequest()
        apply_request_extensions(request)
        request._celery_userid = 'hello'
        self.assertEqual(request.unauthenticated_userid, 'hello')
        self.assertEqual(request.authenticated_userid, 'hello')
