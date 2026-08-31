# Project: Taschengeld & Challenges

Working brief for any new chat. Read this first, then fetch the live repo before changing
anything — this file describes intent and workflow, the repo is the source of truth.

## What this is

A single-file web app that tracks two children's reading challenges, pocket money,
spending, and a virtual savings portfolio. Used by the kids on an iPad from the home
screen; the parent view is PIN-gated.

- Repo: `Ikarus-eth/Taschengeld`, branch `main`, root folder
- Live: https://ikarus-eth.github.io/Taschengeld/
- Files: `index.html` (the entire app), `README.md` (spec), `PROJECT.md` (this file)

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
`status: built` (~40 s), then diff `raw.githubusercontent.com/.../main/index.html`
against the local build. Note that `ikarus-eth.github.io` is **not** on the sandbox
network allowlist, so fetching the live site directly returns a 403 from the proxy —
that is not a site failure. Use `raw.githubusercontent.com`, which is allowlisted.

## Working agreement

- **Test before pushing.** Extract the `<script>` block, `node --check` it, then stub the
  DOM and run the earnings and savings engines against full-completion and edge scenarios.
  Prior chats caught real bugs this way. Do not push untested changes.
- **No build step, no dependencies, no service worker.** `index.html` is self-contained.
  A service worker in an earlier project (blitzword) caused a cache bug that cost hours.
- **No network calls on page load.** Price fetching is a manual button in the parent view
  only, so a dead API never blocks a child from logging a reading day.
- Child-facing copy is German. Code and comments in English.
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
- **Pocket money is unconditional** and strictly separate from challenge payouts. It is
  never tied to grades, chores, or behaviour, and is never clawed back.
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

**Open question:** whether Google's CSV endpoints send CORS headers for browser fetches
has not been confirmed on the actual device. If the parent view's status log shows
`Tabelle ✗`, the fallback plan is a Google Apps Script web app endpoint.

## Current payout structure

See `README.md` in the repo for the full tables. Summary: Juna 20 weeks from 7 Sept 2026,
max €305, reading ladder €2→€8 plus four books plus three handstand milestones. Artus
10 weeks, max €35.50, reading aloud 10 min/day plus a 15-minute bonus tier plus five
Erstlesebücher. No physical challenge for Artus in this cycle.

Design constraint agreed earlier: annual challenge payouts should stay within roughly
2–3× the annual pocket money for that child. The €100 handstand prize is a deliberate
one-time launch anchor, not a template for future cycles.

## Things deliberately not built

- No backend, no accounts, no sync. Data is `localStorage` on one device, with JSON
  export/import in the parent view. The weekly cash payout is the real backup.
- No live rate fetch for EUR→IDR on load; the sheet or a manual field covers it.
- No parent-side analytics dashboard.
