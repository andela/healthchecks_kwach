import json
from datetime import timedelta as td
from django.utils.timezone import now

from hc.api.models import Check
from hc.test import BaseTestCase


class ListChecksTestCase(BaseTestCase):

    def setUp(self):
        super(ListChecksTestCase, self).setUp()

        self.now = now().replace(microsecond=0)

        self.a1 = Check(user=self.alice, name="Alice 1")
        self.a1.timeout = td(seconds=3600)
        self.a1.grace = td(seconds=900)
        self.a1.last_ping = self.now
        self.a1.n_pings = 1
        self.a1.status = "new"
        self.a1.save()

        self.a2 = Check(user=self.alice, name="Alice 2")
        self.a2.timeout = td(seconds=86400)
        self.a2.grace = td(seconds=3600)
        self.a2.last_ping = self.now
        self.a2.status = "up"
        self.a2.save()

    def get(self):
        return self.client.get("/api/v1/checks/", HTTP_X_API_KEY="abc")

    def test_it_works(self):
        r = self.get()
        self.assertEqual(r.status_code, 200)

        doc = r.json()
        self.assertTrue("checks" in doc)

        checks = {check["name"]: check for check in doc["checks"]}
        self.assertEqual(len(checks),2)
        self.assertIn('Alice 1',checks.keys() )
        self.assertEqual(checks[self.a1.name]['timeout'],3600)
        self.assertEqual(checks[self.a1.name]['grace'],900)
        self.assertNotEqual(checks[self.a1.name]['pause_url'],0)
        self.assertNotEqual(len(checks[self.a1.name]['ping_url']),0)
        self.assertEqual(checks[self.a1.name]['status'],"new")
        self.assertEqual(checks[self.a1.name]['last_ping'],self.now.isoformat())
        self.assertEqual(checks[self.a1.name]['n_pings'],1)

        self.assertIn('Alice 2',checks.keys() )
        self.assertEqual(checks[self.a2.name]['timeout'],86400)
        self.assertEqual(checks[self.a2.name]['grace'],3600)
        self.assertNotEqual(checks[self.a2.name]['pause_url'],0)
        self.assertNotEqual(len(checks[self.a2.name]['ping_url']),0)
        self.assertEqual(checks[self.a2.name]['status'],"up")
        self.assertEqual(checks[self.a2.name]['last_ping'],self.now.isoformat())
        self.assertEqual(checks[self.a2.name]['n_pings'],0)

    def test_it_shows_only_users_checks(self):
        bobs_check = Check(user=self.bob, name="Bob 1")
        bobs_check.save()

        r = self.get()
        data = r.json()
        self.assertEqual(len(data["checks"]), 2)
        for check in data["checks"]:
            self.assertNotEqual(check["name"], "Bob 1")
            self.assertEqual(r.status_code,200)

    def test_it_accepts_api_key_in_request(self):
        r = self.client.get("/api/v1/checks/", HTTP_X_API_KEY="bbb")
        self.assertEqual(r.status_code, 400)

        r = self.client.get("/api/v1/checks/", HTTP_X_API_KEY="abc")
        self.assertEqual(r.status_code, 200)

        r = self.client.get("/api/v1/checks/")
        self.assertEqual(r.status_code, 400)
