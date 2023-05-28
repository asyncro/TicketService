from datetime import datetime
import itertools

reservation_id_generator = itertools.count(start=1, step=1)


class Event:
    def __init__(self, _id: int, name: str, description: str,
                 date_str: str, tickets_available: int):
        self.id = _id
        self.name = name
        self.description = description
        self.date_time = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
        self.tickets_available = tickets_available

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'date_time': self.date_time,
            'tickets_available': self.tickets_available
        }


class Reservation:
    def __init__(self, event_id: int, number_tickets: int, _id: int = None, date_created: datetime = None,
                 date_modified: datetime = None):
        self.id = next(reservation_id_generator) if _id is None else _id
        self.event_id = event_id
        self.number_tickets = number_tickets
        self.date_created = datetime.now() if date_created is None else date_created
        self.date_modified = date_modified
        self.cancelled = False

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'event_id': self.event_id,
            'number_tickets': self.number_tickets,
            'date_created': self.date_created,
            'date_modified': self.date_modified,
        }
