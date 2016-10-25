from pyramid.renderers import render
from pyramid_celery import celery_app as app

from arche_celery import logger

@app.task
def send_newsletter_to_local_users(subject, template, sender = None, discriminator = None, root = None, request = None):
    users = set()
    for user in root['users'].values():
        if not user.email:
            continue
        if discriminator:
            if discriminator(user, None):
                users.add(user)
        else:
            users.add(user)
    for user in users:
        html = render(template, {'user': user}, request = request)
        request.add_task(send_email, user, subject, [user.email], html, sender = sender)

@app.task
def send_email(subject, recipients, html, sender = None, plaintext = None, send_immediately = True, request = None, **kw):
    #logger.debug("result of %s + %s: %s" % (x, y, x+y))
    request.send_email(subject, recipients, html, sender = sender, plaintext = plaintext, send_immediately = send_immediately)

    #def send_email(request, subject, recipients, html, sender = None, plaintext = None, send_immediately = False, **kw):


#    logger.debug("KW: %s" % kw)
#    request = get_current_request()
#    logger.debug("Task userid: %s" % request.authenticated_userid)
