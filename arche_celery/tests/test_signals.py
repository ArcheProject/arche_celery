from unittest import TestCase

from arche.testing import barebone_fixture
from pyramid import testing
from pyramid.config import global_registries
from pyramid.interfaces import IAuthenticationPolicy
from pyramid.request import apply_request_extensions

from arche_celery.testing import CONFIG_INI_TESTS


class WorkerStartedTests(TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.registry.settings['arche_celery.ini'] = CONFIG_INI_TESTS

    def tearDown(self):
        testing.tearDown()

    @property
    def _fut(self):
        from arche_celery.signals import worker_started
        return worker_started

    def test_worker_started(self):
        from arche_celery.authentication import CeleryWorkerAuthenticationPolicy
        self.config.include('arche_celery')
        self._fut(None, None)
        policy = self.config.registry.getUtility(IAuthenticationPolicy)
        self.assertIsInstance(policy, CeleryWorkerAuthenticationPolicy)


class PrerunStartTests(TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('arche.testing')
        self.config.include('arche.testing.catalog')
        self.config.include('arche.testing.workflow')
        self.config.registry.settings['arche_celery.ini'] = CONFIG_INI_TESTS
        self.config.include('arche_celery')
        self.root = barebone_fixture(self.config)
        request = testing.DummyRequest()
        request.root = self.root
        apply_request_extensions(request)
        self.request = request
        self.config.begin(request)
        #Need to make registry accessible for worker.
        #This may change in pyramid
        global_registries.add(self.config.registry)
        def _root_fact(*args):
            return self.root
        self.config.set_root_factory(_root_fact)

    def tearDown(self):
        testing.tearDown()

    @property
    def _fut(self):
        from arche_celery.signals import prerun_start
        return prerun_start

    def test_celery_userid_not_set(self):
        kwargs = {}
        self._fut('task_id', None, None, None, [], kwargs)
        #Created request
        request = kwargs['request']
        self.assertEqual(getattr(request, '_celery_userid', None), None)

    def test_celery_userid_set(self):
        kwargs = {'authenticated_userid': 'frej'}
        self._fut('task_id', None, None, None, [], kwargs)
        #Created request
        request = kwargs['request']
        self.assertEqual(request._celery_userid, 'frej')

    def test_context_found_from_uid(self):
        from arche.api import User
        obj = User(uid = '123')
        self.root['user'] = obj
        kwargs = {'context_uid': '123'}
        self._fut('task_id', None, None, None, [], kwargs)
        self.assertEqual(obj, kwargs['context'])
