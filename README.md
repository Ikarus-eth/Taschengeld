# Taschengeld & Challenges

Single-file web app for tracking Juna's and Artus's reading challenges, pocket money,
spending, and a virtual savings portfolio. Deployed as a static page on GitHub Pages,
used on an iPad from the home screen. The interface is in English.

**No build step. No dependencies. No service worker.** `index.html` is the entire app;
the only other files served are the icon PNGs and the manifest.

## Deploy

Push `index.html` to `main`. Pages serves it from the repo root.
To force iOS to pick up a new version, open the URL once in Safari with `?v=N` appended.

## Home screen icon

`apple-touch-icon.png` is a 180x180 opaque PNG, full bleed, no rounded corners — iOS masks
it into a squircle itself and fills any transparency with black. All icon hrefs are
relative because the site is served from `/Taschengeld/`, so iOS cannot find an icon at the
domain root on its own.

The artwork lives at `tools/icon-source.png`. To change the icon, replace that file and run
`python3 tools/prepare-icon.py`, which flattens any transparency, floods the corners with
the background colour so nothing is masked twice, and writes `apple-touch-icon.png`,
`icon-512.png` and `favicon-32.png`. Needs Pillow, runs by hand, is not part of any deploy.

Changing the icon does not update a shortcut that is already on the home screen: iOS caches
the icon when the shortcut is created. Delete it and add it again.

## Data

Everything lives in `localStorage` under the key `challenges_v2`, on the device only.
The price-sheet URL is mirrored into a second key, `challenges_feed`, and restored from
there if the main blob ever loses it — an app update or a partial backup restore cannot
unlink the feed.
There is no backend and no sync. The parent view has JSON export/import; back up after
each payout. Note that `localStorage` is scoped to the `github.io` origin, so it is shared
with other Pages projects on the same account (keys do not collide, but clearing website
data in Safari wipes all of them).

## Payout rules

### Juna — 20 weeks, from 31 Aug 2026 (ends Sun 17 Jan 2027)
| Item | Payout |
|---|---|
| Reading, 20 min/day, ≥5 of 7 days | weeks 1–4 €2 · 5–8 €4 · 9–12 €5 · 13–16 €6 · 17–20 €8 |
| Books, 200+ pages, her choice | €4 / €7 / €10 / €14 |
| New words marked while reading | €0.10 each, capped €1/week — 10 words fills the week |
| Handstand 3s (3x in one day) | €20 — by 25 Dec 2026 |
| Handstand 10s | €80 — by 25 Dec 2026 |
| 10 steps on hands | €50 — by 25 Dec 2026 |
| Pocket money | €20 on the 1st of each month, unconditional |

Maximum: **€305**

### Artus — 10 weeks, from 31 Aug 2026 (ends Sun 8 Nov 2026)
| Item | Payout |
|---|---|
| Reading aloud, 10 min/day, ≥5 of 7 days | weeks 1–3 €1 · 4–6 €1.50 · 7–10 €2 |
| Bonus: 15 min on ≥4 days in a week | €1 |
| Early readers, one per fortnight | €2 each, 5 books |
| Pocket money | €2 every Monday, unconditional |

Maximum: **€35.50**. No physical challenge in this cycle.

## Pocket money

Paid on the **first day of a period**, never pro-rated for a part period. Monthly lands on
the 1st, starting with the first 1st that falls on or after the challenge start; weekly
lands on Monday, same rule. Juna's challenge starts Mon 31 Aug 2026, so August pays
nothing and her first €20 arrives on 1 Sep. Counting calendar months *touched* — the old
behaviour — paid twice within two days.

The Money screen states the date of the next payment under the pocket money row.

## Deadlines

The sport goals have their **own** deadline, Friday 25 December 2026, 23 days before the
reading challenge ends. It is stored per milestone as `due`; a milestone without one falls
back to the challenge end. The parent view has a date field that moves all three at once,
and clearing it returns them to the challenge end.

An unreached goal whose date has passed leaves the *still possible* figure, so the maximum
drops from €305 to €155 on 26 December if none were reached. The parent can still mark one
reached after the date — it pays, and the review log records when it was booked.

Everything else runs in whole Monday-to-Sunday weeks, so that deadline is the Sunday closing
the last week — `monday(start) + weeks*7 - 1`, not `start + weeks*7`. Juna: Sunday 17 Jan
2027. Artus: Sunday 8 Nov 2026. A start date that is not a Monday still ends on a Sunday.

The Goals screen opens with a Time left card: how long is left in words, the deadline
written out, a bar of weeks elapsed, and which week of how many. It has three states —
before the start it says when it begins, during it counts down, and afterwards it says the
challenge finished and that what was earned is still hers. Every unfinished sport goal and
empty book slot carries `by 17 Jan`, the books card says how many are left and by when, and
after the deadline the wording switches from asking to stating (`not reached in time`)
rather than continuing to nag.

The word box shows the Sunday its week closes, and the last-week row says it stays open
until the end of the current week, which matches `wordEditable`.

The weekly rate ladder advances on **qualifying weeks, not calendar weeks**. A missed week
costs nothing already earned; it only delays reaching the higher rate.

## Logging

The big stamp on the Today screen logs today. The two week rows underneath (last week and
this week) are tappable for any day inside a rolling **7-day window**, so a forgotten or
mistaken day can be corrected. Tapping cycles: empty → base minutes → bonus minutes (only
where a bonus tier exists) → empty. Days older than 7 days and future days render dimmed
and do not respond.

Juna ticks the **new words** box herself on the Goals screen once she has marked 10 words
in a week; that fills the week's €1 cap. This week and last week are tappable, older weeks
are locked. The parent view keeps a numeric entry for partial counts.

## Savings

Deposits go into Bitcoin, a world ETF, or an equal-weighted basket of nine companies
(Alphabet, Microsoft, SpaceX, NVIDIA, Apple, Amazon, TSMC, Meta, Tesla). The basket is an
index, base 100, averaged across the nine components' own base-100 indices.

Each company is a tappable row showing what it is in one line, and opens an explainer with
what they make and **where the child has already seen it** — the iPad in her hands for
Apple, Minecraft for Microsoft, WhatsApp for Meta, the chip inside the iPad for TSMC. The
copy lives in the `CO` map in `index.html`; a ten-year-old cannot picture a semiconductor
foundry, so every entry has to name a thing she can point at. A "What is a share?" dialog
covers ownership, why prices move, that the price is a collective guess about the future,
and why nine companies move less than one. It is offered from the fund and the basket but
not from Bitcoin, which is not a company.

Any deposit held **365 whole days** (counted noon-to-noon, so the countdown ticks once a
day and does not shift with the clock or a timezone change) earns a **50% match on the
deposited amount**, not on market
value — so a drawdown of up to 33% still leaves the child above principal. Selling before
365 days forfeits that deposit's match. Each deposit runs its own clock.

Deposits store the instrument's price on the buy date (`px`), so refreshing prices never
retroactively distorts holdings.

**Selling.** Each open holding has a Sell button. The confirmation states the current value
and, if the deposit has not reached 365 days, the exact match amount being given up. A sale
freezes `soldValue` at that day's price; later price moves do not change a completed sale.
Vested sales keep the match (`matchClaimed`). Sold deposits stay in the ledger and are
listed under "Already sold".

Cash accounting: every euro ever deposited is debited from the balance and a sale credits
its proceeds back. Subtracting only *open* principal would hand the stake back for free on
every sale.

The Saving screen carries a three-level swing indicator per instrument, a per-instrument
explainer (why people like it / what to watch out for), and a "How saving works" dialog
with the payoff table down to a 50% drawdown, where the match makes the child break even.

## Price feed

Manual refresh from the parent view, plus a **background auto-refresh**: at most once every
6 hours, started 1.5 s after the first paint and on returning to the app. Nothing is fetched
*during* load and nothing is awaited on the critical path, so a dead source still never
blocks the child from logging a reading day. Every request has a 9 s timeout; failures are
silent and leave the last price in place. The parent view can switch auto-refresh off.

**No API key.** Prices come from a Google Sheet published with "anyone with the link can
view". The sheet holds two columns — key and value in EUR — and uses `GOOGLEFINANCE()`
formulas that Google keeps current. The parent view has a "Sheet template" button that
copies the exact rows to paste into A1, and a "Test the link" button that reports whether
the sheet is readable from the device.

Keys the app reads: `EURIDR`, `btc`, `etf`, and the nine company names. Values are read in
EUR, so USD tickers are divided by `CURRENCY:EURUSD` inside the sheet — the app does no
currency conversion of its own.

The app accepts either a normal sheet URL or a published-CSV URL, and tries the `gviz`
and `pub?output=csv` endpoint shapes in turn. The CSV parser handles quoted fields and
both `1.234,56` and `1,234.56` number formats, so the sheet's locale doesn't matter.

Fallbacks when the sheet is unreachable or a row is missing:

| Source | Covers | Key |
|---|---|---|
| `api.coinbase.com/v2/prices/BTC-EUR/spot` | Bitcoin | none |
| `api.frankfurter.app` | EUR→IDR (ECB daily) | none |

SpaceX has traded on Nasdaq as `SPCX` since its IPO on 12 June 2026, so it is a normal
row like the rest. No manual field.

The rupiah rate is also editable by hand in the parent view, with the timestamp of the last
automatic update shown next to it.

## Spending and extra money

Pocket money and all balances are in **euro**. A purchase can be entered in **rupiah**: it
is converted at that day's rate and the record stores `idr`, `fx` and the resulting `eur`,
so a later rate move never rewrites past spending. The spending list shows the original
rupiah amount and the rate used.

**Extra money** (birthday money, a gift from Oma) is a separate category from both pocket
money and challenge payouts. It is added to the balance and appears in "Where the money
comes from", but it never counts towards *earned* and never affects the challenge total.
It can also be entered in rupiah.

## Review log

Every change to state is appended to `S.log`, capped at 1200 entries. An entry records the
moment of the tap (`t`), a monotonic sequence number (`n`), the day it refers to (`d`), who
made it (`by`: `p` if the parent view was open, otherwise `k`), the euro effect, and the
`earned` and `cash` totals as they stood immediately after. Nothing in the app deletes an
entry; restoring a backup unions the two logs rather than replacing.

The parent view's Review section shows the log grouped by the day the action was taken,
with a summary and a "needs a look" count. Windows: since the last check, 7 days, 30 days,
everything. "Mark as checked" stores the highest sequence number seen, per child — a
sequence number, not a timestamp, so a clock correction or a flight between timezones
cannot hide a new entry or resurface an old one. Export writes a CSV.

Flagged automatically:

| Flag | Why |
|---|---|
| filled in *n* days later | back-filling is allowed up to 7 days, so lateness is the thing to eyeball |
| *n* days entered on this one day | three or more past days entered in one day, covering three or more dates |
| day cleared | a logged day was removed again |
| ticked by *name* | the child ticked her own word week |
| money added by hand | extra money is the only entry that creates money from nothing |
| setting changed / backup restored | anything that moves the totals without an activity behind it |

Not a security boundary: it is a record on a device the child holds. It catches casual
inflation of the numbers, not someone editing `localStorage` directly.

## Parent view

PIN-gated, default `1234`, changeable in settings. Covers: settlement figure, booking
payouts, the review log, ticking off books and milestones, entering word counts, adding extra money, price
refresh and manual price overrides, the auto-refresh toggle, challenge start dates, pocket
money amounts, and JSON backup.
