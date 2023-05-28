import json
import unittest

import connexion

app = connexion.FlaskApp(__name__)
app.debug = True
app.testing = True
app.add_api("../api_schema.yml")


class ReservationTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.app.test_client()

    def test_create_reservation_valid(self):
        # Test with a valid event ID and available tickets
        self.create_reservation(event_id=1, number_tickets=2)

    def create_reservation(self, event_id: int, number_tickets: int):
        response = self.client.post(f"/events/{event_id}/reservations", json={"tickets": number_tickets})
        self.assert_200_status_code(response)

        reservation_id = self.assert_reservation(response, event_id, number_tickets)

        return reservation_id

    def assert_reservation(self, response, event_id, number_tickets):
        response_obj = json.loads(response.data.decode())
        self.assertEqual(event_id, response_obj['event_id'])
        reservation_id = response_obj['id']
        self.assertIsNotNone(reservation_id)
        self.assertEqual(number_tickets, response_obj['number_tickets'])
        return reservation_id

    def test_create_reservation_invalid_event_id(self):
        # Test with an invalid event ID
        response = self.client.post("/events/10/reservations", json={"tickets": 2})
        self.assert_400_status_code(response)
        self.assertIn("is not a valid event ID", response.data.decode())

    def test_create_reservation_insufficient_tickets(self):
        # Test with insufficient tickets available
        response = self.client.post("/events/1/reservations", json={"tickets": 20})
        self.assert_400_status_code(response)
        self.assertIn("does not have", response.data.decode())

    def test_exhausting_supply(self):
        # Test with insufficient tickets available
        for i in range(1, 6):
            response = self.client.post("/events/2/reservations", json={"tickets": 1})
            self.assert_200_status_code(response)

        response = self.client.post("/events/2/reservations", json={"tickets": 1})
        self.assert_400_status_code(response)
        self.assertIn("does not have 1 ticket", response.data.decode())

    def test_create_reservation_missing_tickets(self):
        # Test with missing tickets field in the request body
        response = self.client.post("/events/1/reservations", json={})
        self.assert_400_status_code(response)
        self.assertIn("number of tickets to reserve not specified", response.data.decode())

    def test_invalid_event_id(self):
        event_response = self.client.get(f"/events/999")
        self.assert_404_status_code(event_response)

    def test_modify_reservation_bad_reservation_id(self):
        # Create reservation for 50 tickets for
        reservation_id = self.create_reservation(event_id=4, number_tickets=1)
        response = self.client.patch(f"/events/4/reservations/{reservation_id*999}", json={"tickets": 1})
        self.assert_404_status_code(response)

    def test_modify_reservation(self):
        # Create reservation for 50 tickets for
        reservation_id = self.create_reservation(event_id=4, number_tickets=50)
        self.assert_number_tickets_remaining(event_id=4, number_tickets=150)

        response = self.client.patch(f"/events/4/reservations/{reservation_id}", json={"tickets": 1})
        self.assert_200_status_code(response)
        self.assert_reservation(response, event_id=4, number_tickets=51)
        self.assert_number_tickets_remaining(event_id=4, number_tickets=149)

        response = self.client.patch(f"/events/4/reservations/{reservation_id}", json={"tickets": 149})
        self.assert_200_status_code(response)
        self.assert_reservation(response, event_id=4, number_tickets=200)
        self.assert_number_tickets_remaining(event_id=4, number_tickets=0)

        response = self.client.patch(f"/events/4/reservations/{reservation_id}", json={"tickets": 1})
        self.assert_400_status_code(response)
        self.assertIn("does not have", response.data.decode())
        self.assert_number_tickets_remaining(event_id=4, number_tickets=0)

        response = self.client.patch(f"/events/4/reservations/{reservation_id}", json={"tickets": -149})
        self.assert_200_status_code(response)
        self.assert_reservation(response, event_id=4, number_tickets=51)
        self.assert_number_tickets_remaining(event_id=4, number_tickets=149)

        response = self.client.patch(f"/events/4/reservations/{reservation_id}", json={"tickets": -2})
        self.assert_200_status_code(response)
        self.assert_reservation(response, event_id=4, number_tickets=49)
        self.assert_number_tickets_remaining(event_id=4, number_tickets=151)

        response = self.client.patch(f"/events/4/reservations/{reservation_id}", json={"tickets": -48})
        self.assert_200_status_code(response)
        self.assert_reservation(response, event_id=4, number_tickets=1)
        self.assert_number_tickets_remaining(event_id=4, number_tickets=199)

        response = self.client.patch(f"/events/4/reservations/{reservation_id}", json={"tickets": -1})
        self.assert_400_status_code(response)
        self.assertIn("Cannot return", response.data.decode())

        self.assert_number_tickets_remaining(event_id=4, number_tickets=199)

    def assert_number_tickets_remaining(self, event_id, number_tickets):
        event_response = self.client.get(f"/events/{event_id}")
        self.assert_200_status_code(event_response)
        event_response_obj = json.loads(event_response.data.decode())
        self.assertEquals(number_tickets, event_response_obj['tickets_available'])

    def assert_200_status_code(self, response):
        self.assertEqual(200, response.status_code)

    def assert_404_status_code(self, response):
        self.assertEqual(404, response.status_code)

    def assert_400_status_code(self, response):
        self.assertEqual(400, response.status_code)


if __name__ == "__main__":
    unittest.main()
