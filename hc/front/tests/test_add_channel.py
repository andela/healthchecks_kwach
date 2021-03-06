from django.test.utils import override_settings

from hc.api.models import Channel
from hc.test import BaseTestCase


@override_settings(PUSHOVER_API_TOKEN="token", PUSHOVER_SUBSCRIPTION_URL="url")
class AddChannelTestCase(BaseTestCase):

    def test_it_adds_email(self):
        url = "/integrations/add/"
        form = {"kind": "email", "value": "alice@example.org"}

        self.client.login(username="alice@example.org", password="password")
        r = self.client.post(url, form)

        self.assertRedirects(r, "/integrations/")
        assert Channel.objects.count() == 1

    def test_it_trims_whitespace(self):
        """ Leading and trailing whitespace should get trimmed. """

        url = "/integrations/add/"
        form = {"kind": "email", "value": "   alice@example.org   "}

        self.client.login(username="alice@example.org", password="password")
        self.client.post(url, form)

        q = Channel.objects.filter(value="alice@example.org")
        self.assertEqual(q.count(), 1)

    def test_instructions_work(self):
        self.client.login(username="alice@example.org", password="password")
        kinds = ("email", "webhook", "pd", "pushover", "hipchat", "victorops")
        for frag in kinds:
            url = "/integrations/add_%s/" % frag
            r = self.client.get(url)
            self.assertContains(r, "Integration Settings", status_code=200)

    ### Test that the team access works
    def test_team_access(self):
        """ login as a different user"""
        self.client.login(username='bob@example.org', password="password")

        #a url to make a request to alice's stuff using Bobs's credential who is a team member
        url = "/accounts/switch_team/alice"
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 403)
        self.assertEqual(response.status_code, 301)

    ### Test that bad kinds don't work
    def test_bad_kinds(self):
        self.client.login(username='bob@example.org', password="password")
        #provide non existent kinds
        kind = "kdenno"
        url = "/integrations/add_%s/" % kind
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
