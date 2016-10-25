
def add_task(request, task, context, *args, **kw):
    task_kwargs = {'context_uid': context.uid,
                   'authenticated_userid': request.authenticated_userid}
    task_kwargs.update(**kw)
    return task.delay(*args, **task_kwargs)

def set_celery_userid(request, userid):
    request._celery_userid = userid

def includeme(config):
    config.add_request_method(add_task)
    config.add_request_method(set_celery_userid)
