# Taschengeld & Challenges

Single-file web app for tracking Juna's and Artus's reading challenges, pocket money,
spending, and a virtual savings portfolio. Deployed as a static page on GitHub Pages,
used on an iPad from the home screen.

**No build step. No dependencies. No service worker.** `index.html` is the entire app.

## Deploy

Push `index.html` to `main`. Pages serves it from the repo root.
To force iOS to pick up a new version, open the URL once in Safari with `?v=N` appended.

## Data

Everything lives in `localStorage` under the key `challenges_v2`, on the device only.
There is no backend and no sync. The parent view has JSON export/import; back up after
each payout. Note that `localStorage` is scoped to the `github.io` origin, so it is shared
with other Pages projects on the same account (keys do not collide, but clearing website
data in Safari wipes all of them).

## Payout rules

### Juna — 20 weeks, from 7 Sept 2026
| Item | Payout |
|---|---|
| Reading, 20 min/day, ≥5 of 7 days | weeks 1–4 €2 · 5–8 €4 · 9–12 €5 · 13–16 €6 · 17–20 €8 |
| Books, 200+ pages, her choice | €4 / €7 / €10 / €14 |
| Unknown words marked while reading | €0.10 each, capped €1/week |
| Handstand 3s (3x in one day) | €20 |
| Handstand 10s | €80 |
| 10 steps on hands | €50 |
| Pocket money | €20/month, unconditional |

Maximum: **€305**

### Artus — 10 weeks, from 7 Sept 2026
| Item | Payout |
|---|---|
| Reading aloud, 10 min/day, ≥5 of 7 days | weeks 1–3 €1 · 4–6 €1.50 · 7–10 €2 |
| Bonus: 15 min on ≥4 days in a week | €1 |
| Erstlesebücher, one per fortnight | €2 each, 5 books |
| Pocket money | €2/week, unconditional |

Maximum: **€35.50**. No physical challenge in this cycle.

The weekly rate ladder advances on **qualifying weeks, not calendar weeks**. A missed week
costs nothing already earned; it only delays reaching the higher rate.

## Logging

The big stamp on the Heute screen logs today. The two week rows underneath (last week and
this week) are tappable for any day inside a rolling **7-day window**, so a forgotten or
mistaken day can be corrected. Tapping cycles: empty → base minutes → bonus minutes (only
where a bonus tier exists) → empty. Days older than 7 days and future days render dimmed
and do not respond.

## Savings

Deposits go into Bitcoin, a world ETF, or an equal-weighted basket of nine companies
(Alphabet, Microsoft, SpaceX, NVIDIA, Apple, Amazon, TSMC, Meta, Tesla). The basket is an
index, base 100, averaged across the nine components' own base-100 indices.

Any deposit held **365 days** earns a **50% match on the deposited amount**, not on market
value — so a drawdown of up to 33% still leaves the child above principal. Selling before
365 days forfeits that deposit's match. Each deposit runs its own clock.

Deposits store the instrument's price on the buy date (`px`), so refreshing prices never
retroactively distorts holdings.

## Price feed

Manual refresh only, from the parent view. Nothing fetches on page load, so a dead source
never blocks the child from logging a reading day. Failures leave the last price in place.

**No API key.** Prices come from a Google Sheet published with "anyone with the link can
view". The sheet holds two columns — key and value in EUR — and uses `GOOGLEFINANCE()`
formulas that Google keeps current. The parent view has a "Vorlage für die Tabelle" button
that copies the exact rows to paste into A1.

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

## Parent view

PIN-gated, default `1234`, changeable in settings. Covers: settlement figure, booking
payouts, ticking off books and milestones, entering word counts, price refresh and manual
price overrides, challenge start dates, pocket money amounts, and JSON backup.
