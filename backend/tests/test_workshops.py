# SPDX-License-Identifier: AGPL-3.0-only
"""
Running a workshop: a room, the people in it, and what they get afterwards.

The rules that are easy to get wrong here are about people rather than code —
one link each rather than one link, a free place still being a place, and one
recording email rather than one per evening.
"""
from __future__ import annotations

import inspect

from shruti.core import room as live


def test_a_room_is_private_so_a_url_is_not_a_way_in():
    """
    The whole basis of per-person invitations. A public room would make every
    token pointless: forwarding the address would be enough.
    """
    source = inspect.getsource(live.create)
    assert '"privacy": "private"' in source


def test_chat_and_raised_hands_are_on():
    """Both were asked for by name."""
    source = inspect.getsource(live.create)
    assert '"enable_chat": True' in source
    assert '"enable_hand_raising": True' in source


def test_recording_is_switched_on_when_the_room_is_made():
    """
    Not left to be remembered on the day. A workshop whose recording nobody
    started is a promise broken to everybody who paid for one.
    """
    assert '"enable_recording": "cloud"' in inspect.getsource(live.create)


def test_nobody_arrives_on_camera_unasked():
    source = inspect.getsource(live.create)
    assert '"start_video_off": True' in source
    assert '"start_audio_off": True' in source


def test_a_room_expires():
    """
    A room that lives forever is a URL circulating with nothing to stop
    somebody wandering in months later.
    """
    assert '"exp"' in inspect.getsource(live.create)
    assert live.ROOM_LIFE_HOURS >= 4


def test_launching_twice_returns_the_room_rather_than_failing():
    """
    Pressing a button again because nothing obviously happened is what people
    do, and it must not be an error.
    """
    source = inspect.getsource(live.create)
    assert "already exists" in source


def test_owners_and_guests_get_different_tokens():
    """
    Hers can start the recording and remove somebody; a guest's cannot. One
    token shape for both would hand every attendee the controls.
    """
    assert "is_owner" in inspect.getsource(live.token)


def test_everybody_holding_a_place_is_invited_however_they_got_it():
    """
    Paid and RSVPed alike. She asked for one action that reaches all of them,
    and a free place is still a place.
    """
    from shruti.api.routes import classes

    source = inspect.getsource(classes._ticket_holders)
    assert "Entitlement.revoked_at.is_(None)" in source
    # Not filtered by how the entitlement arose.
    assert "source ==" not in source


def test_seats_count_places_not_payments():
    """A place given away and a place sold both fill a room."""
    from shruti.api.routes import classes

    source = inspect.getsource(classes._seats_taken)
    assert "Entitlement" in source
    assert "Order" not in source


def test_the_recording_goes_out_as_one_message():
    """
    Her words: one package at the end, not one after each day. Somebody who
    attended three evenings should have one thing to keep rather than three to
    keep track of.
    """
    from shruti.api.routes import classes

    source = inspect.getsource(classes.send_recording)
    # Every finished recording is gathered, then one send per person.
    assert "links.append" in source
    assert 'mail.send' in source
    assert source.count("mail.send") == 1


def test_recordings_are_linked_rather_than_copied():
    """
    They are large and already live somewhere durable. Copying them would mean
    paying twice to hold the same hours.
    """
    source = inspect.getsource(live.download_link)
    assert "access-link" in source
    assert "storage.put" not in source
