# SPDX-License-Identifier: AGPL-3.0-only
"""
Where a physical thing can be posted.

Stripe has no "anywhere" — `allowed_countries` wants an explicit list — so
"worldwide" has to be written out. This is that list: every ISO-3166 alpha-2
code Stripe accepts for a shipping address.

**Stripe refuses a handful outright** and a session naming one is rejected in
full, taking the whole checkout with it. Those are excluded here rather than
discovered by a buyer who cannot pay.

Listing a country is a promise to post there. The list is a setting, so it can
be narrowed the day that promise becomes inconvenient — but the default is
worldwide, because a shop that only ships to one country should say so on
purpose rather than by leaving a default alone.
"""
from __future__ import annotations

# Stripe does not accept these for shipping. Sanctions and territories without
# their own postal addressing, mostly.
UNSUPPORTED = frozenset({
    "AS", "CC", "CU", "CX", "HM", "IR", "KP", "MH", "MP", "FM",
    "NF", "PW", "SD", "SY", "UM", "VI",
})

_ALL = """
AD AE AF AG AI AL AM AO AQ AR AT AU AW AX AZ BA BB BD BE BF BG BH BI BJ BL BM
BN BO BQ BR BS BT BV BW BY BZ CA CD CF CG CH CI CK CL CM CN CO CR CV CW CY CZ
DE DJ DK DM DO DZ EC EE EG EH ER ES ET FI FJ FK FO FR GA GB GD GE GF GG GH GI
GL GM GN GP GQ GR GS GT GU GW GY HK HN HR HT HU ID IE IL IM IN IO IQ IS IT JE
JM JO JP KE KG KH KI KM KN KR KW KY KZ LA LB LC LI LK LR LS LT LU LV LY MA MC
MD ME MF MG MK ML MM MN MO MQ MR MS MT MU MV MW MX MY MZ NA NC NE NG NI NL NO
NP NR NU NZ OM PA PE PF PG PH PK PL PM PN PR PS PT PY QA RE RO RS RU RW SA SB
SC SE SG SH SI SJ SK SL SM SN SO SR SS ST SV SX SZ TA TC TD TF TG TH TJ TK TL
TM TN TO TR TT TV TW TZ UA UG US UY UZ VA VC VE VG VN VU WF WS XK YE YT ZA ZM
ZW
"""

WORLDWIDE: tuple[str, ...] = tuple(
    sorted({code for code in _ALL.split() if code not in UNSUPPORTED})
)


def allowed(configured: list[str] | None) -> list[str]:
    """
    The list to hand Stripe.

    Empty or unset means worldwide, which is the honest reading of "I have not
    said" for a shop: nothing was excluded, so nothing is.
    """
    if not configured:
        return list(WORLDWIDE)
    wanted = [c.strip().upper() for c in configured if c and c.strip()]
    if not wanted or wanted == ["*"]:
        return list(WORLDWIDE)
    # Anything Stripe refuses is dropped rather than passed on, because one bad
    # code fails the whole session and the buyer is the one who finds out.
    return [c for c in wanted if c in WORLDWIDE]
