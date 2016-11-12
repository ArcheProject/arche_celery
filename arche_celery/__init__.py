from sys import argv
from logging import getLogger

from pyramid.i18n import TranslationStringFactory


APP_NAME = 'arche_celery'
_ = TranslationStringFactory(APP_NAME)
logger = getLogger(__name__)


DEFAULT_CONFIGURATION = {
    '%s.worker_auth' % APP_NAME: 'arche_celery.authentication.worker_auth',
}


def includeme(config):
    settings = config.registry.settings
    for (k, v) in DEFAULT_CONFIGURATION.items():
        if k not in settings:
            settings[k]=v
    config.include('pyramid_celery')
    #FIXME: option to add configurator object or specify ini file?
    #FIXME: This is not the best way to figure out the ini file.
    ini_file = None
    if '%s.ini' % APP_NAME in settings:
        ini_file=settings['%s.ini' % APP_NAME]
    else:
        for arg in argv:
            if arg.endswith('.ini'):
                ini_file = arg
                break
    if ini_file:
        config.configure_celery(arg)
    else:
        raise Exception("Can't figure out celery configuration.")
    config.include('.signals')
    config.include('.utils')
    config.include('.views')
