from datetime import datetime


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