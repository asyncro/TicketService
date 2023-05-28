import unittest

import connexion

from test_base import BaseTestCase


class ReservationTestCase(BaseTestCase):
    def setUp(self):
        app = connexion.FlaskApp(__name__)
        app.debug = True
        app.testing = True
        app.add_api("../api_schema.yml")
        self.client = app.app.test_client()

    def test_get_all_events(self):
        event_response_obj = super().get_all_events()
        self.assertGreater(len(event_response_obj), 0)

    def test_create_reservation_valid(self):
        # Test with a valid event ID and available tickets
        super().create_reservation(event_id=1, number_tickets=2)

    def test_create_reservation_invalid_event_id(self):
        # Test with an invalid event ID
        response = self.client.post("/events/10/reservations", json={"tickets": 2})
        self.assert_400_status_code(response)
        self.assertIn("is not a valid event ID", response.data.decode())

    def test_create_reservation_insufficient_tickets(self):
        # Test with insufficient tickets available
        response = self.client.post("/events/1/reservations", json={"tickets": 20})
        super().assert_400_status_code(response)
        self.assertIn("does not have", response.data.decode())

    def test_exhausting_supply(self):
        # Test with insufficient tickets available
        number_tickets_remaining = super().assert_or_get_number_tickets_remaining(event_id=2)
        for i in range(0, number_tickets_remaining):
            response = self.client.post("/events/2/reservations", json={"tickets": 1})
            super().assert_200_status_code(response, f"reserving ticket #{i}")

        response = self.client.post("/events/2/reservations", json={"tickets": 1})
        super().assert_400_status_code(response)
        self.assertIn("does not have 1 ticket", response.data.decode())

    def test_create_reservation_missing_tickets(self):
        # Test with missing tickets field in the request body
        response = self.client.post("/events/1/reservations", json={})
        super().assert_400_status_code(response)
        self.assertIn("number of tickets to reserve not specified", response.data.decode())

    def test_invalid_event_id(self):
        event_response = self.client.get(f"/events/999")
        super().assert_404_status_code(event_response)

    def test_modify_delete_reservation_bad_reservation_id(self):
        reservation_id = self.create_reservation(event_id=4, number_tickets=1)
        response = self.client.patch(f"/events/4/reservations/{reservation_id*999}", json={"tickets": 1})
        super().assert_404_status_code(response)

        response = self.client.delete(f"/events/4/reservations/{reservation_id * 999}", json={"tickets": 1})
        super().assert_404_status_code(response)

    def test_modify_reservation(self):
        number_tickets_remaining_initial = super().assert_or_get_number_tickets_remaining(event_id=4)
        reservation_id = self.create_reservation(event_id=4, number_tickets=50)
        super().assert_or_get_number_tickets_remaining(event_id=4, number_tickets=number_tickets_remaining_initial-50)

        # original code had this sequence
        # ticket_num_deltas = [1, 149, 1, -149, -2, -48, -1]
        # but with the introduction of the concurrency test, needed to make the deltas dynamic
        ticket_num_deltas = [1, number_tickets_remaining_initial-51, 1, -number_tickets_remaining_initial-51, -2, -48, -1]
        current_ticket_count = 50
        current_remaining_tickets = number_tickets_remaining_initial-50
        for i, ticket_delta in enumerate(ticket_num_deltas):
            response = self.client.patch(f"/events/4/reservations/{reservation_id}", json={"tickets": ticket_delta})

            if 0 < ticket_delta and current_remaining_tickets < ticket_delta:
                super().assert_400_status_code(response, f"iteration:{i}, applying ticket delta {ticket_delta}")
                self.assertIn("does not have", response.data.decode(), "Insufficient tickets available for event")
            elif 0 > ticket_delta and -current_ticket_count >= ticket_delta:
                super().assert_400_status_code(response, f"iteration:{i}, applying ticket delta {ticket_delta}")
                self.assertIn("Cannot return", response.data.decode(), "Not enough tickets available to return")
            else:
                self.assertGreaterEqual(current_remaining_tickets, ticket_delta)
                current_ticket_count += ticket_delta
                current_remaining_tickets -= ticket_delta
                super().assert_200_status_code(response, f"iteration:{i}, applying ticket delta {ticket_delta}")
                super().assert_reservation(response, event_id=4, number_tickets=current_ticket_count)

            super().assert_or_get_number_tickets_remaining(event_id=4, number_tickets=current_remaining_tickets)

    def test_cancel_reservation(self):
        tickets_left = super().assert_or_get_number_tickets_remaining(event_id=6)
        reservation_id = super().create_reservation(event_id=6, number_tickets=1)
        super().assert_or_get_number_tickets_remaining(event_id=6, number_tickets=tickets_left-1)
        response = self.client.delete(f"/events/6/reservations/{reservation_id}")
        super().assert_200_status_code(response)
        super().assert_or_get_number_tickets_remaining(event_id=6, number_tickets=tickets_left)

        response = self.client.delete(f"/events/6/reservations/{reservation_id}")
        super().assert_400_status_code(response)
        self.assertIn("already been cancelled", response.data.decode())
        super().assert_or_get_number_tickets_remaining(event_id=6, number_tickets=tickets_left)


if __name__ == "__main__":
    unittest.main()
