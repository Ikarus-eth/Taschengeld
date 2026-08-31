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

## Savings

Deposits go into Bitcoin, a world ETF, or an equal-weighted basket of nine companies
(Alphabet, Microsoft, SpaceX, NVIDIA, Apple, Amazon, TSMC, Meta, Tesla).

Any deposit held **365 days** earns a **50% match on the deposited amount**, not on market
value — so a drawdown of up to 33% still leaves the child above principal. Selling before
365 days forfeits that deposit's match. Each deposit runs its own clock.

Deposits store the instrument's price on the buy date (`px`), so refreshing prices never
retroactively distorts holdings.

## Price feed

Manual refresh only, from the parent view. Nothing fetches on page load, so a dead API
never blocks the child from logging a reading day. Failures leave the last price in place.

| Source | Covers | Key |
|---|---|---|
| `api.frankfurter.app` | EUR→USD and EUR→IDR (ECB daily) | none |
| `api.coinbase.com/v2/prices/BTC-EUR/spot` | Bitcoin | none |
| `finnhub.io/api/v1/quote` | URTH, GOOGL, MSFT, NVDA, AAPL, AMZN, TSM, META, TSLA | free key |

The Finnhub key is entered in the parent view and stored in `localStorage`. **It is never
committed to this repo.** Without it, Bitcoin and FX still update; the eight stocks do not.

SpaceX is private and has no feed. Its value is set by hand in the parent view, indexed to
100 at the start.

Stock quotes arrive in USD and are converted to EUR with the ECB rate.

## Parent view

PIN-gated, default `1234`, changeable in settings. Covers: settlement figure, booking
payouts, ticking off books and milestones, entering word counts, price refresh and manual
price overrides, challenge start dates, pocket money amounts, and JSON backup.
