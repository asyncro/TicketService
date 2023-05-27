import unittest

import connexion
from flask import Flask
from flask.testing import FlaskClient

app = connexion.FlaskApp(__name__)
app.debug = True
app.testing = True
app.add_api("../api_schema.yml")


class ReservationTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.app.test_client()

    def test_create_reservation_valid(self):
        # Test with a valid event ID and available tickets
        response = self.client.post("/events/1/reservations", json={"tickets": 2})
        self.assertEqual(200, response.status_code)
        self.assertEqual("\"Success\"", response.data.decode().strip())

    def test_create_reservation_invalid_event_id(self):
        # Test with an invalid event ID
        response = self.client.post("/events/10/reservations", json={"tickets": 2})
        self.assertEqual(400, response.status_code)
        self.assertIn("is not a valid event ID", response.data.decode())

    def test_create_reservation_insufficient_tickets(self):
        # Test with insufficient tickets available
        response = self.client.post("/events/1/reservations", json={"tickets": 20})
        self.assertEqual(400, response.status_code)
        self.assertIn("does not have", response.data.decode())

    def test_exhausting_supply(self):
        # Test with insufficient tickets available
        for i in range(1, 6):
            response = self.client.post("/events/2/reservations", json={"tickets": 1})
            self.assertEqual(200, response.status_code)

        response = self.client.post("/events/2/reservations", json={"tickets": 1})
        self.assertEqual(400, response.status_code)
        self.assertIn("does not have 1 ticket", response.data.decode())

    def test_create_reservation_missing_tickets(self):
        # Test with missing tickets field in the request body
        response = self.client.post("/events/1/reservations", json={})
        self.assertEqual(400, response.status_code)
        self.assertIn("number of tickets to reserve not specified", response.data.decode())


if __name__ == "__main__":
    unittest.main()
