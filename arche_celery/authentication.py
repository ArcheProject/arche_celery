from arche.security import groupfinder
from pyramid.authentication import CallbackAuthenticationPolicy
from pyramid.interfaces import IAuthenticationPolicy
from pyramid.threadlocal import get_current_registry
from zope.interface import implementer


@implementer(IAuthenticationPolicy)
class CeleryWorkerAuthenticationPolicy(CallbackAuthenticationPolicy):
    """ Celery workers should fetch userid from the user who initiated the task
    """

    def __init__(self, callback = None):
        self.callback = callback

    def remember(self, request, userid, **kw):
        """ Workers never login
        """
        raise NotImplementedError()

    def forget(self, request):
        """ Workers never logout"""
        raise NotImplementedError()

    def unauthenticated_userid(self, request):
        return getattr(request, '_celery_userid', None)


def worker_auth(registry):
    """ Should only be run by the worker!
    """
    if registry is None:
        registry=get_current_registry()
    policy = CeleryWorkerAuthenticationPolicy(callback=groupfinder)
    registry.registerUtility(policy, IAuthenticationPolicy)
