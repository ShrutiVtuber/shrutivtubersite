# SPDX-License-Identifier: AGPL-3.0-only
"""
Names read out on stream, and whose.

Her note: "when someone makes a donation or purchases a membership we need to
make sure that they have a place to supply their name to be read on stream (if
they want a custom name). **This is only for monthly supporters - one offs are
not read on stream.**"

The rule is kept where the name is ASKED FOR rather than where it is displayed.
The one-off checkout builder has no field to fill in, so a one-off gift cannot
carry a name at all — that is a fact about the code rather than a filter
somebody could later remove from a query.
"""
from __future__ import annotations

from shruti.api.routes.billing import (
    _chosen_name, _one_off_line_items, _subscription_line_items,
)


def test_the_subscription_checkout_asks_for_a_name() -> None:
    params = _subscription_line_items("price_123", "lamplighter")
    fields = params.get("custom_fields") or []
    assert [f["key"] for f in fields] == ["stream_name"]
    assert fields[0]["optional"] is True, (
        "being named must be optional — plenty of people would rather not be"
    )


def test_a_one_off_gift_has_nowhere_to_put_one() -> None:
    """
    Not a check, an absence. There is no field, so there is nothing to fill in
    and nothing to filter out later.
    """
    params = _one_off_line_items(1000)
    assert "custom_fields" not in params
    assert params["mode"] == "payment"


def test_the_name_is_read_out_of_the_checkout_session() -> None:
    session = {"custom_fields": [
        {"key": "stream_name", "text": {"value": "  Soror Eu. A.  "}},
    ]}
    assert _chosen_name(session) == "Soror Eu. A."


def test_a_session_with_no_fields_gives_nothing() -> None:
    """
    Every other billing webhook reaches the same code path — a renewal, a card
    change — and none of them carry custom fields. Returning anything but the
    empty string here would wipe a name she reads out every month.
    """
    assert _chosen_name({}) == ""
    assert _chosen_name({"custom_fields": []}) == ""
    assert _chosen_name({"custom_fields": [{"key": "something_else",
                                            "text": {"value": "no"}}]}) == ""


def test_a_very_long_name_is_cut_rather_than_refused() -> None:
    """Somebody pasting an essay gets a name, not an error at the till."""
    long = "x" * 500
    assert len(_chosen_name({"custom_fields": [
        {"key": "stream_name", "text": {"value": long}}]})) == 60


def test_an_empty_name_never_overwrites_a_kept_one() -> None:
    """
    The upsert only ever SETS this field. Read the source rather than the
    behaviour, because the alternative is a fixture for every webhook Stripe
    sends.
    """
    import inspect

    from shruti.api.routes import billing

    source = inspect.getsource(billing._upsert)
    assert "if stream_name:" in source, (
        "_upsert no longer guards the empty case — a renewal webhook will now "
        "silently forget the name she reads out"
    )
