""" Testing helpers and fixtures - not ment to be included.
"""
import os

from pyramid_celery import celery_app as app


here = os.path.abspath(os.path.dirname(__file__))
CONFIG_INI_TESTS = os.path.join(here, 'tests', 'config.ini')


@app.task(bind=True)
def dummy_task(*task_args, **task_kwargs):
    return task_args, task_kwargs


@app.task(bind=True)
def dummy_with_children(*task_args, **task_kwargs):
    return dummy_task.s().delay(), dummy_task.s().delay()
