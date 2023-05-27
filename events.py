import datetime

from flask import jsonify, abort

from model.Event import Event, Reservation

EVENTS = {
    1: Event(
        _id=1,
        name='National Awareness Day',
        description="You won't have time for sleeping, soldier, not with all the bed making you'll be doing. "
                    "Guess again. No, I'm Santa Claus! Bender! Ship! Stop bickering or I'm going to come back "
                    "there and change your opinions manually!",
        date_str='2027-03-05T13:00:00Z',
        tickets_available=10
    ),
    2: Event(
        _id=2,
        name='Universal Entrepreneurship Expo',
        description="I suppose I could part with 'one' and still be feared... Enough about your promiscuous "
                    "mother, Hermes! We have bigger problems. Ummm...to eBay?",
        date_str='2013-02-21T15:00:00Z',
        tickets_available=5
    ),
    3: Event(
        _id=3,
        name='Wine festival',
        description="All I want is to be a monkey of moderate intelligence who wears a suit... that's why I'm "
                    "transferring to business school! Meh. We'll go deliver this crate like professionals, "
                    "and then we'll go home.",
        date_str='2024-12-11T14:00:00Z',
        tickets_available=1
    ),
    4: Event(
        _id=4,
        name='Annual Bicycle Appreciation Day',
        description="Yes, if you make it look like an electrical fire. When you do things right, people won't "
                    "be sure you've done anything at all. Oh dear! She's stuck in",
        date_str='2007-03-01T13:00:00Z',
        tickets_available=200
    ),
    5: Event(
        _id=5,
        name='Rocket to Mars',
        description="I'm nobody's taxi service; I'm not gonna be there to catch you every time you feel like "
                    "jumping out of a spaceship. I'm the Doctor, I'm worse than everyone's aunt. *catches "
                    "himself* And that is not how I'm introducing myself.",
        date_str='2047-10-21T09:00:00Z',
        tickets_available=0
    )
}


def get_all_events():
    return [e.to_dict() for e in EVENTS.values()]


reservations = {}


def create_reservation(event_id: int, body):
    e_id = int(event_id)

    if e_id not in EVENTS:
        abort(400, f"{e_id} is not a valid event ID. Valid ids are: {EVENTS.keys()}")

    if "tickets" not in body:
        abort(400, f"number of tickets to reserve not specified")

    event = EVENTS[e_id]
    tickets = body["tickets"]

    if tickets > event.tickets_available:
        abort(400, f"Event {e_id} does not have {tickets} ticket(s) available")

    event.tickets_available -= tickets

    reservation = Reservation(event_id=e_id, number_tickets=tickets)
    reservations[reservation.id] = reservation

    return reservation.to_dict()
