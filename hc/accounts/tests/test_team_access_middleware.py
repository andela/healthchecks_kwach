from django.contrib.auth.models import User
from django.test import TestCase
from hc.accounts.models import Profile


class TeamAccessMiddlewareTestCase(TestCase):

    def test_it_handles_missing_profile(self):
        user = User(username="ned", email="ned@example.org")
        user.set_password("password")
        user.save()
        #returns all Profile Objects with id => 0
        self.new_number = Profile.objects.filter(user_id__gte = 0)

        self.client.login(username="ned@example.org", password="password")
        r = self.client.get("/about/")
        self.assertEqual(r.status_code, 200)

        ### Assert the new Profile objects count
        self.assertEqual(len(self.new_number), 1)
