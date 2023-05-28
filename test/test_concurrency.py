import concurrent.futures
import unittest
from math import floor
from random import randint

import connexion

from test_base import BaseTestCase


class ConcurrencyTestCase(BaseTestCase):
    def setUp(self):
        app = connexion.FlaskApp(__name__)
        app.debug = True
        app.testing = True
        app.add_api("../api_schema.yml")
        self.client = app.app.test_client()

    def get_random_event(self):
        event_response_obj = super().get_all_events()
        num_events = len(event_response_obj)
        random_event_num = randint(1, num_events-1)

        return event_response_obj[random_event_num]

    @staticmethod
    def get_random_number_tickets(maximum):
        if maximum == 1:
            return 1

        # minimize chance of collision in case two threads simultaenously choose the same event
        return randint(1, floor(maximum/2))

    # A test to simulate a burst of traffic to the API.
    # num_requests threads are spawned simultaneously and each thread:
    #   1. creates a new reservation for a random event for a random number of tickets
    #   and either
    #       2a. sends a modify_reservation request to add a ticket to the reservation
    #       2b or cancels the reservation
    def test_concurrent_requests(self):
        num_requests = 10

        def make_requests():
            event = self.get_random_event()
            event_id = event['id']
            tickets_available = event['tickets_available']
            if tickets_available < 1:
                return

            number_tickets = self.get_random_number_tickets(tickets_available)

            reservation_id = self.create_reservation(event_id, number_tickets)
            self.assertGreater(reservation_id, 0)

            new_num_tickets_available = self.assert_or_get_number_tickets_remaining(event_id)
            if randint(1,10) <= 5 and new_num_tickets_available > 1:
                # up to 50% of threads will attempt to modify their reservation
                response = self.client.patch(f"/events/{event_id}/reservations/{reservation_id}", json={"tickets": 1})
                self.assert_200_status_code(response, f"testing patch for event_id:{event_id}/reservation_id:{reservation_id}")
            else:
                # the remainder will cancel their reservation
                response = self.client.delete(f"/events/{event_id}/reservations/{reservation_id}")
                self.assert_200_status_code(response, f"testing delete for event_id:{event_id}/reservation_id:{reservation_id}")

        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Submit the request function to the executor for concurrent execution
            futures = [executor.submit(make_requests) for _ in range(num_requests)]

            # Wait for all the requests to complete
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    self.fail(f"Request raised an exception: {e}")


if __name__ == "__main__":
    unittest.main()
