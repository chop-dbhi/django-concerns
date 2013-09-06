from django.test import TestCase
from django.core.urlresolvers import reverse
from django.core import mail
from django.contrib.auth.models import User, Permission
from concerns.models import Concern


class BaseTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', password='root')


class ReportTestCase(BaseTestCase):
    def test_no_user(self):
        "Tests no user using AJAX."

        comment = 'I have a concern'
        document = '<html>...</html>'

        resp = self.client.post(reverse('report-concern'), {
            'comment': comment,
            'document': document,
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertContains(resp, '', status_code=200)

        concern = Concern.objects.get(pk=1)

        self.assertEqual(concern.status, 'New')
        self.assertFalse(concern.resolved)
        self.assertEqual(concern.reporter, None)
        self.assertEqual(concern.resolver, None)
        self.assertEqual(concern.ip, '127.0.0.1')
        self.assertEqual(concern.document, document)
        self.assertEqual(concern.comment, comment)
        self.assertTrue('Content-Length' in concern.headers)

        # Ensure the email got sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Concern Reported for example.com')
        self.assertEqual(mail.outbox[0].to, ['jdoe@example.com'])

    def test_user(self):
        self.assertTrue(self.client.login(username='user', password='root'))
        self.client.post(reverse('report-concern'))
        concern = Concern.objects.get(pk=1)
        self.assertEqual(concern.reporter, self.user)


class AccessTestCase(BaseTestCase):
    def test_forbidden(self):
        # Anonymous access
        resp = self.client.get(reverse('concern-list'))
        self.assertEqual(resp.status_code, 302)

        # Authenticated user (no perm)
        self.assertTrue(self.client.login(username='user', password='root'))
        resp = self.client.get(reverse('concern-list'))
        self.assertEqual(resp.status_code, 302)

    def test_allowed(self):
        perm = Permission.objects.get(codename='change_concern')
        self.user.user_permissions.add(perm)

        self.assertTrue(self.client.login(username='user', password='root'))
        resp = self.client.get(reverse('concern-list'))
        self.assertEqual(resp.status_code, 200)


class ResolveTestCase(BaseTestCase):
    def test_resolve(self):
        perm = Permission.objects.get(codename='change_concern')
        self.user.user_permissions.add(perm)
        self.assertTrue(self.client.login(username='user', password='root'))

        # Concern reported
        self.client.post(reverse('report-concern'))

        status = 'Closed'
        resolution = 'Data has been redacted'

        resp = self.client.post(reverse('concern-detail', args=[1]), {
            'status': status,
            'resolution': resolution,
            'resolved': True,
        })

        concern = Concern.objects.get(pk=1)

        self.assertEqual(concern.status, status)
        self.assertTrue(concern.resolved)
        self.assertEqual(concern.resolution, resolution)
        self.assertEqual(concern.resolver, self.user)
