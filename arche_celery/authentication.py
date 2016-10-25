from pyramid.authentication import CallbackAuthenticationPolicy
from pyramid.interfaces import IAuthenticationPolicy
from zope.interface import implementer


@implementer(IAuthenticationPolicy)
class CeleryWorkerAuthenticationPolicy(CallbackAuthenticationPolicy):
    """ Celery workers should fetch userid from the user who initiated the task
    """

    def __init__(self):
        pass

    def remember(self, request, userid, **kw):
        """ Workers never login
        """
        raise NotImplementedError()

    def forget(self, request):
        """ Workers never logout"""
        raise NotImplementedError()

    def unauthenticated_userid(self, request):
        return getattr(request, '_celery_userid', None)
