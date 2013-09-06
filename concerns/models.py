from datetime import datetime
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

CONCERN_STATUSES = getattr(settings, 'CONCERN_STATUSES', None)

if not CONCERN_STATUSES:
    CONCERN_STATUSES = ('New', 'In Review', 'Duplicate', 'Closed')

DEFAULT_STATUS = CONCERN_STATUSES[0]


class Concern(models.Model):
    STATUS_CHOICES = [(unicode(s), unicode(s)) for s in CONCERN_STATUSES]

    # Report information
    reporter = models.ForeignKey(User, null=True, blank=True,
        related_name='reported_concerns')
    ip = models.IPAddressField(null=True, blank=True)
    headers = models.TextField(null=True, blank=True)
    document = models.TextField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)

    # Status of concern
    status = models.CharField(max_length=100, choices=STATUS_CHOICES,
        default=DEFAULT_STATUS)

    # Resolution information
    resolved = models.BooleanField(default=False)
    resolution = models.TextField(null=True, blank=True)
    resolver = models.ForeignKey(User, null=True, blank=True,
        related_name='resolved_concerns')

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta(object):
        ordering = ('-resolved', 'created')

    def __unicode__(self):
        return u'Concern #{0}'.format(self.id)

    @models.permalink
    def get_absolute_url(self):
        return 'concern-detail', [self.id], {}
