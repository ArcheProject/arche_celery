import transaction
from celery.signals import task_failure
from celery.signals import task_postrun
from celery.signals import task_prerun
from celery.signals import task_retry
from celery.signals import task_success
from celery.signals import worker_init
from pyramid.interfaces import IAuthenticationPolicy
from pyramid.scripting import prepare
from pyramid.threadlocal import get_current_registry

from arche_celery import logger


# @worker_shutdown.connect
# def close_pyramid(signal, sender):
#     sender.app.pyramid_env['closer']()


@worker_init.connect
def worker_started(signal, sender):
    #FIXME: Paster config is better here. Would it be possible to include it that way?
    from arche_celery.authentication import CeleryWorkerAuthenticationPolicy
    policy = CeleryWorkerAuthenticationPolicy()
    registry = get_current_registry()
    registry.registerUtility(policy, IAuthenticationPolicy)


@task_prerun.connect
def prerun_start_request(task_id, task, signal, sender, args, kwargs):
    """ Populates kwargs
        A context_uid or context_path will be resolved as context instead.
    """
    logger.debug('signal prerun for %r' % task)
    print "Task prerun"
    print "args:", args
    print "kwargs:", kwargs
    #FIXME: MEMORY LEAK RISK! Make sure hook works
    task_env = prepare()
    request = task_env['request']
    print "new request: %r" % request
    if hasattr(request, 'set_celery_userid'):
        if 'authenticated_userid' in kwargs:
            request.set_celery_userid(kwargs['authenticated_userid'])
        else:
            logger.warning("authenticated_userid wasn't sent as a kwarg to task - so it will be Mone.")
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
    def closer_hook(success):
        task_env['closer']()
    transaction.get().addAfterCommitHook(closer_hook)


@task_success.connect
def commit_task_results(sender, **kw):
    logger.debug('signal success for %r' % sender)
    #FIXME: Care about commit veto?
    manager = transaction.manager
    def hook(success):
        if success:
            logger.debug('commit hook says success.')
        else:
            logger.debug("commit hook says fail, won't write command.")
    manager.get().addAfterCommitHook(hook)
    if manager.isDoomed():
        manager.abort()
        logger.debug("Transaction manager says transaction is doomed, aborting commit.")
    else:
        manager.commit()
        logger.debug("Transaction manager committing.")


@task_postrun.connect
def postrun_end_request(sender, task, **kw):
    logger.debug('signal postrun for %r' % task)


@task_failure.connect
@task_retry.connect
def abort_commit(**kw):
    logger.debug('signal retry or failure, transaction aborted.')
    transaction.manager.abort()


def includeme(config):
    logger.debug("Initialize signal read")
