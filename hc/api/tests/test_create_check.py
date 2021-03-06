import json

from hc.api.models import Channel, Check
from hc.test import BaseTestCase


class CreateCheckTestCase(BaseTestCase):
    URL = "/api/v1/checks/"

    def setUp(self):
        super(CreateCheckTestCase, self).setUp()

    def post(self, data, expected_error=None):

        r = self.client.post(self.URL, json.dumps(data),
                             content_type="application/json")

        if expected_error:
            self.assertEqual(r.status_code, 400)

            self.assertEqual(r.json()['error'], expected_error)

        return r

    def test_it_works(self):
        r = self.post({
            "api_key": "abc",
            "name": "Foo",
            "tags": "bar,baz",
            "timeout": 3600,
            "grace": 60
        })

        self.assertEqual(r.status_code, 201)

        doc = r.json()

        assert "ping_url" in doc
        self.assertEqual(doc["name"], "Foo")
        self.assertEqual(doc["tags"], "bar,baz")
        self.assertEqual(doc["last_ping"], None)
        self.assertEqual(doc["n_pings"], 0)
        self.assertEqual(Check.objects.count(), 1)

        check = Check.objects.get()
        self.assertEqual(check.name, "Foo")
        self.assertEqual(check.tags, "bar,baz")
        self.assertEqual(check.timeout.total_seconds(), 3600)
        self.assertEqual(check.grace.total_seconds(), 60)

    def test_it_accepts_api_key_in_header(self):
        payload = json.dumps({"name": "Foo", "api_key": "abc"})
        r = self.client.post(
            self.URL, payload, content_type="application/json")
        self.assertEqual(r.status_code, 201)

    def test_it_handles_missing_request_body(self):
        r = self.client.post(self.URL, content_type="application/json")
        j = r.json()
        self.assertEqual(r.status_code, 400)
        self.assertEqual(j["error"], "wrong api_key")

    def test_it_handles_invalid_json(self):
        r = self.client.post(self.URL, "invalid_json",
                             content_type="application/json")
        j = r.json()
        self.assertEqual(r.status_code, 400)
        self.assertEqual(j["error"], "could not parse request body")

    def test_it_rejects_wrong_api_key(self):
        self.post({"api_key": "wrong"},
                  expected_error="wrong api_key")

    def test_it_rejects_non_number_timeout(self):
        self.post({"api_key": "abc", "timeout": "oops"},
                  expected_error="timeout is not a number")

    def test_it_rejects_non_string_name(self):
        self.post({"api_key": "abc", "name": False},
                  expected_error="name is not a string")

    def test_timeout_is_too_small(self):
        r = self.post({"api_key": "abc", "timeout": 1},
                      expected_error="timeout is too small")

        j = r.json()
        self.assertEqual(j["error"], "timeout is too small")

    def test_timeout_is_too_large(self):
        r = self.post({"api_key": "abc", "timeout": 3456567},
                      expected_error="timeout is too large")

        j = r.json()
        self.assertEqual(j["error"], "timeout is too large")

    def test_for_the_assignment_of_channels(self):
        
        channel = Channel(user=self.alice, kind="pushbullet")
        channel.save()#create channel object 1

        channel2 = Channel(user=self.alice, kind="pushbullet")
        channel2.save()#create second channel object

        data = {"api_key": "abc", "name": "Kip", "tags": "sims,cps", "timeout": 3600,
                "grace": 60, "channels": "*"}

        r = self.client.post(self.URL, json.dumps(
            data), content_type="application/json")

        channels = Channel.objects.all()
        checks=Check.objects.all()
        for check in checks:
            self.assertEqual(len(check.channel_set.all()),2)#assert that has 2 channels
