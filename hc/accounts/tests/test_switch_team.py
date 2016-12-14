from hc.test import BaseTestCase
from hc.api.models import Check


class SwitchTeamTestCase(BaseTestCase):

    def test_it_switches(self):
        alice_check = Check(user=self.alice, name="This belongs to Alice")
        alice_check.save()

        self.client.login(username="bob@example.org", password="password")

        url = "/accounts/switch_team/%s/" % self.alice.username
        response = self.client.get(url, follow=True)

        # Assert the contents of response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "front/my_checks.html")

    def test_it_checks_access_denied_if_not_member(self):
        self.client.login(username="charlie@example.org", password="password")

        url = "/accounts/switch_team/%s/" % self.alice.username
        response = self.client.get(url)
        # Assert the expected error code
        self.assertEqual(response.status_code, 403)

    def test_it_switches_to_own_team(self):
        self.client.login(username="alice@example.org", password="password")

        url = "/accounts/switch_team/%s/" % self.alice.username
        response = self.client.get(url, follow=True)
        # Assert the expected error code
        self.assertEqual(response.status_code, 200)
