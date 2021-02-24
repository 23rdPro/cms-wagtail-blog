from .forms import SubscriberForm


def subscribe_form(request):
    if request.method == 'POST':
        form = SubscriberForm(request.POST)
    else:
        form = SubscriberForm()
    return {'form': form, }
