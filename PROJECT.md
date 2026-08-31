# Project: Taschengeld & Challenges

Working brief for any new chat. Read this first, then fetch the live repo before changing
anything — this file describes intent and workflow, the repo is the source of truth.

## What this is

A single-file web app that tracks two children's reading challenges, pocket money,
spending, and a virtual savings portfolio. Used by the kids on an iPad from the home
screen; the parent view is PIN-gated. The whole interface is in English.

- Repo: `Ikarus-eth/Taschengeld`, branch `main`, root folder
- Live: https://ikarus-eth.github.io/Taschengeld/
- Files: `index.html` (the entire app), `apple-touch-icon.png` / `icon-512.png` /
  `favicon-32.png` / `manifest.webmanifest` (home screen assets),
  `tools/make-icons.py` (regenerates those PNGs, run by hand, never at deploy),
  `README.md` (spec), `PROJECT.md` (this file)

## GitHub access

```
<token lives in the Claude Project knowledge file, not in this repo —
 GitHub push protection blocks it here>
```

Fine-grained token, `Contents: Read and write` on this repo. If a call returns
`Resource not accessible by personal access token`, the token has expired or lost its
permission — say so rather than working around it.

Read a file:

```bash
curl -s https://raw.githubusercontent.com/Ikarus-eth/Taschengeld/main/index.html -o index.html
```

Push a file (needs the current blob sha when the file already exists):

```bash
T=<token>; REPO=Ikarus-eth/Taschengeld; F=index.html
SHA=$(curl -s -H "Authorization: Bearer $T" \
  "https://api.github.com/repos/$REPO/contents/$F" \
  | python3 -c "import sys,json;print(json.load(sys.stdin).get('sha',''))")
python3 - <<PY > /tmp/p.json
import base64,json
b={"message":"<commit message>","content":base64.b64encode(open("$F","rb").read()).decode(),"sha":"$SHA"}
print(json.dumps(b))
PY
curl -s -X PUT -H "Authorization: Bearer $T" \
  "https://api.github.com/repos/$REPO/contents/$F" --data-binary @/tmp/p.json
```

Verify after pushing: poll `api.github.com/repos/$REPO/pages/builds/latest` until
`status: built` (~40 s), then diff the local build against the **contents API**, not
`raw.githubusercontent.com`:

```bash
curl -s -H "Authorization: Bearer $T" "https://api.github.com/repos/$REPO/contents/$F" \
  | python3 -c "import sys,json,base64;sys.stdout.buffer.write(base64.b64decode(json.load(sys.stdin)['content']))"
```

`raw.githubusercontent.com` caches for a couple of minutes and will happily serve the
*previous* version after a successful push. That looks exactly like a failed push and is
not one. The contents API is authoritative and immediate. Note that `ikarus-eth.github.io` is **not** on the sandbox
network allowlist, so fetching the live site directly returns a 403 from the proxy —
that is not a site failure. Use `raw.githubusercontent.com`, which is allowlisted.

## Working agreement

- **Test before pushing.** Extract the `<script>` block, `node --check` it, then stub the
  DOM and run the earnings and savings engines against full-completion and edge scenarios.
  Prior chats caught real bugs this way. Do not push untested changes.
- **No build step, no dependencies, no service worker.** `index.html` is self-contained
  apart from static icon files, which the browser fetches but the app never reads.
  A service worker in an earlier project (blitzword) caused a cache bug that cost hours.
- **Every asset path is relative.** The site is served from `/Taschengeld/`, not a domain
  root, so a leading slash points at `ikarus-eth.github.io/` and 404s. This is why iOS
  could not auto-discover `/apple-touch-icon.png` and why the link tag is required.
- **Nothing is fetched during load, and no fetch is ever awaited on the critical path.**
  Prices now also auto-refresh in the background — 1.5 s after the first paint and on
  returning to the app, throttled to once per 6 hours, 9 s timeout, silent on failure.
  This replaces the earlier "manual button only" rule (Aug 2026): the constraint that
  mattered was that a dead API can never block a child from logging a reading day, and a
  deferred non-blocking fetch keeps that. The parent view can switch it off.
- Child-facing copy is English (was German until Aug 2026). Code and comments in English.
- iPad-first: large touch targets, minimal text, works in portrait.

## Design decisions worth not re-litigating

- **The weekly ladder advances on qualifying weeks, not calendar weeks.** A missed week
  delays the higher rate but never resets progress or costs money already earned. A joker
  system was considered and dropped as redundant.
- **The savings match is 50% of the deposited amount, not of market value.** This puts a
  floor under the child: a drawdown up to 33% still leaves them above principal. Each
  deposit runs its own 365-day clock. Selling early forfeits that deposit's match only.
- **Deposits store the instrument's price on the buy date**, so refreshing prices never
  retroactively distorts existing holdings.
- **Selling is allowed at any time.** A sale freezes `soldValue` at that day's price, keeps
  the match only if the deposit was already 365 days old, and leaves the record in the
  ledger. Cash accounting debits *every* euro ever deposited, not just the open principal —
  subtracting only open principal returns the stake for free on each sale. That bug was
  latent in the ledger until selling existed; it is fixed and covered by a test.
- **Spending can be entered in rupiah**, converted at that day's rate and frozen there
  (`idr`, `fx`, `eur` all stored). Balances themselves stay in euro.
- **Extra money** (gifts, birthday money) is a third category, separate from pocket money
  and challenge payouts. It lands in the balance but never counts as *earned*.
- **The word bonus is a weekly checkbox for the child**, not a number only a parent can
  enter: 10 marked words fills the week's €1 cap. This week and last week are tappable.
- **Pocket money is unconditional** and strictly separate from challenge payouts. It is
  never tied to grades, chores, or behaviour, and is never clawed back.
- **It is paid on the first day of a period, never pro-rated.** Monthly on the 1st, weekly
  on Monday, counting from the first such day on or after the challenge start. The original
  code counted calendar months *touched*, so a 31 Aug start paid August and September
  within two days. Fixed Sept 2026; do not reintroduce month-difference arithmetic on the
  raw start date.
- **Day counts compare noon-anchored dates and round, never floor.** The family moves
  between Bali (no DST) and Europe (DST), so a raw ms division can be off by an hour and
  shift a week index or a vesting countdown by one. Applies to `weekIndex`,
  `allowancePeriods` and `daysHeld`.
- Cash balance is allowed to go negative rather than blocking a payout entry, so the
  parent can settle amounts that do not match the ledger exactly.
- Earned and spent are shown as two separate totals with the balance derived, rather than
  one number that shrinks — spending should not feel like losing.

## Price feed

No API key. A published Google Sheet holds `key,value` rows with prices in EUR, computed
by `GOOGLEFINANCE()` formulas. The parent view has a button that copies the template.
The app accepts either a normal sheet URL or a published-CSV URL and tries the `gviz` and
`pub?output=csv` endpoint shapes in turn. CSV parsing handles quoted fields and both
`1.234,56` and `1,234.56`.

Fallbacks: Coinbase for Bitcoin, frankfurter.app (ECB) for EUR→IDR. Both keyless.

The sheet URL is mirrored into its own `localStorage` key, `challenges_feed`, and restored
from there whenever the main blob comes back without it. The field saves on every keystroke
(`oninput`), not on blur — the previous `onchange` handler could lose a pasted URL when a
re-render replaced the input before the change event fired, which is the most likely cause
of the feed silently unlinking itself. The parent view also has a "Test the link" button.

**Open question:** whether Google's CSV endpoints send CORS headers for browser fetches
has not been confirmed on the actual device. If the parent view's status log shows
`Sheet ✗`, the fallback plan is a Google Apps Script web app endpoint. Bitcoin and the
rupiah rate survive that case via Coinbase and frankfurter.app; the ETF and the nine
company prices do not, and would need the manual fields.

## Current payout structure

See `README.md` in the repo for the full tables. Summary: Juna 20 weeks from 7 Sept 2026,
max €305, reading ladder €2→€8 plus four books plus three handstand milestones. Artus
10 weeks, max €35.50, reading aloud 10 min/day plus a 15-minute bonus tier plus five
early readers. No physical challenge for Artus in this cycle.

Design constraint agreed earlier: annual challenge payouts should stay within roughly
2–3× the annual pocket money for that child. The €100 handstand prize is a deliberate
one-time launch anchor, not a template for future cycles.

- **The app stores state, not events — except for the audit log.** Reading days are a
  date→minutes map, so the state alone cannot show who changed what or when. The log
  (added Sept 2026) is the only history that exists. Every mutation must append to it; a
  new action that moves money and does not call `logEvent` is a hole in the review.
- **The review boundary is a sequence number, not a timestamp.** The family moves between
  UTC+8 and UTC+1/+2, and ISO timestamps are UTC while the day headings are local. Derive
  the day an action happened with `logDayOf(e)`, never by slicing `e.t`.

## Home screen icon

`apple-touch-icon.png`, 180x180, opaque RGB, full bleed. iOS composites transparency onto
black and applies its own squircle mask, so the source must have no alpha and no rounded
corners of its own. PNG only; SVG and data URIs do not work for a web clip.

Four designs live in `tools/make-icons.py`: `spines-ink` (shipped), `book-ink`,
`book-juna`, `spines-paper`. To switch: `python3 tools/make-icons.py book-ink` and push the
three PNGs. Nothing in `index.html` changes.

**iOS caches the web clip icon at the moment the shortcut is created.** Changing the icon
does nothing to a shortcut that already exists. The shortcut has to be deleted from the
home screen and re-added, after a hard reload in Safari.

## Things deliberately not built

- No backend, no accounts, no sync. Data is `localStorage` on one device, with JSON
  export/import in the parent view. The weekly cash payout is the real backup.
- No live rate fetch for EUR→IDR on load; the sheet or a manual field covers it.
- No parent-side analytics dashboard beyond the review log.
- No tamper-proofing. The log is a record on a device the child holds, not a lock. Signing
  entries or shipping them off-device would need a backend, which is out of scope.
