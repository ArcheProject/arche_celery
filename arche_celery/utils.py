from celery.result import ResultSet


def add_task(request, task, context, *args, **kw):
    task_kwargs = {'context_uid': context.uid,
                   'authenticated_userid': request.authenticated_userid}
    task_kwargs.update(**kw)
    return task.delay(*args, **task_kwargs)


def set_celery_userid(request, userid):
    """
    :param request: Pyramids request object
    :param userid: userid or None

    Method is ment to set the userid on the task so we can track who initiated the task
    and to proper permission checks based on that users permission.
    prerun_start_request is responsible for using it.
    """
    request._celery_userid = userid


def includeme(config):
    config.add_request_method(add_task)
    config.add_request_method(set_celery_userid)


def build_status(result):
    """ Checks the result of the specified task and any children
        Result may look like:

        {
            'all_ready': True,
            'completed': 1,
            'state': 'SUCCESS',
            'ready': True,
            'total': 1,
            'children': {'completed': 0, 'total': 0}
        }

        Meaning of the keywords

        ready (bool)
            The tasks ready-state?

        all_ready(bool)
            Is the task an all of its children completed?

        state (str)
            Celerys state/status of the task.

        total
            Total count task + children, their children etc...

        completed
            Total count of completed

        children
            Count for referenced tasks.
    """
    response = {'ready': result.ready(), 'children': {'completed': 0, 'total': 0}}
    completed = 0
    total = 0
    children_ready = []
    if isinstance(result, ResultSet):
        completed += result.completed_count()
        total += len(result)
    else:
        #Assume Assync or Eager result
        response['state'] = result.state
        if result.ready():
            completed += 1
        total += 1
        #only investigare children on regular async results
        if result.children:
            for child in result.children:
                ch_response = build_status(child)
                response['children']['completed'] += ch_response['completed']
                response['children']['total'] += ch_response['total']
                children_ready.append(ch_response['ready'])
            total += response['children']['total']
            completed += response['children']['completed']
    response['completed'] = completed
    response['total'] = total
    if children_ready:
        response['all_ready'] = sum([result.ready()] + children_ready) == len(children_ready) + 1
    else:
        response['all_ready'] = result.ready()
    return response
