from hc.api.models import Check
from hc.test import BaseTestCase



class AddCheckTestCase(BaseTestCase):

    def test_it_works(self):
        url = "/checks/add/"
        self.client.login(username="alice@example.org", password="password")
        r = self.client.post(url)
        self.assertRedirects(r, "/checks/")
        assert Check.objects.count() == 1

    ### Test that team access works
    def test_check_team_works(self):
        url = "/checks/add/"
        self.client.login(username="bob@example.org", password="password")
        response = self.client.post(url)

        import pdb;
        added_check = Check.objects.all().order_by('id').last().user
        self.assertEqual(added_check, self.alice)
