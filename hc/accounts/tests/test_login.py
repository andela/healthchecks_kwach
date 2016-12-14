from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from hc.api.models import Check


class LoginTestCase(TestCase):

    def test_it_sends_link(self):
        check = Check()
        check.save()

        session = self.client.session
        session["welcome_code"] = str(check.code)
        session.save()

        form = {"email": "alice@example.org"}

        # assert the user doesn't exist before post operation
        self.assertEqual(len(User.objects.filter(email=form["email"])), 0)
        self.old_user_count = User.objects.count()

        response = self.client.post("/accounts/login/", form)
        self.assertEqual(response.status_code, 302)

        # Assert that a user was created
        self.new_user_count = User.objects.count()
        self.test_user_list = User.objects.filter(email=form["email"])
        self.assertEqual(self.test_user_list[0].email, form["email"])
        self.assertEqual(self.new_user_count - self.old_user_count, 1)

        # And email sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Log in to healthchecks.io')
        # Assert contents of the email body
        self.assertIn("To log into healthchecks.io, please open the link below",
                      mail.outbox[0].body)

        # Assert that check is associated with the new user
        self.test_check = Check.objects.get(user=self.test_user_list[0].id)
        self.assertEqual(self.test_user_list[0].id, self.test_check.user_id)

    def test_it_pops_bad_link_from_session(self):
        self.client.session["bad_link"] = True
        self.client.get("/accounts/login/")
        assert "bad_link" not in self.client.session
