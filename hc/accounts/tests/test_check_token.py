from django.contrib.auth.hashers import make_password
from hc.test import BaseTestCase


class CheckTokenTestCase(BaseTestCase):

    def setUp(self):
        super(CheckTokenTestCase, self).setUp()
        self.profile.token = make_password("secret-token")
        self.profile.save()

    def test_it_shows_form(self):
        response = self.client.get("/accounts/check_token/alice/secret-token/")
        self.assertContains(response, "You are about to log in")

    def test_it_redirects(self):
        response = self.client.post(
            "/accounts/check_token/alice/secret-token/")
        self.assertRedirects(response, "/checks/")

        # After login, token should be blank
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.token, "")

    def test_it_redirects_if_already_logged_in(self):
        self.client.login(username="alice@example.org", password="password")
        response = self.client.get("/accounts/check_token/alice/secret-token/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/checks/")

    def test_login_with_wrong_token(self):
        response = self.client.post("/accounts/check_token/bob/secret-token/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/accounts/login/")
