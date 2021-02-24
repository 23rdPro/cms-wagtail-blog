import secrets
from django.conf import settings
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from .models import Subscriber
from .forms import SubscriberForm


# Helper func
def random_digits():
    return secrets.token_urlsafe(29)


@csrf_exempt
def subscribe(request):
    if request.method == 'POST':
        sub = Subscriber(email=request.POST['email'], conf_num=random_digits())
        # sub = Subscriber(email=request.POST.get('email'), conf_num=random_digits())
        sub.save()
        message = Mail(
            from_email=settings.FROM_EMAIL,
            to_emails=sub.email,
            subject='Newsletter Confirmation.',
            html_content="""Thank you for signing up for our newsletter!
            Please complete the process by
            <a href='{}/confirm-subscription/?email={}&conf_num={}'> clicking here to
            confirm your registration</a>""".format(
                request.build_absolute_uri('http://localhost:8000'),
                sub.email,
                sub.conf_num
            )
        )  # TODO: change from localhost to domain

        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        return render(request, 'blog/subscribe.html',
                      {
                          'email': sub.email,
                          'action': 'added, we sent you a message already,<br> please confirm your email.',
                          'conf_num': sub.conf_num,
                          'form': SubscriberForm()
                      },)
    else:
        return render(request, 'blog/subscribe.html',
                      {
                          'form': SubscriberForm()
                      })


def confirm(request):
    sub = Subscriber.objects.get(email=request.GET['email'])
    if sub.conf_num == request.GET['conf_num']:
        sub.confirmed = True
        sub.save()
        return render(request, 'blog/confirm.html',
                      {
                          'email': sub.email,
                          'action': 'confirmed, thank you!',
                      })
    else:
        return render(request, 'blog/confirm.html',
                      {
                          'email': sub.email,
                          'action': 'denied request, try again?',

                      })


def unsubscribe(request):
    sub = Subscriber.objects.get(email=request.GET['email'])
    if sub.conf_num == request.GET['conf_num']:
        sub.delete()
        return render(request, 'blog/unsubscribe.html',
                      {
                          'email': sub.email,
                          'action': 'deleted from our record',
                      })
    else:
        return render(request, 'blog/unsubscribe.html',
                      {
                          'email': sub.email,
                          'action': 'denied request, try again?'
                      })
