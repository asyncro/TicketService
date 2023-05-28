import json
import unittest


class BaseTestCase(unittest.TestCase):
    def get_all_events(self):
        event_response = self.client.get(f"/events")
        self.assert_200_status_code(event_response)
        event_response_obj = json.loads(event_response.data.decode())
        return event_response_obj

    def create_reservation(self, event_id: int, number_tickets: int):
        response = self.client.post(f"/events/{event_id}/reservations", json={"tickets": number_tickets})
        self.assert_200_status_code(response, f"reserving {number_tickets} tickets for event:{event_id}")

        reservation_id = self.assert_reservation(response, event_id, number_tickets)

        return reservation_id

    def assert_reservation(self, response, event_id, number_tickets):
        response_obj = json.loads(response.data.decode())
        self.assertEqual(event_id, response_obj['event_id'])
        reservation_id = response_obj['id']
        self.assertIsNotNone(reservation_id)
        self.assertEqual(number_tickets, response_obj['number_tickets'])
        return reservation_id

    def assert_or_get_number_tickets_remaining(self, event_id, number_tickets=None):
        event_response = self.client.get(f"/events/{event_id}")
        self.assert_200_status_code(event_response)
        event_response_obj = json.loads(event_response.data.decode())
        if number_tickets is not None:
            self.assertEqual(number_tickets, event_response_obj['tickets_available'],
                             f"checking tickets_available for event {event_id}")
        else:
            return event_response_obj['tickets_available']

    def assert_200_status_code(self, response, message=None):
        self.assertEqual(200, response.status_code, f"{message}, response={response}")

    def assert_404_status_code(self, response, message=None):
        self.assertEqual(404, response.status_code, f"{message}, response={response}")

    def assert_400_status_code(self, response, message=None):
        self.assertEqual(400, response.status_code, f"{message}, response={response}")