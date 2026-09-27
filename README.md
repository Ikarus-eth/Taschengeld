# Taschengeld & Challenges

Single-file web app for tracking Juna's and Artus's reading challenges, pocket money,
spending, and a virtual savings portfolio, plus Nalu's pocket-money jar. Deployed as a static page on GitHub Pages,
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
| Pocket money | €2 every Sunday from 6 Sep 2026, unconditional |

Maximum: **€35.50**. No physical challenge in this cycle.

### Nalu — pocket money only (born 2021)
| Item | Payout |
|---|---|
| Pocket money | Rp 20,000 (four Rp 5,000 notes) every Sunday from 6 Sep 2026, unconditional |

No challenge. Started late September 2026 and backdated to the start of September, so the
four September Sundays were in the jar on day one. See [Nalu's jar](#nalus-jar).

## Pocket money

Paid on the **first day of a period**, never pro-rated for a part period. Monthly lands on
the 1st, starting with the first 1st that falls on or after the start; weekly lands on the
child's pay day (`payDay`, 0 = Sunday … 6 = Saturday, Monday if unset), same rule. The start
is `allowanceFrom` if set, otherwise the challenge start. Juna's challenge starts Mon 31 Aug
2026, so August pays nothing and her first €20 arrives on 1 Sep. Counting calendar months
*touched* — the old behaviour — paid twice within two days.

Artus and Nalu are paid on **Sunday**, counted from 1 Sep 2026 (`allowanceFrom`), so the
first payment is Sun 6 Sep. Artus was on Mondays from 31 Aug until 27 Sep 2026; both rules
give €8 on 27 Sep, so the switch moved nothing he could see that day. From then on a
Sunday pays what the following Monday used to.

Pocket money is **derived, not booked**: `periods × amount`, recomputed on every render.
Changing the amount, the pay day or the start date in the parent view therefore changes
every past period too. That is what made the September backdating a one-field change, and
it is also why a raise should not be entered by editing the amount (see PROJECT.md).

The Money screen and Nalu's jar state the date of the next payment.

## Nalu's jar

Nalu is five and does not read numbers yet, and rupiah amounts have too many zeros. His
side of the app is one screen, the **Jar**, plus the parent view; the tab bar hides Today,
Goals, Money and Saving for him.

- **The unit is a note, not a currency.** His ledger is kept in rupiah (`allowanceIdr`,
  and `idr` on every record), with `note: 5000`. Rp 20,000 a week is always exactly four
  notes; a euro-based ledger would drift with the exchange rate and show him 3.9 notes.
  Each record also stores `eur` and `fx` at the day's rate, for information only.
- **The jar draws the notes.** Rows of five, ten to a frame, filling from the bottom, so
  four reads as a shape before it reads as a number. Past 49 notes, full tens collapse
  into bundles marked 10. The count is shown large beside the jar, with the rupiah value
  small underneath. Amounts that are not whole notes show as change.
- **Sunday is visible.** On pay day the four new notes have a gold edge and drop in once
  per day. Other days show "4 notes more on Sunday" with one moon per sleep.
- **In and out** lists pocket money, purchases, gifts and cash handed over as rows of
  small notes with +4 / −2.
- **Taking out and putting in** use a stepper (− / +) that draws the notes as they are
  counted, with an optional exact rupiah field. Taking out is capped at what is in the
  jar. "I bought something" and "I got money" are on the jar; "Hand over as cash" is in
  the parent view, for when real notes move into a physical jar or wallet.
- Everything goes through `logEvent` like the other children; jar entries also carry
  `jar`, the rupiah balance after the change. The review summary and CSV export switch
  to rupiah for him.

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

Cash accounting: a sale hands back a stake the child already owned, so the sale amount is
not income — only the difference the price made is. The balance therefore counts the
**realised** gain or loss (`proceeds - soldPrincipal`) as money in, and only the principal
still tied up in **open** holdings as money out. This is algebraically identical to
crediting gross proceeds and debiting every euro ever deposited
(`proceeds - principalAll == realized - principalOpen`), so no stored data changes, but it
keeps a buy and a sell at the same price from inflating any total the child sees. `invested()`
also returns `unrealized` (open value minus open principal) and `turnover` (principal that
has gone in and come back out again) — turnover is a volume, never income.

**Money screen.** "Where the money comes from" lists only money the child actually
received — the challenge lines, pocket money, gifts and extras — and closes with a
**Money in total** subtotal. It deliberately does not say *earned*, because the Goals
screen already uses that word for challenge money alone and pocket money is unconditional.
"What is left" then reconciles to the balance: money in, plus the saving match, plus or
minus the realised investment result, minus spending, minus principal still invested,
minus payouts already made. A note underneath states the turnover when there is any, so a
buy-and-sell round trip reads as volume rather than as income.

The Saving screen carries a three-level swing indicator per instrument, a per-instrument
explainer (why people like it / what to watch out for), and a "How saving works" dialog
with the payoff table down to a 50% drawdown, where the match makes the child break even.

## Compounding playground

A separate screen (`VIEW="grow"`) reached from the **What if I wait?** button on Saving and
from a link in the "How saving works" dialog. It is a toy: it reads nothing from the ledger,
writes nothing, and touches no saved state. The Saving tab stays lit in the nav while it is
open, and a "Back to saving" button sits at the top.

Two modes over the same maths, solved for a different unknown:

| Mode | Given | Solved for |
|---|---|---|
| What does it turn into? | start, monthly, rate, years | final value |
| How do I reach a goal? | goal, start, rate, years | monthly amount |

Monthly compounding with the deposit at the **end** of each month, matching how her own
deposits land and keeping the goal solver a closed form rather than a search:

```
i = rate/100/12,  g = (1+i)^months
FV  = P0·g + PMT·(g−1)/i
PMT = (FV − P0·g)·i/(g−1)
```

Both degrade to plain addition at `i = 0`. `pmtFor` inverts `fvOf` to floating-point
precision (worst relative error ~1e-16 over a 3,000-state fuzz). A goal already covered by
the starting amount clamps the monthly to zero and says so rather than showing a negative.

Sliders: start €0–500, monthly €0–100, rate 0–15% in half steps, horizon 1–50 years. The
horizon label shows the child's age at the end, from a new per-child `born` field
(Juna 2016, Artus 2019) — it is the line that makes fifty years mean something. Goal chips
run €500 to €1m.

Sliders repaint **in place** (`growPaint` swaps the readout, the chart and the labels)
rather than through `render()`; re-creating the `<input>` under a finger that is still
dragging it cancels the drag on iOS. Mode switches do go through `render()`, because they
change which sliders exist.

The chart is inline SVG, one stacked bar per year: contributions in the accent colour at
32% opacity, growth on top in gold. The widening gold band *is* the lesson. Bars stop
widening past a 94px slot and the group centres, so a one-year horizon reads as a small
chart rather than a broken one. In goal mode a dashed line marks the target, with the scale
padded 8% above it so the line does not land on the top edge in exactly the case that
matters — the plan that works out.

Honesty is load-bearing here: a note under the sliders states that the machine pretends the
price climbs by the same amount every year and that real prices do not, and the rate hint
anchors 1% to a bank account, ~7% to the world fund's long-run average and 12% to a lucky
run rather than a plan. The "Why does it curve upwards?" dialog covers the slice-of-the-pile
mechanism, the rule of 72, a €10/month table from 10 to 50 years, and a paragraph on
inflation.

`fmtShort()` handles the axis and chip labels, since `fmt()` spells out every digit and is
unreadable at a million or in rupiah. `fmt()` and `eur()` now put thousands separators on
the euro side as well (via `euros()`); everyday two- and three-digit balances look
identical, but this screen runs to seven.

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

For Juna and Artus, pocket money and all balances are in **euro** (Nalu's jar is in rupiah, see above). A purchase can be entered in **rupiah**: it
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

PIN-gated, default `1234`, changeable in settings. For weekly pocket money it also sets the
pay day and the date pocket money is counted from. Nalu's parent view shows the jar
statement, cash handed over, his review log and his pocket-money settings. Covers: settlement figure, booking
payouts, the review log, ticking off books and milestones, entering word counts, adding extra money, price
refresh and manual price overrides, the auto-refresh toggle, challenge start dates, pocket
money amounts, and JSON backup.
