from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail
from django.contrib.sites.models import Site
from django.template import Context
from django.template.loader import get_template
from django.contrib.auth.decorators import permission_required
from .models import Concern
from .forms import ReportConcernForm, ConcernForm


CONCERN_EMAIL_SUBJECT = getattr(settings, 'CONCERN_EMAIL_SUBJECT', u'Concern Reported for {site}')
CONCERN_RESOLVERS = getattr(settings, 'CONCERN_RESOLVERS', ())


def send_concern_email(request, concern, recipient_list=None):
    if not recipient_list:
        recipient_list = [r[1] for r in CONCERN_RESOLVERS]
    if not recipient_list:
        return

    site = Site.objects.get_current()

    t = get_template('concerns/concern_email.txt')
    c = Context({
        'protocol': 'https' if request.is_secure() else 'http',
        'site': site,
        'concern': concern,
    })

    subject = CONCERN_EMAIL_SUBJECT.format(site=site)
    body = t.render(c)
    from_email = settings.DEFAULT_FROM_EMAIL

    # No need to be a nuisance, fail silently
    send_mail(subject, body, from_email, recipient_list, fail_silently=True)

@csrf_exempt
def report_concern(request):
    "View that provides a form for reporting a concern."
    if request.method == 'POST':
        form = ReportConcernForm(request, request.POST)

        if form.is_valid():
            concern = form.save()
            send_concern_email(request, concern)

            if request.is_ajax():
                return HttpResponse()
            return HttpResponseRedirect(reverse('report-concern'))
    else:
        form = ReportConcernForm(request)

    return render(request, 'concerns/report_concern.html', {
        'form': form,
    })

@permission_required('concerns.change_concern')
def concern_list(request):
    "View that provides a queryset of concerns."
    concerns = Concern.objects.all()
    return render(request, 'concerns/concern_list.html', {
        'concerns': concerns,
    })

@permission_required('concerns.change_concern')
def concern_detail(request, pk):
    "View that provides a concern instance and form for resolving the concern."
    concern = get_object_or_404(Concern, pk=pk)

    if request.method == 'POST':
        form = ConcernForm(request, request.POST, instance=concern)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('concern-detail', args=[concern.pk]))
    else:
        form = ConcernForm(request, instance=concern)

    return render(request, 'concerns/concern_detail.html', {
        'form': form,
        'concern': concern,
    })
