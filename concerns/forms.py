import re
from django import forms
from concerns.models import Concern

IPv4_RE = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')

def get_ip_address(request):
    ip_address = request.META.get('HTTP_X_FORWARDED_FOR',
        request.META.get('REMOTE_ADDR', None))

    if ip_address:
        ip_match = IPv4_RE.match(ip_address)
        if ip_match is not None:
            ip_address = ip_match.group()
        else:
            ip_address = None
    return ip_address

def get_headers(request):
    headers = {}

    for key, value in request.META.iteritems():
        if key.startswith('HTTP_') and key != 'HTTP_COOKIE':
            header = key.replace('HTTP_', '').replace('_', '-').title()
            headers[header] = value
        elif key.startswith('CONTENT_'):
            header = key.replace('_', '-').title()
            headers[header] = value

    return '\n'.join(['{0}: {1}'.format(key, value)
        for key, value in sorted(headers.items())])


class ReportConcernForm(forms.ModelForm):
    """Form for reporting a concern. Only the `comment` and `document` are
    exposed to be defined. The other fields are set implicited based on the
    request and requesting user.
    """
    comment = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(ReportConcernForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        concern = super(ReportConcernForm, self).save(commit=False)
        if self.request.user.is_authenticated():
            concern.reporter = self.request.user
        concern.ip = get_ip_address(self.request)
        concern.headers = get_headers(self.request)

        if commit:
            concern.save()
        return concern

    class Meta(object):
        model = Concern
        fields = ('comment', 'document')


class ConcernForm(forms.ModelForm):
    """Form for resolving a concern once reported. The `resolver` is not
    exposed in the form, but will be set as the requesting user.
    """
    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(ConcernForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        concern = super(ConcernForm, self).save(commit=False)
        concern.resolver = self.request.user
        if commit:
            concern.save()
        return concern

    class Meta(object):
        model = Concern
        exclude = ('resolver',)
