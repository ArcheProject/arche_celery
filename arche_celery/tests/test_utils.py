from unittest import TestCase

from arche.testing import barebone_fixture
from pyramid import testing
from pyramid.config import global_registries
from pyramid.request import apply_request_extensions

from arche_celery.testing import CONFIG_INI_TESTS
from arche_celery.testing import dummy_task


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
        apply_request_extensions(request)
        self.config.begin(request)
        global_registries.add(self.config.registry)
        def _root_fact(*args):
            return self.root
        self.config.set_root_factory(_root_fact)

    def tearDown(self):
        testing.tearDown()

    @property
    def _fut(self):
        from arche_celery.utils import build_status
        return build_status

    def test_single_task(self):
        self.assertEqual(
            self._fut(dummy_task.delay()),
            {'all_ready': True, 'completed': 1,
             'state': 'SUCCESS', 'ready': True, 'total': 1,
             'children': {'completed': 0, 'total': 0}}
        )

#FIXME: Tests with children won't work on Eager without result storage
    # def test_with_children(self):
    #     dummy_with_children.delay()
    #     self.assertEqual(
    #         self._fut(dummy_with_children.delay()),
    #         {'all_ready': True, 'completed': 1,
    #          'state': 'SUCCESS', 'ready': True, 'total': 1,
    #          'children': {'completed': 0, 'total': 0}}
    #     )
