from pyramid.i18n import TranslationStringFactory
from logging import getLogger

_ = TranslationStringFactory('arche_celery')

logger = getLogger(__name__)


def includeme(config):
    config.include('pyramid_celery')
    #FIXME:
    config.configure_celery('etc/development.ini')
    config.include('.signals')
    config.include('.utils')

    #TEMP:
    # from pyramid_celery import celery_app
    # print "CELERY_ACCEPT_CONTENT", celery_app.conf['CELERY_ACCEPT_CONTENT']
    # print "CELERY_TASK_SERIALIZER", celery_app.conf['CELERY_TASK_SERIALIZER']
    # print "CELERY_RESULT_SERIALIZER", celery_app.conf['CELERY_RESULT_SERIALIZER']
    #CELERY_ACCEPT_CONTENT = ['json']
    #CELERY_TASK_SERIALIZER = 'json'
    #CELERY_RESULT_SERIALIZER = 'json'

    #from kombu import serialization
    #print "serializers, decoders: ", serialization.registry._decoders
    #serialization.registry._decoders.pop('application/x-python-serialize')

    #celery_app.conf.update(CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml'])
    #CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']
    #config.include('.views')
