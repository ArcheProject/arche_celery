from pyramid.renderers import render
from pyramid_celery import celery_app as app

#from arche_celery import logger


@app.task(bind=True)
def send_newsletter_to_local_users(self, subject, template,
                                   sender = None, discriminator = None,
                                   root = None, request = None):
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


@app.task(bind=True)
def send_email(self, subject, recipients, html,
               sender = None, plaintext = None,
               send_immediately = True, request = None, **kw):
    request.send_email(
        subject, recipients, html,
        sender = sender,
        plaintext = plaintext,
        send_immediately = send_immediately
    )
