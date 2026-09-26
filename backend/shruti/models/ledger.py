# SPDX-License-Identifier: AGPL-3.0-only
"""
The Ledger: one company in one game, its businesses, and the weeks they ran.

A ledger is a save file's company — Big Ambitions, one difficulty, the courses
taken. A business in it is a plan that was kept, and later the weeks it
actually had. The reckoning (what a plan should come to) runs in the browser
and is never stored; these tables hold what a person chose and what they
wrote down (docs/LEDGER.md).

⚠ **A null line was not written, and it is never zero.** A week with money in
and no wages written is a week whose wages nobody knows, and a sum that read
the null as 0 would show a profit that never happened. Every line but the week
number is nullable for that reason, and nothing here fills one in.

⚠ **Private, all of it.** Nothing in a ledger is ever shown to anybody else,
so nothing needs the publishing agreement, and all three tables go with the
account (`ledger.user_id` is ON DELETE CASCADE, and the other two cascade from
it). They are in the export: `accounts._everything_else`.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field

from shruti.models import TimestampMixin, UTC_TS


class Ledger(TimestampMixin, table=True):
    """One company, in one game, at one difficulty."""

    __tablename__ = "ledger"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="site_user.id", ondelete="CASCADE")
    name: str
    game: str = Field(default="big-ambitions")
    # The game's version the figures were read against, so a ledger started
    # on 1.0 can say so after a patch changes the prices.
    version: str = ""
    # A difficulty id from the data pack (`normal`), or `custom` with its
    # values in `custom`.
    difficulty: str = Field(default="normal")
    custom: Optional[dict] = Field(default=None, sa_column=Column(JSONB, nullable=True))
    in_game_day: Optional[int] = Field(default=None)
    courses: list = Field(default_factory=list, sa_column=Column(JSONB, nullable=False))
    position: int = 0
    # ── on stream (the Ledger on stream; docs/LEDGER.md) ──
    # The business the stream is about: an OPEN business of this ledger, or
    # nothing. SET NULL when that business is deleted. `use_alter`, because a
    # business also points at its ledger.
    on_screen_business_id: Optional[int] = Field(default=None, sa_column=Column(
        Integer, ForeignKey("ledger_business.id", ondelete="SET NULL", use_alter=True,
                            name="fk_ledger_on_screen_business"), nullable=True))
    # The plan on stream, which may never have been kept: {"plan": {...},
    # "name": "..."}. Null when the planner's switch is off. One per ledger.
    live_plan: Optional[dict] = Field(default=None, sa_column=Column(JSONB, nullable=True))
    # When the live plan (or the switch) last changed: the overlay's clock.
    live_updated_at: Optional[datetime] = Field(default=None, sa_type=UTC_TS)
    # The planner's own diff of the last tap: {"label": "A second register", "delta": 12845}.
    live_change: Optional[dict] = Field(default=None, sa_column=Column(JSONB, nullable=True))


class LedgerBusiness(TimestampMixin, table=True):
    """
    One business: the plan as it stands, and the plan as it was kept.

    `kept_plan` is the plan when it was saved to the ledger; `plan` is where
    it has been taken since. The two differing is the "changed since you kept
    it" state, so neither is overwritten by the other here.
    """

    __tablename__ = "ledger_business"

    id: Optional[int] = Field(default=None, primary_key=True)
    ledger_id: int = Field(index=True, foreign_key="ledger.id", ondelete="CASCADE")
    name: str
    plan: dict = Field(default_factory=dict, sa_column=Column(JSONB, nullable=False))
    kept_plan: Optional[dict] = Field(default=None, sa_column=Column(JSONB, nullable=True))
    # Null: still a plan. A date: the business opened in the game.
    opened_at: Optional[datetime] = Field(default=None, sa_type=UTC_TS)
    position: int = 0


class LedgerWeek(TimestampMixin, table=True):
    """
    One in-game week of one business, as the person read it off the game.

    ⚠ Null is "not written". See the module's note before adding a default.
    """

    __tablename__ = "ledger_week"
    __table_args__ = (UniqueConstraint("business_id", "n", name="uq_ledger_week_business_n"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    business_id: int = Field(index=True, foreign_key="ledger_business.id", ondelete="CASCADE")
    n: int
    money_in: Optional[float] = Field(default=None)
    goods: Optional[float] = Field(default=None)
    wages: Optional[float] = Field(default=None)
    rent: Optional[float] = Field(default=None)
    ads: Optional[float] = Field(default=None)
    deliveries: Optional[float] = Field(default=None)
    units: Optional[int] = Field(default=None)
    customers: Optional[int] = Field(default=None)
    note: str = ""
