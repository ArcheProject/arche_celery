import transaction
from celery.signals import task_failure
from celery.signals import task_postrun
from celery.signals import task_prerun
from celery.signals import task_revoked
from celery.signals import task_success
from celery.signals import worker_init
from pyramid.path import DottedNameResolver
from pyramid.scripting import prepare
from pyramid.threadlocal import get_current_registry
from pyramid.threadlocal import manager as threadlocal_manager

from arche_celery import logger


@worker_init.connect
def worker_started(signal, sender):
    registry=get_current_registry()
    resolver=DottedNameResolver()
    worker_auth=resolver.resolve(registry.settings['arche_celery.worker_auth'])
    worker_auth(registry)


@task_prerun.connect
def prerun_start(task_id, task, signal, sender, args, kwargs):
    """ Populates kwargs
        A context_uid or context_path will be resolved as context instead.
    """
    logger.debug('signal prerun for %r' % task_id)
    task_env = prepare()
    request = task_env['request']
    if hasattr(request, 'set_celery_userid'):

        if 'authenticated_userid' in kwargs:
            request.set_celery_userid(kwargs['authenticated_userid'])
            logger.debug("authenticated_userid set to %s", kwargs['authenticated_userid'])
        else:
            logger.debug("authenticated_userid wasn't sent as a kwarg to task - so it will be None.")
    root = request.root
    context = None
    context_uid = kwargs.pop('context_uid', None)
    if context_uid:
        context = request.resolve_uid(context_uid)
    if context:
        request.context = context
    else:
        request.context = root
    logger.debug('context is %r' % context)
    kwargs.update(root=root, request=request)
    if context:
        kwargs['context'] = context
    transaction.begin()


@task_success.connect
def commit_task_results(sender, kwargs = {}, **kw):
    logger.debug('signal success for %r' % sender)
    manager = transaction.manager
    if manager.isDoomed():
        manager.abort()
        logger.debug("Transaction manager says transaction is doomed, aborting commit.")
    else:
        manager.commit()
        logger.debug("Transaction manager committing.")


@task_postrun.connect
def postrun_end_request(sender, task, kwargs = {}, **kw):
    logger.debug('signal postrun for %r' % task)
    request = kwargs.get('request', None)
    if request and request.finished_callbacks:
        request._process_finished_callbacks()
    threadlocal_manager.pop()


#@task_retry.connect
#def will_retry(**kw):
#    print "I WILL RETRY NOW"


@task_failure.connect
@task_revoked.connect
def abort_commit(kwargs = {}, **kw):
    logger.debug('signal retry or failure, transaction aborted.')
    transaction.manager.abort()


def includeme(config):
    logger.debug("Initialize signal read")
